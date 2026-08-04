from __future__ import annotations

import hashlib
import importlib.util
import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SCRIPT = (
    ROOT
    / "plan-summary"
    / "skills"
    / "plan-summary"
    / "scripts"
    / "generate_plan_summary.py"
)


def load_renderer():
    spec = importlib.util.spec_from_file_location("generate_plan_summary", SCRIPT)
    if spec is None or spec.loader is None:
        raise AssertionError("generator module could not be loaded")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


renderer = load_renderer()


DIGEST_A = "a" * 64
DIGEST_B = "b" * 64

KO_REPORT = f"""# Plan Summary Report

**Date:** 2026-08-04
**Sources:** `docs/plan.md`, `docs/design.md`
**Source Digests:** `{DIGEST_A}`, `{DIGEST_B}`
**Language:** ko

## Executive Summary

첫 출시의 문서 요약 범위와 검증 기준을 정리합니다.

## Summary

### Goals and Scope

#### [PS-001] 첫 출시 범위 확정

**Category:** Scope
**Sources:** `docs/plan.md#release-scope`

**Summary:** 첫 출시에는 문서 요약과 퀴즈가 포함됩니다.

**Why it matters:** 설치 가능한 결과물의 경계를 고정합니다.

**Source basis:** `Release scope` 절의 필수 기능 목록.

### Decisions

#### [PS-002] 명시적 파일만 읽기

**Category:** Decision
**Sources:** `docs/plan.md#inputs`, `docs/design.md#security`

**Summary:** 사용자가 지정한 UTF-8 문서만 수집합니다.

**Why it matters:** 문서 밖으로 읽기 범위가 넓어지는 것을 막습니다.

**Source basis:** `Inputs`와 `Security` 절의 입력 경계.

## Plan Map

| Source | Section | Role | Key point |
| --- | --- | --- | --- |
| `docs/plan.md` | Release scope | Requirements | 첫 출시 범위 |
| `docs/design.md` | Security | Constraint | 명시적 입력 경계 |

## Risks, Contradictions, and Open Questions

- 명시되지 않은 문서 형식은 지원하지 않습니다.
"""

EN_REPORT = f"""# Plan Summary Report

**Date:** 2026-08-04
**Sources:** `docs/plan.md`, `docs/design.md`
**Source Digests:** `{DIGEST_A}`, `{DIGEST_B}`
**Language:** en

## Executive Summary

The first release defines the document-summary scope and verification criteria.

## Summary

### Goals and Scope

#### [PS-001] Fix the first-release boundary

**Category:** Scope
**Sources:** `docs/plan.md#release-scope`

**Summary:** The first release includes document summaries and quizzes.

**Why it matters:** This fixes the boundary of the installable deliverables.

**Source basis:** The required features under `Release scope`.

### Decisions

#### [PS-002] Read only explicit files

**Category:** Decision
**Sources:** `docs/plan.md#inputs`, `docs/design.md#security`

**Summary:** Collection is limited to user-selected UTF-8 documents.

**Why it matters:** This prevents the read scope from expanding beyond the documents.

**Source basis:** The input boundary in `Inputs` and `Security`.

## Plan Map

| Source | Section | Role | Key point |
| --- | --- | --- | --- |
| `docs/plan.md` | Release scope | Requirements | First-release scope |
| `docs/design.md` | Security | Constraint | Explicit input boundary |

## Risks, Contradictions, and Open Questions

- Unspecified document formats are unsupported.
"""

KO_QUIZ = """

## Quiz

#### [QZ-001] 첫 출시 범위에 포함되는 것은 무엇인가요?

- [ ] 원격 URL 자동 탐색
- [x] 문서 요약과 퀴즈
- [ ] 원본 문서 자동 수정

**Explanation:** PS-001은 문서 요약과 퀴즈를 첫 출시 범위로 명시합니다.

#### [QZ-002] 수집기가 읽을 수 있는 파일은 무엇인가요?

- [x] 사용자가 명시한 UTF-8 문서
- [ ] 저장소의 모든 파일

**Explanation:** PS-002는 명시적으로 선택한 UTF-8 문서만 허용합니다.
"""

EN_QUIZ = """

## Quiz

#### [QZ-001] What is included in the first-release scope?

- [ ] Automatic remote URL discovery
- [x] Document summaries and quizzes
- [ ] Automatic source-document editing

**Explanation:** PS-001 names document summaries and quizzes as first-release scope.

#### [QZ-002] Which files may the collector read?

- [x] User-selected UTF-8 documents
- [ ] Every file in the repository

**Explanation:** PS-002 permits only explicitly selected UTF-8 documents.
"""

KO_QUIZ_REPORT = KO_REPORT.rstrip() + KO_QUIZ
EN_QUIZ_REPORT = EN_REPORT.rstrip() + EN_QUIZ


def replace_once(markdown: str, old: str, new: str) -> str:
    if markdown.count(old) != 1:
        raise AssertionError(f"fixture fragment must occur exactly once: {old!r}")
    return markdown.replace(old, new, 1)


class PlanSummaryParserTests(unittest.TestCase):
    def test_parses_metadata_cards_and_source_references(self) -> None:
        report = renderer.parse_report(KO_REPORT)

        self.assertEqual(report.date, "2026-08-04")
        self.assertEqual(report.sources, ("docs/plan.md", "docs/design.md"))
        self.assertEqual(report.source_digests, (DIGEST_A, DIGEST_B))
        self.assertEqual(report.language, "ko")
        self.assertIn("첫 출시", report.executive_summary)
        self.assertEqual([card.id for card in report.cards], ["PS-001", "PS-002"])
        self.assertEqual(report.cards[0].category, "Scope")
        self.assertEqual(report.cards[0].sources, ("docs/plan.md#release-scope",))
        self.assertEqual(report.cards[1].category, "Decision")
        self.assertIn("**Source basis:**", report.cards[1].markdown)
        self.assertEqual(report.quiz, ())
        self.assertEqual(report.markdown, KO_REPORT)

    def test_rejects_missing_duplicate_or_malformed_metadata(self) -> None:
        cases = (
            (KO_REPORT.replace("**Date:** 2026-08-04\n", ""), "Date"),
            (
                KO_REPORT.replace(
                    "**Date:** 2026-08-04\n",
                    "**Date:** 2026-08-04\n**Date:** 2026-08-05\n",
                ),
                "Date.*exactly once",
            ),
            (replace_once(KO_REPORT, "2026-08-04", "2026-02-30"), "real calendar"),
            (replace_once(KO_REPORT, "**Language:** ko", "**Language:** kr"), "Language"),
            (
                replace_once(KO_REPORT, f"`{DIGEST_B}`", "`not-a-digest`"),
                "Source Digests",
            ),
            (
                replace_once(
                    KO_REPORT,
                    f"`{DIGEST_A}`, `{DIGEST_B}`",
                    f"`{DIGEST_A}`",
                ),
                "one digest per source",
            ),
        )
        for markdown, reason in cases:
            with self.subTest(reason=reason):
                with self.assertRaisesRegex(renderer.ReportFormatError, reason):
                    renderer.parse_report(markdown)

    def test_rejects_nonsequential_duplicate_or_malformed_ps_ids(self) -> None:
        cases = (
            (replace_once(KO_REPORT, "[PS-002]", "[PS-003]"), "sequential"),
            (replace_once(KO_REPORT, "[PS-002]", "[PS-001]"), "sequential"),
            (replace_once(KO_REPORT, "[PS-002]", "[PS-02]"), "malformed.*PS"),
        )
        for markdown, reason in cases:
            with self.subTest(reason=reason):
                with self.assertRaisesRegex(renderer.ReportFormatError, reason):
                    renderer.parse_report(markdown)

    def test_rejects_unknown_categories_and_empty_sources(self) -> None:
        cases = (
            (
                replace_once(KO_REPORT, "**Category:** Scope", "**Category:** Feature"),
                "Category.*Feature",
            ),
            (
                replace_once(
                    KO_REPORT,
                    "**Sources:** `docs/plan.md#release-scope`",
                    "**Sources:**",
                ),
                "PS-001.*Sources",
            ),
        )
        for markdown, reason in cases:
            with self.subTest(reason=reason):
                with self.assertRaisesRegex(renderer.ReportFormatError, reason):
                    renderer.parse_report(markdown)

    def test_requires_summary_why_it_matters_and_source_basis_once(self) -> None:
        cases = (
            (KO_REPORT.replace("**Summary:** 첫 출시에는 문서 요약과 퀴즈가 포함됩니다.\n", "", 1), "Summary"),
            (
                replace_once(
                    KO_REPORT,
                    "**Why it matters:** 설치 가능한 결과물의 경계를 고정합니다.",
                    "**Why it matters:** 하나\n\n**Why it matters:** 둘",
                ),
                "Why it matters.*exactly once",
            ),
            (
                replace_once(
                    KO_REPORT,
                    "**Source basis:** `Release scope` 절의 필수 기능 목록.",
                    "**Source basis:**",
                ),
                "Source basis",
            ),
        )
        for markdown, reason in cases:
            with self.subTest(reason=reason):
                with self.assertRaisesRegex(renderer.ReportFormatError, reason):
                    renderer.parse_report(markdown)

    def test_ignores_card_like_text_inside_fenced_code(self) -> None:
        fenced = """```markdown
#### [PS-999] 가짜 카드
**Category:** Feature
**Sources:**
```

"""
        report = replace_once(KO_REPORT, "## Summary\n\n", "## Summary\n\n" + fenced)

        parsed = renderer.parse_report(report)

        self.assertEqual([card.id for card in parsed.cards], ["PS-001", "PS-002"])

    def test_bilingual_reports_require_matching_metadata_ids_categories_and_sources(self) -> None:
        renderer.validate_bilingual_alignment(
            renderer.parse_report(KO_REPORT), renderer.parse_report(EN_REPORT)
        )
        cases = (
            (replace_once(EN_REPORT, "2026-08-04", "2026-08-05"), "Date"),
            (replace_once(EN_REPORT, "**Category:** Scope", "**Category:** Goal"), "categories"),
            (
                replace_once(
                    EN_REPORT,
                    "`docs/plan.md#release-scope`",
                    "`docs/design.md#release-scope`",
                ),
                "source references",
            ),
        )
        for alternate, reason in cases:
            with self.subTest(reason=reason):
                with self.assertRaisesRegex(renderer.ReportFormatError, reason):
                    renderer.validate_bilingual_alignment(
                        renderer.parse_report(KO_REPORT),
                        renderer.parse_report(alternate),
                    )

    def test_parses_quiz_questions_and_rejects_invalid_options_or_explanations(self) -> None:
        report = renderer.parse_report(KO_QUIZ_REPORT)

        self.assertEqual([question.id for question in report.quiz], ["QZ-001", "QZ-002"])
        self.assertEqual(report.quiz[0].correct_index, 1)
        self.assertEqual(len(report.quiz[0].options), 3)
        cases = (
            (replace_once(KO_QUIZ_REPORT, "- [x] 문서 요약과 퀴즈", "- [ ] 문서 요약과 퀴즈"), "exactly one"),
            (
                replace_once(
                    KO_QUIZ_REPORT,
                    "- [ ] 원본 문서 자동 수정",
                    "- [x] 원본 문서 자동 수정",
                ),
                "exactly one",
            ),
            (KO_QUIZ_REPORT.replace("**Explanation:** PS-001은 문서 요약과 퀴즈를 첫 출시 범위로 명시합니다.\n", "", 1), "Explanation"),
            (
                replace_once(
                    KO_QUIZ_REPORT,
                    "- [ ] 원격 URL 자동 탐색",
                    "- [ ] **문서 요약과 퀴즈**",
                ),
                "duplicate option",
            ),
        )
        for markdown, reason in cases:
            with self.subTest(reason=reason):
                with self.assertRaisesRegex(renderer.ReportFormatError, reason):
                    renderer.parse_report(markdown)

    def test_bilingual_quizzes_align_ids_option_counts_and_correct_indexes(self) -> None:
        renderer.validate_bilingual_alignment(
            renderer.parse_report(KO_QUIZ_REPORT),
            renderer.parse_report(EN_QUIZ_REPORT),
        )
        cases = (
            (replace_once(EN_QUIZ_REPORT, "[QZ-002]", "[QZ-003]"), "sequential"),
            (
                replace_once(
                    EN_QUIZ_REPORT,
                    "- [ ] Automatic source-document editing\n",
                    "",
                ),
                "option counts",
            ),
            (
                replace_once(
                    EN_QUIZ_REPORT,
                    "- [ ] Automatic remote URL discovery\n- [x] Document summaries and quizzes",
                    "- [x] Automatic remote URL discovery\n- [ ] Document summaries and quizzes",
                ),
                "correct-answer indexes",
            ),
        )
        for alternate, reason in cases:
            with self.subTest(reason=reason):
                with self.assertRaisesRegex(renderer.ReportFormatError, reason):
                    renderer.validate_bilingual_alignment(
                        renderer.parse_report(KO_QUIZ_REPORT),
                        renderer.parse_report(alternate),
                    )


class PlanSummaryOutputTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary_directory = tempfile.TemporaryDirectory()
        self.root = Path(self.temporary_directory.name)

    def tearDown(self) -> None:
        self.temporary_directory.cleanup()

    def test_bilingual_directory_mode_writes_korean_and_english_markdown_atomically(self) -> None:
        output = self.root / ".plan-summaries"

        korean, english, html = renderer.generate_bilingual_report_in_directory(
            KO_REPORT,
            EN_REPORT,
            output,
            markdown_only=True,
        )

        self.assertEqual(korean.read_text(encoding="utf-8"), KO_REPORT)
        self.assertEqual(english.read_text(encoding="utf-8"), EN_REPORT)
        self.assertIsNone(html)
        self.assertEqual(list(output.glob(".*.tmp")), [])
        self.assertTrue(korean.name.endswith(".md"))
        self.assertTrue(english.name.endswith(".en.md"))

    def test_source_order_changes_the_collision_safe_output_stem(self) -> None:
        original = renderer.parse_report(KO_REPORT)
        swapped = renderer.parse_report(
            KO_REPORT.replace(
                "**Sources:** `docs/plan.md`, `docs/design.md`",
                "**Sources:** `docs/design.md`, `docs/plan.md`",
            ).replace(
                f"**Source Digests:** `{DIGEST_A}`, `{DIGEST_B}`",
                f"**Source Digests:** `{DIGEST_B}`, `{DIGEST_A}`",
            )
        )

        self.assertRegex(renderer.source_tag(original), r"^plan-design-[0-9a-f]{12}$")
        self.assertRegex(renderer.source_tag(swapped), r"^design-plan-[0-9a-f]{12}$")
        self.assertNotEqual(renderer.source_tag(original), renderer.source_tag(swapped))

    def test_rejects_symlinked_output_parent_and_existing_output_symlink(self) -> None:
        real = self.root / "real"
        real.mkdir()
        alias = self.root / "alias"
        alias.symlink_to(real, target_is_directory=True)
        with self.assertRaisesRegex(renderer.ReportFormatError, "symbolic link"):
            renderer.generate_bilingual_report_in_directory(
                KO_REPORT, EN_REPORT, alias, markdown_only=True
            )

        output = self.root / ".plan-summaries"
        output.mkdir()
        stem = f"2026-08-04_{renderer.source_tag(renderer.parse_report(KO_REPORT))}"
        target = self.root / "target.md"
        target.write_text("keep", encoding="utf-8")
        (output / f"{stem}.md").symlink_to(target)
        with self.assertRaisesRegex(renderer.ReportFormatError, "already exists"):
            renderer.generate_bilingual_report_in_directory(
                KO_REPORT, EN_REPORT, output, markdown_only=True
            )
        self.assertEqual(target.read_text(encoding="utf-8"), "keep")

    def test_markdown_only_writes_no_html(self) -> None:
        output = self.root / "out"

        result = renderer.generate_bilingual_report_in_directory(
            KO_REPORT, EN_REPORT, output, markdown_only=True
        )

        self.assertIsNone(result[2])
        self.assertEqual(list(output.glob("*.html")), [])

    def test_single_language_mode_requires_an_explicit_report(self) -> None:
        output = self.root / "out"
        path = renderer.generate_single_report_in_directory(
            KO_REPORT, output, markdown_only=True
        )

        self.assertEqual(path[0].read_text(encoding="utf-8"), KO_REPORT)
        self.assertIsNone(path[1])
        process = subprocess.run(
            [
                sys.executable,
                "-I",
                str(SCRIPT),
                "--markdown-stdin",
                "--output-directory",
                str(self.root / "cli-out"),
                "--markdown-only",
            ],
            input="",
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=False,
        )
        self.assertEqual(process.returncode, 2)
        self.assertEqual(process.stdout, "")
        self.assertIn("non-empty", process.stderr)

    def test_cli_bilingual_json_mode_returns_written_paths(self) -> None:
        output = self.root / "cli"
        process = subprocess.run(
            [
                sys.executable,
                "-I",
                str(SCRIPT),
                "--bilingual-json-stdin",
                "--output-directory",
                str(output),
                "--markdown-only",
            ],
            input=json.dumps({"ko": KO_REPORT, "en": EN_REPORT}),
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=False,
        )

        self.assertEqual(process.returncode, 0, process.stderr)
        payload = json.loads(process.stdout)
        self.assertEqual(len(payload["artifacts"]), 2)
        self.assertTrue(all(Path(path).is_file() for path in payload["artifacts"]))


class PlanSummaryHtmlTests(unittest.TestCase):
    def test_renders_plan_cards_without_git_specific_labels(self) -> None:
        rendered = renderer.render_html_report(
            renderer.parse_report(KO_REPORT), renderer.parse_report(EN_REPORT)
        )

        self.assertIn("Plan Summary", rendered)
        self.assertIn('data-summary-id="PS-001"', rendered)
        self.assertIn("docs/plan.md#release-scope", rendered)
        self.assertIn("Source basis", rendered)
        for forbidden in (
            "Diff Summary",
            ".diff-summaries",
            "DS-",
            "diff-summary:",
            ">Repository<",
            ">Command<",
            ">HEAD<",
            "requested Git scope",
        ):
            with self.subTest(forbidden=forbidden):
                self.assertNotIn(forbidden, rendered)

    def test_bilingual_html_defaults_to_korean_and_switches_the_whole_page(self) -> None:
        rendered = renderer.render_html_report(
            renderer.parse_report(KO_REPORT), renderer.parse_report(EN_REPORT)
        )

        self.assertIn('<html lang="ko"', rendered)
        self.assertIn('data-language-part="ko" class="language-part is-active"', rendered)
        self.assertIn('data-language-part="en" class="language-part" hidden', rendered)
        self.assertIn('data-set-lang="ko" aria-pressed="true"', rendered)
        self.assertIn('data-set-lang="en" aria-pressed="false"', rendered)
        self.assertIn("document.documentElement.lang = language", rendered)
        self.assertIn("첫 출시의 문서 요약 범위", rendered)
        self.assertIn("The first release defines", rendered)

    def test_html_is_self_contained_and_escapes_document_content(self) -> None:
        unsafe = replace_once(
            KO_REPORT,
            "첫 출시의 문서 요약 범위와 검증 기준을 정리합니다.",
            '<script>alert("atlas & ink")</script>',
        )

        rendered = renderer.render_html_report(
            renderer.parse_report(unsafe), renderer.parse_report(EN_REPORT)
        )

        self.assertNotIn('<script>alert("atlas & ink")</script>', rendered)
        self.assertIn("&lt;script&gt;alert", rendered)
        self.assertIn(r"\u003cscript\u003ealert", rendered)
        self.assertNotRegex(rendered, r'<(?:link|script)[^>]+src=["\']https?://')
        self.assertNotRegex(rendered, r'<link[^>]+href=["\']https?://')

    def test_quiz_options_are_accessible_buttons_with_one_shot_answer_behavior(self) -> None:
        rendered = renderer.render_html_report(
            renderer.parse_report(KO_QUIZ_REPORT),
            renderer.parse_report(EN_QUIZ_REPORT),
        )

        self.assertIn('class="quiz-option"', rendered)
        self.assertIn('data-quiz-correct="true"', rendered)
        self.assertIn('aria-pressed="false"', rendered)
        self.assertIn('role="status"', rendered)
        self.assertIn("if (question.dataset.answered === \"true\")", rendered)
        self.assertIn("option.disabled = true", rendered)
        self.assertIn("explanation.open = true", rendered)

    def test_print_styles_reveal_the_quiz_answer_key(self) -> None:
        rendered = renderer.render_html_report(renderer.parse_report(KO_QUIZ_REPORT))

        self.assertIn("@media print", rendered)
        self.assertIn('.quiz-option[data-quiz-correct="true"]::after', rendered)
        self.assertIn(".quiz-explanation {", rendered)
        self.assertIn("display: block !important", rendered)

    def test_runtime_uses_plan_summary_storage_keys(self) -> None:
        rendered = renderer.render_html_report(
            renderer.parse_report(KO_REPORT), renderer.parse_report(EN_REPORT)
        )

        self.assertIn("data-plan-summary-runtime", rendered)
        self.assertIn('const THEME_KEY = "plan-summary:theme"', rendered)
        self.assertIn('const LANGUAGE_KEY = "plan-summary:language"', rendered)
        self.assertNotIn("diff-summary:", rendered)

    def test_default_generation_writes_one_bilingual_html_file(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            output = Path(temporary_directory) / ".plan-summaries"

            korean, english, html_path = renderer.generate_bilingual_report_in_directory(
                KO_REPORT, EN_REPORT, output
            )

            self.assertTrue(korean.is_file())
            self.assertTrue(english.is_file())
            self.assertIsNotNone(html_path)
            assert html_path is not None
            self.assertIn("data-plan-summary-runtime", html_path.read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
