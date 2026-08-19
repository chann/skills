"""Every packaged skill must satisfy the skill contract.

The contract is stated in
`skill-forge/skills/skill-forge/references/skill-package-contract.md` and
enforced by `skill-forge/skills/skill-audit/scripts/audit_skills.py`. This test
runs the auditor over this repository so a half-published skill fails the suite
instead of shipping.
"""

import json
import subprocess
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
AUDITOR = (
    ROOT / "skill-forge" / "skills" / "skill-audit" / "scripts" / "audit_skills.py"
)
CONTRACT = (
    ROOT
    / "skill-forge"
    / "skills"
    / "skill-forge"
    / "references"
    / "skill-package-contract.md"
)


def audit(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(AUDITOR), "--root", str(ROOT), *args],
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        check=False,
    )


class SkillContractTests(unittest.TestCase):
    def test_repository_satisfies_every_contract_rule(self) -> None:
        result = audit()
        self.assertEqual(0, result.returncode, result.stdout)
        self.assertIn("Contract satisfied", result.stdout)

    def test_every_packaged_skill_was_audited(self) -> None:
        payload = json.loads(audit("--format", "json").stdout)
        self.assertEqual(
            len(list(ROOT.glob("*/skills/*/SKILL.md"))), payload["packaged_skills"]
        )
        self.assertEqual([], payload["violations"])

    def test_every_skill_ships_evals(self) -> None:
        for skill_md in sorted(ROOT.glob("*/skills/*/SKILL.md")):
            name = skill_md.parent.name
            evals = skill_md.parent / "evals" / "evals.json"
            with self.subTest(skill=name):
                self.assertTrue(evals.is_file(), f"{name} ships no evals")
                payload = json.loads(evals.read_text(encoding="utf-8"))
                self.assertEqual(name, payload["skill_name"])
                self.assertGreaterEqual(len(payload["evals"]), 3)
                for item in payload["evals"]:
                    self.assertGreaterEqual(len(item["assertions"]), 2)

    def test_invocation_mode_matches_the_opening_clause(self) -> None:
        for skill_md in sorted(ROOT.glob("*/skills/*/SKILL.md")):
            frontmatter = skill_md.read_text(encoding="utf-8").split("---\n", 2)[1]
            selector_only = "description: Use only when" in frontmatter
            declared = "disable-model-invocation: true" in frontmatter
            with self.subTest(skill=skill_md.parent.name):
                self.assertEqual(selector_only, declared)

    def test_contract_document_and_auditor_cover_the_same_rules(self) -> None:
        document = CONTRACT.read_text(encoding="utf-8")
        auditor = AUDITOR.read_text(encoding="utf-8")
        for index in range(1, 10):
            rule = f"C{index}"
            with self.subTest(rule=rule):
                self.assertIn(f"## {rule}", document)
                self.assertIn(f'"{rule}"', auditor)


if __name__ == "__main__":
    unittest.main()
