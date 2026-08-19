import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PACKAGE = ROOT / "bug-hunt"
SKILL = PACKAGE / "skills" / "bug-hunt"


class BugHuntSkillPackageTests(unittest.TestCase):
    def test_plugin_shape_is_complete(self) -> None:
        expected = (
            PACKAGE / ".claude-plugin" / "plugin.json",
            PACKAGE / "commands" / "bug-hunt.md",
            PACKAGE / "README.md",
            PACKAGE / "README.ko.md",
            SKILL / "SKILL.md",
            SKILL / "agents" / "openai.yaml",
            SKILL / "evals" / "evals.json",
            SKILL / "references" / "instrumentation-playbook.md",
        )

        for path in expected:
            with self.subTest(path=path.relative_to(ROOT)):
                self.assertTrue(path.is_file())

    def test_plugin_metadata_publishes_the_ledger_contract(self) -> None:
        metadata = json.loads(
            (PACKAGE / ".claude-plugin" / "plugin.json").read_text(encoding="utf-8")
        )

        self.assertEqual("bug-hunt", metadata["name"])
        self.assertEqual("0.1.0", metadata["version"])
        self.assertIn("hypothesis ledger", metadata["description"])

    def test_interfaces_publish_both_selectors(self) -> None:
        frontmatter = (SKILL / "SKILL.md").read_text(encoding="utf-8").split("---\n", 2)[1]
        openai = (SKILL / "agents" / "openai.yaml").read_text(encoding="utf-8")
        command = (PACKAGE / "commands" / "bug-hunt.md").read_text(encoding="utf-8")

        self.assertIn("name: bug-hunt", frontmatter)
        self.assertIn("/bug-hunt", frontmatter)
        self.assertIn("$bug-hunt", frontmatter)
        self.assertIn("$bug-hunt", openai)
        self.assertIn("Use the **bug-hunt** skill", command)
        self.assertIn("$ARGUMENTS", command)
        self.assertIn('argument-hint: "[symptom or failing command]"', command)

    def test_skill_orders_the_diagnosis_loop(self) -> None:
        text = (SKILL / "SKILL.md").read_text(encoding="utf-8")
        ordered = [
            "## 1. State the defect as an observation",
            "## 2. Reproduce before touching product code",
            "## 3. Work the hypothesis ledger",
            "## 4. Pin the fix with a failing check",
            "## 5. Clean up the instrumentation",
            "## 6. Close the record",
            "## Refusals",
        ]

        positions = [text.find(heading) for heading in ordered]
        for heading, position in zip(ordered, positions):
            with self.subTest(heading=heading):
                self.assertNotEqual(-1, position)
        self.assertEqual(sorted(positions), positions)

    def test_skill_states_the_gates_that_make_the_record_useful(self) -> None:
        # Normalized so a line wrap in the prose cannot break the assertion.
        text = " ".join((SKILL / "SKILL.md").read_text(encoding="utf-8").split())
        for contract in (
            ".bug-hunts/<YYYY-MM-DD>-<slug>.md",
            "Falsified if",
            "### The widening rule",
            "fails **for the defect's reason**",
            "BUGHUNT",
            "Do not fix a defect you never reproduced",
            "Do not delete or rewrite a falsified hypothesis",
        ):
            with self.subTest(contract=contract):
                self.assertIn(contract, text)

    def test_widening_rule_bounds_hypotheses_per_layer(self) -> None:
        text = " ".join((SKILL / "SKILL.md").read_text(encoding="utf-8").split())
        self.assertIn("After **three** falsified hypotheses inside the same layer", text)
        self.assertIn(
            "Do not generate a fourth hypothesis in a layer that produced three falsified",
            text,
        )

    def test_playbook_covers_probes_bisection_and_removal(self) -> None:
        text = (SKILL / "references" / "instrumentation-playbook.md").read_text(
            encoding="utf-8"
        )
        for section in (
            "## Pick the cheapest probe that answers the question",
            "## Probe at the boundary, not in the middle",
            "## Per-ecosystem probes",
            "## Intermittent failures",
            "## Bisection",
            "## Performance hypotheses",
            "## Removal",
        ):
            with self.subTest(section=section):
                self.assertIn(section, text)
        self.assertIn('grep -rn "BUGHUNT"', text)

    def test_artifact_directory_is_ignored(self) -> None:
        self.assertIn(".bug-hunts/", (ROOT / ".gitignore").read_text(encoding="utf-8"))

    def test_catalog_and_every_locale_publish_the_skill(self) -> None:
        sources = [
            ROOT / "website" / "src" / "data" / "skills.ts",
            *(
                ROOT / "website" / "src" / "i18n" / "content" / f"{locale}.json"
                for locale in ("ko", "en", "jp", "cn")
            ),
        ]

        for path in sources:
            with self.subTest(path=path.relative_to(ROOT)):
                self.assertIn('"bug-hunt"', path.read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
