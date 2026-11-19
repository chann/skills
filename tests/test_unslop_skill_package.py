import json
import re
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PACKAGE = ROOT / "unslop"
SKILL = PACKAGE / "skills" / "unslop"


class UnslopSkillPackageTests(unittest.TestCase):
    def test_plugin_shape_is_complete(self) -> None:
        expected = [
            PACKAGE / ".claude-plugin" / "plugin.json",
            PACKAGE / "commands" / "unslop.md",
            SKILL / "SKILL.md",
            SKILL / "agents" / "openai.yaml",
            SKILL / "evals" / "evals.json",
            SKILL / "references" / "slop-lexicon.md",
            SKILL / "references" / "style-rules.md",
            SKILL / "references" / "english-rules.md",
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
        command = (PACKAGE / "commands" / "unslop.md").read_text(
            encoding="utf-8"
        )
        openai = (SKILL / "agents" / "openai.yaml").read_text(encoding="utf-8")

        self.assertEqual("unslop", metadata["name"])
        self.assertEqual("1.0.0", metadata["version"])
        self.assertIn("korean", metadata["description"].lower())
        self.assertIn("english", metadata["description"].lower())
        self.assertIn('argument-hint: "[text-or-file]"', command)
        self.assertIn("Use the **unslop** skill", command)
        self.assertIn("$ARGUMENTS", command)
        self.assertIn("$unslop", openai)

    def test_skill_preserves_meaning_and_standard_terms(self) -> None:
        text = (SKILL / "SKILL.md").read_text(encoding="utf-8")
        frontmatter = text.split("---\n", 2)[1]

        self.assertIn("name: unslop", frontmatter)
        self.assertIn("/unslop", frontmatter)
        self.assertIn("$unslop", frontmatter)

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

    def test_description_carries_korean_and_english_triggers(self) -> None:
        text = (SKILL / "SKILL.md").read_text(encoding="utf-8")
        description = text.split("---\n", 2)[1].split("description: ", 1)[1].strip()

        self.assertTrue(description.startswith("Use when"))
        self.assertLessEqual(len(description), 1024)
        for trigger in (
            "AI 용어 없애줘",
            "사람답게 다듬어줘",
            "AI 슬롭 제거",
            "자연스러운 한국어로 윤문해줘",
            "unslop this",
            "make this sound human",
            "remove the AI tells",
            "/unslop",
            "$unslop",
            "Not a spell-checker, not a translator, never changes content",
        ):
            with self.subTest(trigger=trigger):
                self.assertIn(trigger, description)

    def test_skill_detects_language_per_passage_and_never_translates(self) -> None:
        text = (SKILL / "SKILL.md").read_text(encoding="utf-8")

        for contract in (
            "Detect the language of each passage",
            "references/english-rules.md",
            "Never translate",
            "Mixed",
            "rule ids",
            "**Reply:**",
        ):
            with self.subTest(contract=contract):
                self.assertIn(contract, text)

    def test_english_rules_are_numbered_and_cover_the_required_tells(self) -> None:
        rules = (SKILL / "references" / "english-rules.md").read_text(
            encoding="utf-8"
        )
        ids = re.findall(r"(?m)^\*\*E(\d+)\.", rules)

        self.assertEqual([str(n) for n in range(1, len(ids) + 1)], ids)
        self.assertGreaterEqual(len(ids), 21)
        lowered = rules.lower()
        for topic in (
            "filler openers",
            "chatbot",
            "praise or agreement openers",
            "vague attributions",
            "inflated vocabulary",
            '"serves as"',
            "not just x but y",
            "forced lists of three",
            "one name per thing",
            "dashes as connectors",
            "colons as mid-sentence connectors",
            "bold on every noun",
            "bold labels that restate",
            "sentence-case headings",
            "decorative emoji",
            "stacked hedges",
            "generic conclusions",
            "abstract metaphor nouns",
            "one idea per sentence",
            "active voice with a named actor",
            "adverbs in place of numbers",
            "plain words",
            "utilize",
            "keep list",
        ):
            with self.subTest(topic=topic):
                self.assertIn(topic, lowered)

    def test_evals_cover_english_mixed_and_out_of_scope(self) -> None:
        payload = json.loads(
            (SKILL / "evals" / "evals.json").read_text(encoding="utf-8")
        )

        self.assertEqual("unslop", payload["skill_name"])
        self.assertGreaterEqual(len(payload["evals"]), 3)
        for item in payload["evals"]:
            with self.subTest(eval=item["id"]):
                self.assertGreaterEqual(len(item["assertions"]), 2)
        prompts = " ".join(item["prompt"] for item in payload["evals"])
        self.assertIn("English", prompts)
        self.assertIn("translate", prompts)

    def test_readmes_document_installation_and_boundaries(self) -> None:
        for path in (PACKAGE / "README.md", PACKAGE / "README.ko.md"):
            with self.subTest(path=path.relative_to(ROOT)):
                text = path.read_text(encoding="utf-8")
                self.assertEqual(
                    2, text.count("chann/skills --skill unslop")
                )
                self.assertIn("/unslop", text)
                self.assertIn("$unslop", text)


if __name__ == "__main__":
    unittest.main()
