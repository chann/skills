import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PACKAGE = ROOT / "human-friendly-writing"
SKILL = PACKAGE / "skills" / "human-friendly-writing"


class HumanFriendlyWritingSkillPackageTests(unittest.TestCase):
    def test_plugin_shape_is_complete(self) -> None:
        expected = [
            PACKAGE / ".claude-plugin" / "plugin.json",
            PACKAGE / "commands" / "human-friendly-writing.md",
            SKILL / "SKILL.md",
            SKILL / "agents" / "openai.yaml",
            SKILL / "references" / "slop-lexicon.md",
            SKILL / "references" / "style-rules.md",
            PACKAGE / "README.md",
            PACKAGE / "README.ko.md",
        ]

        for path in expected:
            with self.subTest(path=path.relative_to(ROOT)):
                self.assertTrue(path.is_file())

    def test_plugin_metadata_and_interfaces_publish_the_selector(self) -> None:
        metadata = json.loads(
            (PACKAGE / ".claude-plugin" / "plugin.json").read_text(
                encoding="utf-8"
            )
        )
        command = (PACKAGE / "commands" / "human-friendly-writing.md").read_text(
            encoding="utf-8"
        )
        openai = (SKILL / "agents" / "openai.yaml").read_text(encoding="utf-8")

        self.assertEqual("human-friendly-writing", metadata["name"])
        self.assertEqual("0.1.0", metadata["version"])
        self.assertIn("korean", metadata["description"].lower())
        self.assertIn('argument-hint: "[text-or-file]"', command)
        self.assertIn("Use the **human-friendly-writing** skill", command)
        self.assertIn("$ARGUMENTS", command)
        self.assertIn("$human-friendly-writing", openai)

    def test_skill_preserves_meaning_and_standard_terms(self) -> None:
        text = (SKILL / "SKILL.md").read_text(encoding="utf-8")
        frontmatter = text.split("---\n", 2)[1]

        self.assertIn("name: human-friendly-writing", frontmatter)
        self.assertIn("/human-friendly-writing", frontmatter)
        self.assertIn("$human-friendly-writing", frontmatter)

        for contract in (
            "Never add, remove, or reorder facts",
            "keep list",
            "keep the term",
            "already sounds natural stays",
            "Never overwrite a source file",
            "references/slop-lexicon.md",
            "references/style-rules.md",
        ):
            with self.subTest(contract=contract):
                self.assertIn(contract, text)

    def test_skill_defines_the_three_part_test_and_no_method_jargon(self) -> None:
        text = (SKILL / "SKILL.md").read_text(encoding="utf-8")

        for contract in (
            "three-part test",
            "literal translation or one-off transliteration",
            "would not say it",
            "natural everyday replacement",
            "Any doubt",
            "Never leak method vocabulary",
            "모든 렌즈 감사가 끝났고",
            "own replies",
        ):
            with self.subTest(contract=contract):
                self.assertIn(contract, text)

    def test_lexicon_covers_seed_terms_method_jargon_and_keep_list(self) -> None:
        lexicon = (SKILL / "references" / "slop-lexicon.md").read_text(
            encoding="utf-8"
        )

        for term in ("계약", "엔벨로프", "패리티", "직교", "레버리지"):
            with self.subTest(term=term):
                self.assertIn(term, lexicon)

        for jargon in ("렌즈", "노드", "마감 기록", "프런티어"):
            with self.subTest(jargon=jargon):
                self.assertIn(jargon, lexicon)

        self.assertIn("## 4. 보존 목록", lexicon)
        for keep in ("API", "토큰", "프롬프트", "멱등", "커밋"):
            with self.subTest(keep=keep):
                self.assertIn(keep, lexicon)

    def test_style_rules_include_translationese_rhythm_and_checklist(self) -> None:
        rules = (SKILL / "references" / "style-rules.md").read_text(
            encoding="utf-8"
        )

        for fragment in (
            "번역투",
            "리듬",
            "과윤문 방지",
            "자기검증",
            "수치·날짜·고유명사",
            "보존 목록",
        ):
            with self.subTest(fragment=fragment):
                self.assertIn(fragment, rules)

    def test_readmes_document_installation_and_boundaries(self) -> None:
        for path in (PACKAGE / "README.md", PACKAGE / "README.ko.md"):
            with self.subTest(path=path.relative_to(ROOT)):
                text = path.read_text(encoding="utf-8")
                self.assertEqual(
                    2, text.count("chann/skills --skill human-friendly-writing")
                )
                self.assertIn("/human-friendly-writing", text)
                self.assertIn("$human-friendly-writing", text)


if __name__ == "__main__":
    unittest.main()
