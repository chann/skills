import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PACKAGE = ROOT / "all-subagents"
SKILL = PACKAGE / "skills" / "all-subagents"


class AllSubagentsSkillPackageTests(unittest.TestCase):
    def test_plugin_shape_is_complete(self) -> None:
        expected = (
            PACKAGE / ".claude-plugin" / "plugin.json",
            PACKAGE / "commands" / "all-subagents.md",
            PACKAGE / "README.md",
            PACKAGE / "README.ko.md",
            SKILL / "SKILL.md",
            SKILL / "agents" / "openai.yaml",
            SKILL / "evals" / "evals.json",
            SKILL / "scripts" / "all_subagents.py",
            SKILL / "assets" / "prompts" / "common.md",
            SKILL / "references" / "routes.md",
            SKILL / "references" / "selection.md",
            SKILL / "references" / "execution.md",
        )
        for path in expected:
            with self.subTest(path=path.relative_to(ROOT)):
                self.assertTrue(path.is_file(), path)

    def test_plugin_metadata_names_the_run_record(self) -> None:
        metadata = json.loads(
            (PACKAGE / ".claude-plugin" / "plugin.json").read_text(encoding="utf-8")
        )
        self.assertEqual("all-subagents", metadata["name"])
        self.assertEqual("0.1.0", metadata["version"])
        self.assertIn("call-tree", metadata["description"])

    def test_interfaces_publish_both_selectors(self) -> None:
        frontmatter = (SKILL / "SKILL.md").read_text(encoding="utf-8").split("---\n", 2)[1]
        openai = (SKILL / "agents" / "openai.yaml").read_text(encoding="utf-8")
        command = (PACKAGE / "commands" / "all-subagents.md").read_text(encoding="utf-8")
        self.assertIn("name: all-subagents", frontmatter)
        self.assertIn("/all-subagents", frontmatter)
        self.assertIn("$all-subagents", frontmatter)
        self.assertIn("$all-subagents", openai)
        self.assertIn("Use the **all-subagents** skill", command)
        self.assertIn("$ARGUMENTS", command)
        description = frontmatter.split("description: ", 1)[1].strip()
        self.assertLessEqual(len(description), 1024)
        self.assertIn("서브에이전트로 작업해줘", description)
        self.assertIn("use subagents", description)
        self.assertIn("spawn subagents", description)

    def test_skill_orders_the_delegation_gates(self) -> None:
        text = (SKILL / "SKILL.md").read_text(encoding="utf-8")
        ordered = [
            "## 1. Decide this skill applies",
            "## 2. Probe before choosing",
            "## 3. Select the route and record the plan",
            "## 4. Write the prompt to a file, then run",
            "## 5. Read the result before trusting it",
            "## 6. Report the call tree",
            "## Refusals",
        ]
        positions = [text.find(heading) for heading in ordered]
        for heading, position in zip(ordered, positions, strict=True):
            with self.subTest(heading=heading):
                self.assertNotEqual(-1, position, heading)
        self.assertEqual(sorted(positions), positions)

    def test_skill_keeps_neighbours_and_stops_polling(self) -> None:
        text = (SKILL / "SKILL.md").read_text(encoding="utf-8")
        for phrase in (
            "heterogeneous: false",
            "long-task",
            "research-brief",
            "code-review",
            "Do not poll",
            "error_class: permission",
            "error_class: mutated",
            "write_set_ok: false",
            "--context-file",
        ):
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, text)

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
                text = path.read_text(encoding="utf-8")
                self.assertIn('"all-subagents"', text)
        triggers = {
            "ko": "서브에이전트",
            "en": "subagents",
            "jp": "サブエージェント",
            "cn": "子代理",
        }
        for locale, trigger in triggers.items():
            path = ROOT / "website" / "src" / "i18n" / "content" / f"{locale}.json"
            with self.subTest(locale=locale):
                self.assertIn(trigger, path.read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
