import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PACKAGE = ROOT / "research-brief"
SKILL = PACKAGE / "skills" / "research-brief"


def normalized(path: Path) -> str:
    return " ".join(path.read_text(encoding="utf-8").split())


class ResearchBriefSkillPackageTests(unittest.TestCase):
    def test_plugin_shape_is_complete(self) -> None:
        expected = (
            PACKAGE / ".claude-plugin" / "plugin.json",
            PACKAGE / "commands" / "research-brief.md",
            PACKAGE / "README.md",
            PACKAGE / "README.ko.md",
            SKILL / "SKILL.md",
            SKILL / "agents" / "openai.yaml",
            SKILL / "evals" / "evals.json",
        )

        for path in expected:
            with self.subTest(path=path.relative_to(ROOT)):
                self.assertTrue(path.is_file())

    def test_plugin_metadata_publishes_the_citation_contract(self) -> None:
        metadata = json.loads(
            (PACKAGE / ".claude-plugin" / "plugin.json").read_text(encoding="utf-8")
        )

        self.assertEqual("research-brief", metadata["name"])
        self.assertEqual("0.1.0", metadata["version"])
        self.assertIn("primary sources", metadata["description"])

    def test_interfaces_publish_both_selectors(self) -> None:
        frontmatter = (SKILL / "SKILL.md").read_text(encoding="utf-8").split("---\n", 2)[1]
        openai = (SKILL / "agents" / "openai.yaml").read_text(encoding="utf-8")
        command = (PACKAGE / "commands" / "research-brief.md").read_text(encoding="utf-8")

        self.assertIn("name: research-brief", frontmatter)
        self.assertIn("/research-brief", frontmatter)
        self.assertIn("$research-brief", frontmatter)
        self.assertIn("$research-brief", openai)
        self.assertIn("Use the **research-brief** skill", command)
        self.assertIn("$ARGUMENTS", command)
        self.assertIn('argument-hint: "[question]"', command)

    def test_skill_orders_the_research_workflow(self) -> None:
        text = (SKILL / "SKILL.md").read_text(encoding="utf-8")
        ordered = [
            "## 1. Sharpen the question",
            "## 2. Delegate the reading when you can",
            "## 3. Read the source that owns the answer",
            "## 4. Pin every claim to a version",
            "## 5. Record contradictions instead of resolving them silently",
            "## 6. Write the brief",
            "## Refusals",
        ]

        positions = [text.find(heading) for heading in ordered]
        for heading, position in zip(ordered, positions):
            with self.subTest(heading=heading):
                self.assertNotEqual(-1, position)
        self.assertEqual(sorted(positions), positions)

    def test_skill_defines_three_source_tiers(self) -> None:
        text = normalized(SKILL / "SKILL.md")
        for tier in ("**T1**", "**T2**", "**T3**"):
            with self.subTest(tier=tier):
                self.assertIn(tier, text)
        self.assertIn("Only as **unverified**, never as fact", text)
        self.assertIn("A T3 claim is a lead, not an answer", text)

    def test_skill_requires_version_pinning_and_open_questions(self) -> None:
        text = normalized(SKILL / "SKILL.md")
        for contract in (
            ".research/<YYYY-MM-DD>-<slug>.md",
            "## Bottom line",
            "## Contradictions",
            "## Open questions",
            "**Open questions is mandatory.**",
            "records the **version** — `4.2.1`, not \"latest\"",
            "Do not write a claim without the version or date",
            "Do not resolve a contradiction by deleting one side",
            "Do not cite a search snippet as a source",
        ):
            with self.subTest(contract=contract):
                self.assertIn(contract, text)

    def test_skill_routes_held_documents_to_plan_summary(self) -> None:
        text = normalized(SKILL / "SKILL.md")
        self.assertIn("route it to `plan-summary`", text)
        self.assertIn("Research is for material that is not yet in hand", text)

    def test_artifact_directory_is_ignored(self) -> None:
        self.assertIn(".research/", (ROOT / ".gitignore").read_text(encoding="utf-8"))

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
                self.assertIn('"research-brief"', path.read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
