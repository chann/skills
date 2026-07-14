import re
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]

INSTALL_DOCS = [
    ROOT / "USAGE.md",
    ROOT / "code-review" / "README.md",
    ROOT / "code-review" / "README.ko.md",
    ROOT / "doc-skill" / "README.md",
    ROOT / "doc-skill" / "README.ko.md",
    ROOT / "doc-skill" / "USAGE.md",
    ROOT / "git-skill" / "README.md",
    ROOT / "git-skill" / "README.ko.md",
    ROOT / "handoff" / "README.md",
    ROOT / "handoff" / "README.ko.md",
    ROOT / "long-task" / "README.md",
    ROOT / "long-task" / "README.ko.md",
]

CODE_REVIEW_READMES = [
    ROOT / "code-review" / "README.md",
    ROOT / "code-review" / "README.ko.md",
]

ROOT_DIFF_SUMMARY_DOCS = [
    ROOT / "README.md",
    ROOT / "README.ko.md",
    ROOT / "USAGE.md",
    ROOT / "ARCHITECTURE.md",
]


class InstallationDocsTests(unittest.TestCase):
    def test_npx_install_examples_use_skill_option_not_at_selector(self) -> None:
        invalid_selector = re.compile(r"npx skills add[^\n`]*chann/skills@")

        for path in INSTALL_DOCS:
            with self.subTest(doc=path.relative_to(ROOT)):
                self.assertIsNone(invalid_selector.search(path.read_text(encoding="utf-8")))

    def test_code_review_readmes_install_every_packaged_skill_by_exact_selector(self) -> None:
        skills_root = ROOT / "code-review" / "skills"
        expected_selectors = tuple(
            sorted(path.name for path in skills_root.iterdir() if (path / "SKILL.md").is_file())
        )
        self.assertIn("diff-summary", expected_selectors)

        for path in CODE_REVIEW_READMES:
            text = path.read_text(encoding="utf-8")
            with self.subTest(doc=path.relative_to(ROOT)):
                for selector in expected_selectors:
                    self.assertGreaterEqual(
                        text.count(f"--skill {selector}"),
                        2,
                        f"{path.relative_to(ROOT)} must include {selector} in global and local installs",
                    )

    def test_root_docs_publish_diff_summary_command_and_generated_path(self) -> None:
        for path in ROOT_DIFF_SUMMARY_DOCS:
            text = path.read_text(encoding="utf-8")
            with self.subTest(doc=path.relative_to(ROOT)):
                self.assertIn("/diff-summary", text)
                self.assertIn(".diff-summaries/", text)

    def test_diff_summary_architecture_and_usage_document_the_collector_boundary(self) -> None:
        architecture = (ROOT / "ARCHITECTURE.md").read_text(encoding="utf-8")
        usage = (ROOT / "USAGE.md").read_text(encoding="utf-8")

        for text in (architecture, usage):
            self.assertIn("collect_diff_evidence.py", text)
            self.assertIn("generate_summary_report.py", text)
        self.assertIn("argv", architecture)
        self.assertIn("JSON", architecture)

    def test_code_review_readmes_show_natural_summary_prompts_and_scope_examples(self) -> None:
        english = CODE_REVIEW_READMES[0].read_text(encoding="utf-8")
        korean = CODE_REVIEW_READMES[1].read_text(encoding="utf-8")

        for phrase in ("summarize the code changes", "main..dev", "last commit", "PR"):
            with self.subTest(language="en", phrase=phrase):
                self.assertIn(phrase, english)
        for phrase in ("코드를 요약해줘", "main..dev", "마지막 커밋", "PR"):
            with self.subTest(language="ko", phrase=phrase):
                self.assertIn(phrase, korean)

    def test_code_review_readmes_document_evidence_first_conditional_reports(self) -> None:
        english = CODE_REVIEW_READMES[0].read_text(encoding="utf-8")
        korean = CODE_REVIEW_READMES[1].read_text(encoding="utf-8")

        for phrase in (
            "Evidence-first writing",
            "Conditional sections",
            "observation → consequence → correction",
            "Verified context that affects a decision; no code change required",
        ):
            with self.subTest(language="en", phrase=phrase):
                self.assertIn(phrase, english)

        for phrase in (
            "근거 우선 문체",
            "조건부 섹션",
            "관찰 → 영향 → 수정",
            "의사결정에 영향을 주지만 코드 변경은 필요하지 않은 확인된 맥락",
        ):
            with self.subTest(language="ko", phrase=phrase):
                self.assertIn(phrase, korean)

        self.assertNotIn("Each `/code-review*` report includes:", english)
        self.assertNotIn("각 `/code-review*` 리포트에는 다음이 포함됩니다:", korean)
        self.assertNotIn("Positive observation or contextual note", english)
        self.assertNotIn("긍정적 관찰 또는 참고 사항", korean)
