import json
import re
import subprocess
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PACKAGE = ROOT / "skill-forge"
FORGE = PACKAGE / "skills" / "skill-forge"
AUDIT = PACKAGE / "skills" / "skill-audit"
AUDITOR = AUDIT / "scripts" / "audit_skills.py"


def run_auditor(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(AUDITOR), *args],
        cwd=ROOT,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        check=False,
    )


class SkillForgePackageTests(unittest.TestCase):
    def test_plugin_shape_is_complete(self) -> None:
        expected = (
            PACKAGE / ".claude-plugin" / "plugin.json",
            PACKAGE / "commands" / "skill-forge.md",
            PACKAGE / "commands" / "skill-audit.md",
            PACKAGE / "README.md",
            PACKAGE / "README.ko.md",
            FORGE / "SKILL.md",
            FORGE / "agents" / "openai.yaml",
            FORGE / "evals" / "evals.json",
            FORGE / "references" / "skill-package-contract.md",
            FORGE / "references" / "description-grammar.md",
            AUDIT / "SKILL.md",
            AUDIT / "agents" / "openai.yaml",
            AUDIT / "evals" / "evals.json",
            AUDITOR,
        )

        for path in expected:
            with self.subTest(path=path.relative_to(ROOT)):
                self.assertTrue(path.is_file())

    def test_plugin_metadata_publishes_both_skills(self) -> None:
        metadata = json.loads(
            (PACKAGE / ".claude-plugin" / "plugin.json").read_text(encoding="utf-8")
        )

        self.assertEqual("skill-forge", metadata["name"])
        self.assertEqual("0.1.0", metadata["version"])
        self.assertIn("contract", metadata["description"])

    def test_interfaces_publish_both_explicit_selectors(self) -> None:
        for skill, name in ((FORGE, "skill-forge"), (AUDIT, "skill-audit")):
            with self.subTest(skill=name):
                frontmatter = (skill / "SKILL.md").read_text(encoding="utf-8").split(
                    "---\n", 2
                )[1]
                openai = (skill / "agents" / "openai.yaml").read_text(encoding="utf-8")
                command = (PACKAGE / "commands" / f"{name}.md").read_text(
                    encoding="utf-8"
                )

                self.assertIn(f"name: {name}", frontmatter)
                self.assertIn(f"/{name}", frontmatter)
                self.assertIn(f"${name}", frontmatter)
                self.assertIn(f"${name}", openai)
                self.assertIn(f"**{name}**", command)
                self.assertIn("$ARGUMENTS", command)

    def test_contract_reference_states_every_rule(self) -> None:
        text = (FORGE / "references" / "skill-package-contract.md").read_text(
            encoding="utf-8"
        )
        for rule in [f"## C{index}" for index in range(1, 10)]:
            with self.subTest(rule=rule):
                self.assertIn(rule, text)

    def test_forge_publishes_every_website_surface(self) -> None:
        text = (FORGE / "SKILL.md").read_text(encoding="utf-8")
        for surface in (
            "website/src/data/skills.ts",
            "website/src/i18n/content/{ko,en,jp,cn}.json",
            "website/scripts/verify-catalog.mjs",
            "website/scripts/generate-social-cards.mjs",
        ):
            with self.subTest(surface=surface):
                self.assertIn(surface, text)

    def test_audit_skill_refuses_to_weaken_the_contract(self) -> None:
        text = (AUDIT / "SKILL.md").read_text(encoding="utf-8")
        self.assertIn("## Refusals", text)
        self.assertIn("Do not edit files during an audit", text)
        self.assertIn("MIN_EVALS", text)
        self.assertIn("Do not treat a skipped rule as a passed rule", text)

    def test_auditor_emits_machine_readable_output(self) -> None:
        result = run_auditor("--root", ".", "--format", "json")
        payload = json.loads(result.stdout)

        self.assertEqual(
            len(list(ROOT.glob("*/skills/*/SKILL.md"))), payload["packaged_skills"]
        )
        self.assertIsInstance(payload["violations"], list)
        self.assertEqual(
            payload["catalog_workflows"],
            len(
                re.findall(
                    r'^\s*id: "([^"]+)",$',
                    (ROOT / "website" / "src" / "data" / "skills.ts").read_text(
                        encoding="utf-8"
                    ),
                    re.MULTILINE,
                )
            ),
        )

    def test_auditor_scopes_a_single_skill(self) -> None:
        result = run_auditor("--root", ".", "--skill", "skill-forge")
        self.assertEqual(0, result.returncode, result.stdout)
        self.assertIn("no violations", result.stdout)

    def test_auditor_detects_a_broken_package(self) -> None:
        import shutil
        import tempfile

        with tempfile.TemporaryDirectory() as workspace:
            fake = Path(workspace) / "demo"
            skill = fake / "skills" / "demo-skill"
            skill.mkdir(parents=True)
            (skill / "SKILL.md").write_text(
                "---\nname: demo-skill\ndescription: Summarizes things.\n---\n\nBody.\n",
                encoding="utf-8",
            )
            shutil.copy(AUDITOR, Path(workspace) / "audit_skills.py")

            result = subprocess.run(
                [sys.executable, str(Path(workspace) / "audit_skills.py"), "--root", workspace],
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                check=False,
            )

        self.assertEqual(1, result.returncode, result.stdout)
        for rule in ("C2", "C4", "C5", "C6", "C8"):
            with self.subTest(rule=rule):
                self.assertIn(rule, result.stdout)


if __name__ == "__main__":
    unittest.main()
