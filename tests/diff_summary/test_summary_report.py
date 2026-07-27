from __future__ import annotations

import json
import io
import re
import subprocess
import sys
import tempfile
import unittest
from contextlib import redirect_stderr
from dataclasses import FrozenInstanceError, replace
from html.parser import HTMLParser
from pathlib import Path
from unittest import mock


ROOT = Path(__file__).resolve().parents[2]
SCRIPTS_DIR = ROOT / "code-review" / "skills" / "diff-summary" / "scripts"
SCRIPT_PATH = SCRIPTS_DIR / "generate_summary_report.py"
sys.path.insert(0, str(SCRIPTS_DIR))

import generate_summary_report as renderer  # noqa: E402
from generate_summary_report import (  # noqa: E402
    ParsedReport,
    ReportFormatError,
    ReportMetadata,
    SummaryCard,
    parse_report,
    safe_fence_language,
)


REPORT = """# main..dev Diff Summary

**Date:** 2026-07-13
**Repository:** chann/skills
**Scope:** main..dev
**Command:** `git diff --no-ext-diff --no-color --end-of-options main..dev`
**HEAD:** abc1234
**Language:** KO

## Executive Summary

| Metric | Value |
| --- | ---: |
| Summary cards | 2 |
| High impact | 1 |

The change set keeps **review context** close to `main..dev` while rendering <script>alert("atlas & ink")</script> as text.

- Preserve the exact comparison scope
- Keep 검토 맥락 close to the change

1. Parse the report safely
2. Render a portable atlas

## Changes

### Architecture

#### [DS-001] Separate parsing from rendering

**Category:** Architecture
**Impact:** High
**Files:** `src/report_parser.py`, `tests/test_report_parser.py`

파서가 렌더러와 분리되어 입력 계약을 한 곳에서 검증합니다.

```python
def parse_report(markdown):
    return markdown
```

```diff
@@ -1,2 +1,2 @@
-return unsafe_html
+return escaped_html
 context_line
```

### Tests

#### [DS-002] Cover report validation

**Category:** Test
**Impact:** Medium
**Files:** `tests/test_report_parser.py`

`main..dev` 범위와 유니코드 내용을 회귀 테스트로 보호합니다.

- Exact card Markdown remains available to copy.
- Offline output remains reviewable.

## Notes

Generated footer outside the summary cards.
"""


METADATA_LINES = {
    "Title": "# main..dev Diff Summary",
    "Date": "**Date:** 2026-07-13",
    "Repository": "**Repository:** chann/skills",
    "Scope": "**Scope:** main..dev",
    "Command": "**Command:** `git diff --no-ext-diff --no-color --end-of-options main..dev`",
    "HEAD": "**HEAD:** abc1234",
    "Language": "**Language:** KO",
}


QUIZ_SECTION = """## Quiz

#### [QZ-001] What does separating the parser protect?

짧은 근거 문단이 질문 앞에 올 수 있습니다.

- [ ] Rendering speed
- [x] Input contract validation in `parse_report`
- [ ] Browser storage of <script>alert("quiz")</script>

**Explanation:** `parse_report` validates the report contract in one place before rendering.

#### [QZ-002] Which scope stays byte-identical?

- [x] `main..dev`
- [ ] `main...dev`

**Explanation:** The requested two-dot scope is preserved exactly.
"""


QUIZ_REPORT = REPORT + "\n" + QUIZ_SECTION

ENGLISH_REPORT = """# main..dev Diff Summary

**Date:** 2026-07-13
**Repository:** chann/skills
**Scope:** main..dev
**Command:** `git diff --no-ext-diff --no-color --end-of-options main..dev`
**HEAD:** abc1234
**Language:** en

## Executive Summary

| Metric | Value |
| --- | ---: |
| Summary cards | 2 |
| High impact | 1 |

The change set keeps **review context** close to `main..dev` while rendering escaped markup as text.

## Changes

### Architecture

#### [DS-001] Separate parsing from rendering

**Category:** Architecture
**Impact:** High
**Files:** `src/report_parser.py`, `tests/test_report_parser.py`

The parser validates the input contract independently from the renderer.

### Tests

#### [DS-002] Cover report validation

**Category:** Test
**Impact:** Medium
**Files:** `tests/test_report_parser.py`

Regression tests preserve the exact `main..dev` scope and Unicode content.

## Notes

Generated footer outside the summary cards.
"""


def replace_once(markdown: str, old: str, new: str) -> str:
    if markdown.count(old) != 1:
        raise AssertionError(f"fixture fragment must occur exactly once: {old!r}")
    return markdown.replace(old, new, 1)


def remove_card_field(markdown: str, field: str) -> str:
    lines = markdown.splitlines(keepends=True)
    prefix = f"**{field}:**"
    for index, line in enumerate(lines):
        if line.startswith(prefix):
            del lines[index]
            return "".join(lines)
    raise AssertionError(f"fixture field not found: {field}")


def source_line_number(markdown: str, fragment: str) -> int:
    return markdown[: markdown.index(fragment)].count("\n") + 1


class SummaryReportSuccessTests(unittest.TestCase):
    def test_scope_tags_encode_dot_semantics_and_hash_sanitization_collisions(
        self,
    ) -> None:
        two_dot = renderer.scope_tag("main..dev")
        three_dot = renderer.scope_tag("main...dev")
        slash = renderer.scope_tag("release/a")
        colon = renderer.scope_tag("release:a")

        self.assertRegex(two_dot, r"^main-dot2-dev-[0-9a-f]{12}$")
        self.assertRegex(three_dot, r"^main-dot3-dev-[0-9a-f]{12}$")
        self.assertNotEqual(two_dot, three_dot)
        self.assertRegex(slash, r"^release-a-[0-9a-f]{12}$")
        self.assertRegex(colon, r"^release-a-[0-9a-f]{12}$")
        self.assertNotEqual(slash, colon)
        self.assertEqual(renderer.scope_tag("working"), "working")
        self.assertEqual(renderer.scope_tag("PR #42"), "pr-42")

    def test_parses_metadata_cards_and_exact_markdown_slices(self) -> None:
        parsed = parse_report(REPORT)

        self.assertIsInstance(parsed, ParsedReport)
        self.assertEqual(
            parsed.metadata,
            ReportMetadata(
                title="main..dev Diff Summary",
                date="2026-07-13",
                repository="chann/skills",
                scope="main..dev",
                command="git diff --no-ext-diff --no-color --end-of-options main..dev",
                head="abc1234",
                language="ko",
            ),
        )
        self.assertEqual(parsed.markdown, REPORT)
        self.assertIsInstance(parsed.cards, tuple)
        self.assertEqual(len(parsed.cards), 2)

        first, second = parsed.cards
        self.assertIsInstance(first, SummaryCard)
        self.assertEqual(
            (
                first.id,
                first.title,
                first.section,
                first.category,
                first.impact,
                first.files,
            ),
            (
                "DS-001",
                "Separate parsing from rendering",
                "Architecture",
                "Architecture",
                "High",
                ("src/report_parser.py", "tests/test_report_parser.py"),
            ),
        )
        self.assertEqual(
            (
                second.id,
                second.title,
                second.section,
                second.category,
                second.impact,
                second.files,
            ),
            (
                "DS-002",
                "Cover report validation",
                "Tests",
                "Test",
                "Medium",
                ("tests/test_report_parser.py",),
            ),
        )

        first_start = REPORT.index("#### [DS-001]")
        second_section = REPORT.index("### Tests")
        second_start = REPORT.index("#### [DS-002]")
        report_notes = REPORT.index("## Notes")
        self.assertEqual(first.markdown, REPORT[first_start:second_section])
        self.assertEqual(second.markdown, REPORT[second_start:report_notes])
        self.assertIn("파서가 렌더러와 분리", first.markdown)
        self.assertIn("유니코드 내용을", second.markdown)

    def test_accepts_h3_sections_indented_by_one_to_three_spaces(self) -> None:
        for width in (1, 2, 3):
            with self.subTest(width=width):
                report = replace_once(
                    REPORT,
                    "### Architecture",
                    f"{' ' * width}### Architecture",
                )

                parsed = parse_report(report)

                self.assertEqual(
                    [card.id for card in parsed.cards], ["DS-001", "DS-002"]
                )
                self.assertEqual(parsed.cards[0].section, "Architecture")
                first_start = report.index("#### [DS-001]")
                first_end = report.index("### Tests")
                self.assertEqual(
                    parsed.cards[0].markdown, report[first_start:first_end]
                )

    def test_accepts_h4_cards_indented_by_one_to_three_spaces(self) -> None:
        for width in (1, 2, 3):
            with self.subTest(width=width):
                prefix = " " * width
                report = replace_once(
                    REPORT,
                    "#### [DS-001] Separate parsing from rendering",
                    f"{prefix}#### [DS-001] Separate parsing from rendering",
                )

                try:
                    parsed = parse_report(report)
                except ReportFormatError as error:
                    self.fail(f"valid indented H4 was rejected: {error}")

                self.assertEqual(
                    [card.id for card in parsed.cards], ["DS-001", "DS-002"]
                )
                self.assertEqual(parsed.cards[0].section, "Architecture")
                first_start = report.index(f"{prefix}#### [DS-001]")
                first_end = report.index("### Tests")
                self.assertEqual(
                    parsed.cards[0].markdown, report[first_start:first_end]
                )

    def test_returned_dataclasses_are_frozen(self) -> None:
        parsed = parse_report(REPORT)

        with self.assertRaises(FrozenInstanceError):
            parsed.metadata.title = "changed"  # type: ignore[misc]
        with self.assertRaises(FrozenInstanceError):
            parsed.cards[0].impact = "Low"  # type: ignore[misc]
        with self.assertRaises(FrozenInstanceError):
            parsed.markdown = "changed"  # type: ignore[misc]

    def test_preserves_non_command_metadata_and_strips_only_command_wrapper(
        self,
    ) -> None:
        report = replace_once(
            REPORT, "**Repository:** chann/skills", "**Repository:** Chann / Skills"
        )
        report = replace_once(
            report,
            METADATA_LINES["Command"],
            "**Command:** git diff `main..dev`",
        )

        parsed = parse_report(report)

        self.assertEqual(parsed.metadata.repository, "Chann / Skills")
        self.assertEqual(parsed.metadata.command, "git diff `main..dev`")

    def test_rejects_korean_category_alias(self) -> None:
        report = replace_once(
            REPORT, "**Category:** Architecture", "**Category:** 아키텍처"
        )

        with self.assertRaisesRegex(ReportFormatError, "DS-001.*Category.*아키텍처"):
            parse_report(report)

    def test_rejects_korean_impact_alias(self) -> None:
        report = replace_once(REPORT, "**Impact:** High", "**Impact:** 높음")

        with self.assertRaisesRegex(ReportFormatError, "DS-001.*Impact.*높음"):
            parse_report(report)

    def test_ignores_metadata_fields_inside_fenced_code(self) -> None:
        fenced_metadata = """```markdown
# Not the report title
**Date:** 1900-01-01
**Language:** unsafe
```

"""
        report = replace_once(REPORT, "## Changes", fenced_metadata + "## Changes")

        parsed = parse_report(report)

        self.assertEqual(parsed.metadata.title, "main..dev Diff Summary")
        self.assertEqual(parsed.metadata.date, "2026-07-13")
        self.assertEqual(parsed.metadata.language, "ko")

    def test_ignores_card_fields_and_headings_inside_fenced_code(self) -> None:
        fenced_body = """파서가 렌더러와 분리되어 입력 계약을 한 곳에서 검증합니다.

```markdown
### 가짜 섹션
#### [DS-999] 가짜 카드
    #### [DS-998] 과도하게 들여쓴 가짜 카드
	#### [DS-997] 탭으로 들여쓴 가짜 카드
**Category:** Security
**Impact:** Low
**Files:** `fake.py`
```
"""
        report = replace_once(
            REPORT,
            "파서가 렌더러와 분리되어 입력 계약을 한 곳에서 검증합니다.",
            fenced_body.rstrip("\n"),
        )

        parsed = parse_report(report)

        self.assertEqual([card.id for card in parsed.cards], ["DS-001", "DS-002"])
        self.assertEqual(parsed.cards[0].section, "Architecture")
        self.assertIn("#### [DS-999] 가짜 카드", parsed.cards[0].markdown)
        self.assertIn(
            "    #### [DS-998] 과도하게 들여쓴 가짜 카드", parsed.cards[0].markdown
        )
        self.assertIn(
            "\t#### [DS-997] 탭으로 들여쓴 가짜 카드", parsed.cards[0].markdown
        )


class MetadataValidationTests(unittest.TestCase):
    def test_rejects_each_missing_metadata_field(self) -> None:
        for field, line in METADATA_LINES.items():
            with self.subTest(field=field):
                report = replace_once(REPORT, line + "\n", "")
                with self.assertRaisesRegex(ReportFormatError, field):
                    parse_report(report)

    def test_rejects_each_empty_metadata_field(self) -> None:
        for field, line in METADATA_LINES.items():
            with self.subTest(field=field):
                empty_line = "#   " if field == "Title" else f"**{field}:**   "
                report = replace_once(REPORT, line, empty_line)
                with self.assertRaisesRegex(ReportFormatError, field):
                    parse_report(report)

    def test_rejects_each_duplicate_metadata_field(self) -> None:
        for field, line in METADATA_LINES.items():
            with self.subTest(field=field):
                report = replace_once(REPORT, line, f"{line}\n{line}")
                with self.assertRaisesRegex(ReportFormatError, field):
                    parse_report(report)

    def test_rejects_metadata_and_title_repeated_after_the_header(self) -> None:
        for field, line in METADATA_LINES.items():
            with self.subTest(field=field):
                report = f"{REPORT}\n{line}\n"
                with self.assertRaisesRegex(ReportFormatError, field):
                    parse_report(report)


class CardIdentityValidationTests(unittest.TestCase):
    def test_rejects_malformed_card_id(self) -> None:
        report = replace_once(REPORT, "#### [DS-001]", "  #### [DS-01]")
        heading_line = source_line_number(report, "  #### [DS-01]")

        with self.assertRaisesRegex(
            ReportFormatError,
            rf"malformed.*heading.*line {heading_line}.*DS-01",
        ):
            parse_report(report)

    def test_rejects_final_card_heading_indented_four_spaces(self) -> None:
        report = replace_once(REPORT, "#### [DS-002]", "    #### [DS-002]")
        heading_line = source_line_number(report, "    #### [DS-002]")

        with self.assertRaisesRegex(
            ReportFormatError,
            rf"over-indented.*line {heading_line}.*DS-002",
        ):
            parse_report(report)

    def test_rejects_final_card_heading_indented_with_tab(self) -> None:
        report = replace_once(REPORT, "#### [DS-002]", "\t#### [DS-002]")
        heading_line = source_line_number(report, "\t#### [DS-002]")

        with self.assertRaisesRegex(
            ReportFormatError,
            rf"over-indented.*line {heading_line}.*DS-002",
        ):
            parse_report(report)

    def test_rejects_duplicate_card_ids(self) -> None:
        report = replace_once(REPORT, "#### [DS-002]", "#### [DS-001]")

        with self.assertRaisesRegex(ReportFormatError, "duplicate.*DS-001"):
            parse_report(report)

    def test_rejects_gap_in_card_ids(self) -> None:
        report = replace_once(REPORT, "#### [DS-002]", "#### [DS-003]")

        with self.assertRaisesRegex(ReportFormatError, "expected DS-002.*DS-003"):
            parse_report(report)

    def test_rejects_out_of_order_card_ids(self) -> None:
        report = replace_once(REPORT, "#### [DS-001]", "#### [DS-002]")
        report = replace_once(report, "#### [DS-002] Cover", "#### [DS-001] Cover")

        with self.assertRaisesRegex(ReportFormatError, "expected DS-001.*DS-002"):
            parse_report(report)

    def test_rejects_report_without_cards(self) -> None:
        report = REPORT[: REPORT.index("### Architecture")]

        with self.assertRaisesRegex(ReportFormatError, "no cards"):
            parse_report(report)


class CardFieldValidationTests(unittest.TestCase):
    def test_rejects_each_missing_required_card_field(self) -> None:
        for field in ("Category", "Impact", "Files"):
            with self.subTest(field=field):
                report = remove_card_field(REPORT, field)
                with self.assertRaisesRegex(ReportFormatError, rf"DS-001.*{field}"):
                    parse_report(report)

    def test_rejects_each_duplicate_required_card_field(self) -> None:
        values = {
            "Category": "Architecture",
            "Impact": "High",
            "Files": "`src/report_parser.py`",
        }
        for field, value in values.items():
            with self.subTest(field=field):
                line = f"**{field}:** {value}"
                report = replace_once(REPORT, line, f"{line}\n{line}")
                with self.assertRaisesRegex(
                    ReportFormatError, rf"DS-001.*duplicate.*{field}"
                ):
                    parse_report(report)

    def test_rejects_unsupported_category(self) -> None:
        report = replace_once(
            REPORT, "**Category:** Architecture", "**Category:** Documentation"
        )

        with self.assertRaisesRegex(
            ReportFormatError, "DS-001.*Category.*Documentation"
        ):
            parse_report(report)

    def test_rejects_unsupported_impact(self) -> None:
        report = replace_once(REPORT, "**Impact:** High", "**Impact:** Critical")

        with self.assertRaisesRegex(ReportFormatError, "DS-001.*Impact.*Critical"):
            parse_report(report)

    def test_rejects_malformed_files_values(self) -> None:
        malformed_values = (
            "",
            "src/report_parser.py",
            "`src/report_parser.py`,",
            "`src/report_parser.py` and tests",
            "`src/report_parser.py`, `src/report_parser.py`",
            "``",
        )
        for value in malformed_values:
            with self.subTest(value=value):
                report = replace_once(
                    REPORT,
                    "**Files:** `src/report_parser.py`, `tests/test_report_parser.py`",
                    f"**Files:** {value}",
                )
                with self.assertRaisesRegex(ReportFormatError, "DS-001.*Files"):
                    parse_report(report)

    def test_card_validation_errors_include_card_heading_line(self) -> None:
        heading_line = source_line_number(REPORT, "#### [DS-001]")
        category_line = "**Category:** Architecture"
        cases = {
            "missing field": remove_card_field(REPORT, "Category"),
            "duplicate field": replace_once(
                REPORT,
                category_line,
                f"{category_line}\n{category_line}",
            ),
            "category": replace_once(
                REPORT,
                category_line,
                "**Category:** Documentation",
            ),
            "impact": replace_once(REPORT, "**Impact:** High", "**Impact:** Critical"),
            "files": replace_once(
                REPORT,
                "**Files:** `src/report_parser.py`, `tests/test_report_parser.py`",
                "**Files:** src/report_parser.py",
            ),
        }

        for label, report in cases.items():
            with self.subTest(label=label):
                with self.assertRaisesRegex(
                    ReportFormatError,
                    rf"DS-001.*heading line {heading_line}\b",
                ):
                    parse_report(report)


class FenceValidationTests(unittest.TestCase):
    def test_rejects_unclosed_fenced_code_blocks(self) -> None:
        for opening in ("```python", "~~~text"):
            with self.subTest(opening=opening):
                report = REPORT + f"\n{opening}\ncontent\n"
                with self.assertRaisesRegex(ReportFormatError, "unclosed.*fence"):
                    parse_report(report)

    def test_safe_fence_language_allows_only_safe_ascii_and_caps_length(self) -> None:
        self.assertEqual(safe_fence_language("python"), "python")
        self.assertEqual(safe_fence_language("c++"), "c++")
        self.assertEqual(safe_fence_language("tsx.jsx-1_2"), "tsx.jsx-1_2")
        self.assertEqual(safe_fence_language("a" * 40), "a" * 32)
        self.assertEqual(safe_fence_language("python onclick=alert(1)"), "")
        self.assertEqual(safe_fence_language("<script>"), "")
        self.assertEqual(safe_fence_language("파이썬"), "")


TEMPLATE_PLACEHOLDERS = (
    "__REPORT_TITLE__",
    "__REPORT_LANGUAGE__",
    "__REPORT_METADATA__",
    "__REPORT_BODY__",
    "__SIDEBAR_REPOSITORY__",
    "__SIDEBAR_NAV__",
    "__LANGUAGE_CONTROL__",
    "__SUMMARY_DATA__",
    "__RAW_MARKDOWN__",
    "__COMMENT_SCOPE__",
    "__DEFAULT_THEME__",
)


class _MarkupInventory(HTMLParser):
    _VOID_ELEMENTS = {
        "area",
        "base",
        "br",
        "col",
        "embed",
        "hr",
        "img",
        "input",
        "link",
        "meta",
        "param",
        "source",
        "track",
        "wbr",
    }

    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.elements: list[tuple[str, dict[str, str | None]]] = []
        self.ancestors: list[
            tuple[tuple[str, dict[str, str | None]], ...]
        ] = []
        self._open_elements: list[tuple[str, dict[str, str | None]]] = []

    def handle_starttag(
        self,
        tag: str,
        attrs: list[tuple[str, str | None]],
    ) -> None:
        attributes = dict(attrs)
        self.elements.append((tag, attributes))
        self.ancestors.append(tuple(self._open_elements))
        if tag not in self._VOID_ELEMENTS:
            self._open_elements.append((tag, attributes))

    def handle_startendtag(
        self,
        tag: str,
        attrs: list[tuple[str, str | None]],
    ) -> None:
        self.elements.append((tag, dict(attrs)))
        self.ancestors.append(tuple(self._open_elements))

    def handle_endtag(self, tag: str) -> None:
        for index in range(len(self._open_elements) - 1, -1, -1):
            if self._open_elements[index][0] == tag:
                del self._open_elements[index:]
                return


def extract_json_script(rendered: str, element_id: str):
    match = re.search(
        rf'<script(?=[^>]*\bid="{re.escape(element_id)}")'
        rf'(?=[^>]*\btype="application/json")[^>]*>(.*?)</script>',
        rendered,
        re.DOTALL,
    )
    if match is None:
        raise AssertionError(f"application/json script not found: {element_id}")
    return json.loads(match.group(1))


def extract_runtime_script(rendered: str) -> str:
    match = re.search(
        r"<script(?=[^>]*\bdata-diff-summary-runtime(?:\s|=|>))"
        r"(?=[^>]*>)(?![^>]*\bsrc=)[^>]*>(.*?)</script>",
        rendered,
        re.DOTALL,
    )
    if match is None:
        raise AssertionError("inline diff-summary runtime script not found")
    return match.group(1)


def run_runtime_harness(runtime: str, scenario: dict) -> dict:
    source = (
        "const runtimeSource = "
        + json.dumps(runtime)
        + ";\nconst scenario = "
        + json.dumps(scenario)
        + ";\n"
        + r"""
const vm = require("node:vm");

class FakeClassList {
  constructor(...names) {
    this.names = new Set(names);
  }
  add(...names) {
    names.forEach((name) => this.names.add(name));
  }
  remove(...names) {
    names.forEach((name) => this.names.delete(name));
  }
  contains(name) {
    return this.names.has(name);
  }
  toggle(name, force) {
    const enabled = force === undefined ? !this.names.has(name) : Boolean(force);
    if (enabled) this.names.add(name);
    else this.names.delete(name);
    return enabled;
  }
}

class FakeElement {
  constructor(tagName = "div", classes = []) {
    this.tagName = tagName.toUpperCase();
    this._className = classes.join(" ");
    this.classList = new FakeClassList(...classes);
    this.dataset = {};
    this.attributes = new Map();
    this.children = [];
    this.parentNode = null;
    this.textContent = "";
    this.value = "";
    this.hidden = false;
    this.disabled = false;
    this.isConnected = true;
    this.listeners = new Map();
    this.selectionStart = 0;
    this.selectionEnd = 0;
    this.style = { setProperty() {} };
  }
  set className(value) {
    this._className = String(value);
    this.classList = new FakeClassList(
      ...this._className.split(/\s+/).filter(Boolean),
    );
  }
  get className() {
    return this._className;
  }
  setAttribute(name, value) {
    const stringValue = String(value);
    this.attributes.set(name, stringValue);
    if (name === "id") this.id = stringValue;
    if (name.startsWith("data-")) {
      const key = name.slice(5).replace(/-([a-z])/g, (_, letter) => letter.toUpperCase());
      this.dataset[key] = stringValue;
    }
  }
  getAttribute(name) {
    return this.attributes.has(name) ? this.attributes.get(name) : null;
  }
  removeAttribute(name) {
    this.attributes.delete(name);
    if (name.startsWith("data-")) {
      const key = name.slice(5).replace(/-([a-z])/g, (_, letter) => letter.toUpperCase());
      delete this.dataset[key];
    }
  }
  append(...nodes) {
    nodes.forEach((node) => {
      node.parentNode = this;
      node.isConnected = true;
      this.children.push(node);
    });
  }
  insertBefore(node, reference) {
    const index = this.children.indexOf(reference);
    node.parentNode = this;
    node.isConnected = true;
    if (index === -1) this.children.push(node);
    else this.children.splice(index, 0, node);
  }
  replaceChildren(...nodes) {
    this.children.forEach((node) => {
      node.parentNode = null;
      node.isConnected = false;
    });
    this.children = [];
    this.append(...nodes);
  }
  remove() {
    if (this.parentNode) {
      this.parentNode.children = this.parentNode.children.filter((node) => node !== this);
    }
    this.parentNode = null;
    this.isConnected = false;
  }
  focus() {
    document.activeElement = this;
  }
  select() {
    this.selectionStart = 0;
    this.selectionEnd = this.value.length;
  }
  setSelectionRange(start, end) {
    this.selectionStart = start;
    this.selectionEnd = end;
  }
  addEventListener(type, listener) {
    if (!this.listeners.has(type)) this.listeners.set(type, []);
    this.listeners.get(type).push(listener);
  }
  dispatch(type, event = {}) {
    (this.listeners.get(type) || []).forEach((listener) => listener({
      preventDefault() {},
      target: this,
      ...event,
    }));
  }
  querySelector(selector) {
    return this.querySelectorAll(selector)[0] || null;
  }
  querySelectorAll(selector) {
    const matches = [];
    const visit = (node) => {
      node.children.forEach((child) => {
        if (child.matches(selector)) matches.push(child);
        visit(child);
      });
    };
    visit(this);
    return matches;
  }
  matches(selector) {
    const classSelector = selector.match(
      /^\.([A-Za-z0-9_-]+)(?:\[data-([A-Za-z0-9-]+)\])?$/,
    );
    if (classSelector) {
      if (!this.classList.contains(classSelector[1])) return false;
      if (!classSelector[2]) return true;
      const key = classSelector[2].replace(
        /-([a-z])/g,
        (_, letter) => letter.toUpperCase(),
      );
      return Object.hasOwn(this.dataset, key);
    }
    const dataSelector = selector.match(/^\[data-([A-Za-z0-9-]+)\]$/);
    if (dataSelector) {
      const key = dataSelector[1].replace(
        /-([a-z])/g,
        (_, letter) => letter.toUpperCase(),
      );
      return Object.hasOwn(this.dataset, key);
    }
    return this.tagName === selector.toUpperCase();
  }
  closest(selector) {
    return selector === "button" && this.tagName === "BUTTON" ? this : null;
  }
  scrollIntoView() {}
  setPointerCapture() {}
  hasPointerCapture() { return false; }
  releasePointerCapture() {}
}

const body = new FakeElement("body");
body.dataset.defaultTheme = scenario.defaultTheme || "auto";
const documentElement = new FakeElement("html");
documentElement.lang = scenario.language || "en";
const status = new FakeElement("div");
status.id = "report-status";
const header = new FakeElement("header", ["report-header"]);
header.dataset.repository = "chann/skills";
header.dataset.scope = "main..dev";
const payloads = new Map();
for (const [id, value] of Object.entries({
  "summary-data": scenario.summaryData,
  "raw-markdown": scenario.rawMarkdown,
  "comment-scope": scenario.commentScope,
})) {
  const element = new FakeElement("script");
  element.id = id;
  element.textContent = scenario.invalidPayload === id ? "{" : JSON.stringify(value);
  payloads.set(id, element);
}
payloads.set("report-status", status);

const cards = (scenario.domCardIds || []).map((id) => {
  const card = new FakeElement("details", ["summary-card"]);
  card.dataset.summaryId = id;
  return card;
});
const controls = {
  add: new FakeElement("button"),
  feedback: new FakeElement("button"),
  clear: new FakeElement("button"),
};
const printControl = new FakeElement("button");
printControl.dataset.printReport = "";
const sidebarToggle = new FakeElement("button");
sidebarToggle.dataset.sidebarToggle = "";
sidebarToggle.dataset.testFocus = "sidebar-toggle";
const sidebarExpand = new FakeElement("button");
sidebarExpand.dataset.sidebarExpand = "";
sidebarExpand.dataset.testFocus = "sidebar-expand";
controls.add.dataset.addComment = "DS-001";
controls.feedback.dataset.copyFeedback = "";
controls.clear.dataset.clearComments = "";
if (cards[0]) {
  const panel = new FakeElement("div", ["card-panel"]);
  const toolbar = new FakeElement("div", ["card-toolbar"]);
  toolbar.append(controls.add);
  panel.append(toolbar);
  cards[0].append(panel);
}

const quizElements = (scenario.quizQuestions || []).map((spec) => {
  const question = new FakeElement("section", ["quiz-question"]);
  question.dataset.quizId = spec.id;
  const list = new FakeElement("ol", ["quiz-options"]);
  const optionButtons = [];
  for (let index = 0; index < spec.options; index += 1) {
    const item = new FakeElement("li", ["quiz-option-item"]);
    const button = new FakeElement("button", ["quiz-option"]);
    button.dataset.quizId = spec.id;
    button.dataset.quizOption = String(index);
    button.dataset.quizLabel = (spec.labels || [])[index] || `Option ${index + 1}`;
    button.setAttribute("aria-pressed", "false");
    if (index === spec.correct) {
      button.dataset.quizCorrect = "";
    }
    item.append(button);
    list.append(item);
    optionButtons.push(button);
  }
  const status = new FakeElement("p", ["quiz-status"]);
  status.dataset.quizStatus = "";
  status.hidden = true;
  const explanation = new FakeElement("details", ["quiz-explanation"]);
  explanation.open = Boolean(spec.explanationOpen);
  question.append(list, status, explanation);
  return { question, optionButtons, status, explanation };
});

const selectorLists = new Map([
  [".summary-card[data-summary-id]", cards],
  [".metadata-cell", []],
  ["[data-add-comment]", [controls.add]],
  ["[data-copy-feedback]", [controls.feedback]],
  ["[data-clear-comments]", [controls.clear]],
  ["[data-copy-summary]", []],
  [".card-files-title", []],
  [".quiz-question[data-quiz-id]", quizElements.map((entry) => entry.question)],
  ["[data-quiz-option]", quizElements.flatMap((entry) => entry.optionButtons)],
  [".quiz-explanation", quizElements.map((entry) => entry.explanation)],
  [".quiz-explanation-title", []],
  ["[data-print-report]", [printControl]],
]);
const selectorSingles = new Map([
  [".report-header", header],
  ["[data-copy-feedback]", controls.feedback],
  ["[data-clear-comments]", controls.clear],
  ["[data-sidebar-toggle]", sidebarToggle],
  ["[data-sidebar-expand]", sidebarExpand],
  ["[data-print-report]", printControl],
]);

const documentListeners = new Map();
globalThis.document = {
  body,
  documentElement,
  activeElement: null,
  getElementById(id) { return payloads.get(id) || null; },
  querySelector(selector) { return selectorSingles.get(selector) || null; },
  querySelectorAll(selector) { return selectorLists.get(selector) || []; },
  createElement(tagName) { return new FakeElement(tagName); },
  addEventListener(type, listener) {
    if (!documentListeners.has(type)) documentListeners.set(type, []);
    documentListeners.get(type).push(listener);
  },
  dispatchEvent(event) {
    (documentListeners.get(event.type) || []).forEach((listener) => listener(event));
    return true;
  },
  execCommand() {
    if (scenario.execCommandThrows) throw new Error("copy denied");
    return Boolean(scenario.execCommandResult);
  },
};
globalThis.Element = FakeElement;
globalThis.window = globalThis;
window.confirm = () => true;
let printCalls = 0;
window.print = () => { printCalls += 1; };
const windowListeners = new Map();
window.addEventListener = (type, listener) => {
  if (!windowListeners.has(type)) windowListeners.set(type, []);
  windowListeners.get(type).push(listener);
};
window.dispatchEvent = (event) => {
  (windowListeners.get(event.type) || []).forEach((listener) => listener(event));
  return true;
};
const origin = controls.add;
origin.dataset.testFocus = "origin";
document.activeElement = origin;

const storageValues = new Map(Object.entries(scenario.storage || {}));
const storageCalls = [];
globalThis.localStorage = {
  getItem(key) {
    storageCalls.push(["get", key]);
    if (scenario.storageGetThrows) throw new Error("storage denied");
    return storageValues.has(key) ? storageValues.get(key) : null;
  },
  setItem(key, value) {
    storageCalls.push(["set", key, value]);
    if (scenario.storageSetThrows) throw new Error("storage denied");
    storageValues.set(key, value);
  },
  removeItem(key) {
    storageCalls.push(["remove", key]);
    if (scenario.storageRemoveThrows) throw new Error("storage denied");
    storageValues.delete(key);
  },
};
Object.defineProperty(globalThis, "navigator", {
  configurable: true,
  value: {
    clipboard: {
      writeText() {
        if (scenario.clipboardRejects) return Promise.reject(new Error("clipboard denied"));
        return Promise.resolve();
      },
    },
  },
});
globalThis.__DIFF_SUMMARY_RUNTIME_TEST__ = {};

vm.runInThisContext(runtimeSource, { filename: "diff-summary-runtime.js" });

(async () => {
  const bridge = globalThis.__DIFF_SUMMARY_RUNTIME_TEST__;
  if (typeof bridge.getState !== "function") throw new Error("runtime bridge missing");
  const before = bridge.getState();
  let afterCopy = null;
  let afterDismiss = null;
  let afterCommentCommit = null;
  let quizPrintStates = null;
  let sidebarFocusStates = null;
  const quizAnswerResults = [];
  if (scenario.action === "copy-failure") {
    await bridge.copyText(scenario.copyText, "copied", "copy failed");
    afterCopy = bridge.getState();
    bridge.dismissManualCopy();
    afterDismiss = bridge.getState();
  } else if (scenario.action === "comment-commit") {
    if (
      typeof bridge.openCommentEditor !== "function" ||
      typeof bridge.commitActiveComment !== "function"
    ) {
      throw new Error("comment editor runtime bridge missing");
    }
    bridge.openCommentEditor("DS-001", null, origin);
    bridge.commitActiveComment(scenario.commentText);
    afterCommentCommit = bridge.getState();
  } else if (scenario.action === "quiz-answer") {
    if (typeof bridge.answerQuiz !== "function") {
      throw new Error("quiz runtime bridge missing");
    }
    quizAnswerResults.push(
      bridge.answerQuiz(scenario.quizAnswerId, scenario.quizAnswerIndex),
    );
    if (scenario.quizRepeatIndex !== undefined) {
      quizAnswerResults.push(
        bridge.answerQuiz(scenario.quizAnswerId, scenario.quizRepeatIndex),
      );
    }
  } else if (scenario.action === "quiz-print") {
    const openStates = () => quizElements.map(
      (entry) => Boolean(entry.explanation.open),
    );
    const beforePrint = openStates();
    window.dispatchEvent({ type: "beforeprint" });
    const duringPrint = openStates();
    window.dispatchEvent({ type: "afterprint" });
    quizPrintStates = { beforePrint, duringPrint, afterPrint: openStates() };
  } else if (scenario.action === "print-control") {
    document.dispatchEvent({ type: "click", target: printControl });
  } else if (scenario.action === "sidebar-focus") {
    document.dispatchEvent({ type: "click", target: sidebarToggle });
    const afterCollapse = bridge.getState().activeFocus;
    document.dispatchEvent({ type: "click", target: sidebarExpand });
    sidebarFocusStates = {
      afterCollapse,
      afterExpand: bridge.getState().activeFocus,
    };
  } else if (scenario.action === "sidebar-programmatic") {
    bridge.setSidebarCollapsed(true);
    const afterCollapse = bridge.getState().activeFocus;
    bridge.setSidebarCollapsed(false);
    sidebarFocusStates = {
      afterCollapse,
      afterExpand: bridge.getState().activeFocus,
    };
  }
  console.log(JSON.stringify({
    before,
    afterCopy,
    afterDismiss,
    afterCommentCommit,
    quizPrintStates,
    sidebarFocusStates,
    quizAnswerResults,
    quiz: quizElements.map((entry) => ({
      id: entry.question.dataset.quizId,
      answered: entry.question.dataset.quizAnswered || null,
      statusHidden: entry.status.hidden,
      statusText: entry.status.textContent,
      statusTone: entry.status.dataset.tone || null,
      explanationOpen: Boolean(entry.explanation.open),
      options: entry.optionButtons.map((button) => ({
        disabled: button.disabled,
        classes: Array.from(button.classList.names).sort(),
        ariaLabel: button.getAttribute("aria-label"),
        ariaPressed: button.getAttribute("aria-pressed"),
      })),
    })),
    status: status.textContent,
    tone: status.dataset.tone || null,
    storageCalls,
    printCalls,
    printControl: {
      textContent: printControl.textContent,
      ariaLabel: printControl.getAttribute("aria-label"),
    },
    controls: {
      addDisabled: controls.add.disabled,
      feedbackDisabled: controls.feedback.disabled,
      clearDisabled: controls.clear.disabled,
    },
  }));
})().catch((error) => {
  console.error(error.stack || String(error));
  process.exitCode = 1;
});
"""
    )
    with tempfile.TemporaryDirectory() as temporary_directory:
        harness_path = Path(temporary_directory) / "runtime-harness.js"
        harness_path.write_text(source, encoding="utf-8")
        result = subprocess.run(
            ["node", str(harness_path)],
            cwd=ROOT,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            check=False,
        )
    if result.returncode != 0:
        raise AssertionError(result.stdout)
    return json.loads(result.stdout.splitlines()[-1])


def details_block(rendered: str, summary_id: str) -> str:
    marker = f'data-summary-id="{summary_id}"'
    marker_index = rendered.index(marker)
    start = rendered.rfind("<details", 0, marker_index)
    end = rendered.index("</details>", marker_index) + len("</details>")
    return rendered[start:end]


def css_rule(stylesheet: str, selector: str) -> str:
    match = re.search(rf"{re.escape(selector)}\s*\{{(?P<body>[^{{}}]*)\}}", stylesheet)
    if match is None:
        raise AssertionError(f"CSS rule not found: {selector}")
    return match.group("body")


class StaticRendererApiTests(unittest.TestCase):
    def test_static_renderer_public_apis_exist(self) -> None:
        for api in (
            "json_for_script",
            "stable_comment_scope",
            "render_report_body",
            "assemble_html",
            "load_template",
            "replace_placeholders",
            "generate_report",
            "generate_bilingual_report_in_directory",
        ):
            with self.subTest(api=api):
                self.assertTrue(callable(getattr(renderer, api, None)), api)

    def test_json_for_script_round_trips_without_raw_script_breakouts(self) -> None:
        value = {
            "danger": "</script><script>alert('atlas')</script>",
            "marks": "ink & paper > screen < print\u2028next\u2029last",
            "korean": "안전한 요약",
        }

        encoded = renderer.json_for_script(value)

        self.assertEqual(json.loads(encoded), value)
        self.assertNotIn("</script", encoded.lower())
        self.assertNotIn("<", encoded)
        self.assertNotIn(">", encoded)
        self.assertNotIn("&", encoded)
        self.assertNotIn("\u2028", encoded)
        self.assertNotIn("\u2029", encoded)
        self.assertIn(r"\u003c/script\u003e", encoded.lower())
        self.assertIn(r"\u0026", encoded)
        self.assertIn(r"\u2028", encoded)
        self.assertIn(r"\u2029", encoded)

    def test_comment_scope_hashes_only_stable_review_identity(self) -> None:
        parsed = parse_report(REPORT)
        scope = renderer.stable_comment_scope(parsed)

        self.assertRegex(scope, r"^chann/skills::main\.\.dev::[0-9a-f]{20}$")
        self.assertEqual(scope, renderer.stable_comment_scope(parse_report(REPORT)))

        date_changed = parse_report(REPORT.replace("2026-07-13", "2027-01-02", 1))
        footer_changed = parse_report(
            REPORT.replace(
                "Generated footer outside the summary cards.",
                "A different generated footer remains outside the cards.",
            )
        )
        self.assertEqual(scope, renderer.stable_comment_scope(date_changed))
        self.assertEqual(scope, renderer.stable_comment_scope(footer_changed))

        mutations = (
            REPORT.replace("**Scope:** main..dev", "**Scope:** main...dev", 1),
            REPORT.replace("**HEAD:** abc1234", "**HEAD:** def5678", 1),
            REPORT.replace(
                "git diff --no-ext-diff --no-color --end-of-options main..dev",
                "git diff --no-color --end-of-options main..dev",
                1,
            ),
            REPORT.replace(
                "파서가 렌더러와 분리되어",
                "안전한 파서가 렌더러와 분리되어",
                1,
            ),
        )
        for changed_report in mutations:
            with self.subTest(changed=changed_report[:80]):
                self.assertNotEqual(
                    scope,
                    renderer.stable_comment_scope(parse_report(changed_report)),
                )

        reordered = ParsedReport(
            metadata=parsed.metadata,
            cards=tuple(reversed(parsed.cards)),
            markdown=parsed.markdown,
        )
        self.assertNotEqual(scope, renderer.stable_comment_scope(reordered))

    def test_comment_scope_normalizes_only_non_material_card_whitespace(self) -> None:
        parsed = parse_report(REPORT)
        scope = renderer.stable_comment_scope(parsed)

        crlf_cards = tuple(
            replace(card, markdown=card.markdown.replace("\n", "\r\n"))
            for card in parsed.cards
        )

        def add_trailing_horizontal_space(markdown: str) -> str:
            lines = markdown.split("\n")
            padded = [f"{line} \t" if line else "\t" for line in lines]
            return "\r".join(padded) + "\r\t\r\r"

        padded_cards = tuple(
            replace(card, markdown=add_trailing_horizontal_space(card.markdown))
            for card in parsed.cards
        )
        for cards in (crlf_cards, padded_cards):
            with self.subTest(line_form=cards[0].markdown[:40]):
                equivalent = replace(parsed, cards=cards)
                self.assertEqual(scope, renderer.stable_comment_scope(equivalent))

        changed_id = replace(
            parsed,
            cards=(replace(parsed.cards[0], id="DS-900"), *parsed.cards[1:]),
        )
        changed_indent = replace(
            parsed,
            cards=(
                replace(
                    parsed.cards[0],
                    markdown=parsed.cards[0].markdown.replace(
                        "def parse_report(markdown):",
                        " def parse_report(markdown):",
                        1,
                    ),
                ),
                *parsed.cards[1:],
            ),
        )
        self.assertNotEqual(scope, renderer.stable_comment_scope(changed_id))
        self.assertNotEqual(scope, renderer.stable_comment_scope(changed_indent))


class MarkdownRenderingTests(unittest.TestCase):
    def test_renders_supported_markdown_as_escaped_semantic_html(self) -> None:
        body = renderer.render_report_body(parse_report(REPORT))

        self.assertIn('<h2 id="executive-summary">Executive Summary</h2>', body)
        self.assertIn('<h3 id="architecture">Architecture</h3>', body)
        self.assertIn("<table", body)
        self.assertIn("<thead>", body)
        self.assertIn("<tbody>", body)
        self.assertIn("<ul>", body)
        self.assertIn("<ol>", body)
        self.assertIn("<strong>review context</strong>", body)
        self.assertIn("<code>main..dev</code>", body)
        self.assertIn('<code class="language-python">', body)
        self.assertIn('class="diff-line diff-line--hunk"', body)
        self.assertIn('class="diff-line diff-line--delete"', body)
        self.assertIn('class="diff-line diff-line--add"', body)
        self.assertIn("검토 맥락", body)
        self.assertIn(
            "&lt;script&gt;alert(&quot;atlas &amp; ink&quot;)&lt;/script&gt;", body
        )
        self.assertNotIn('<script>alert("atlas & ink")</script>', body)

    def test_table_cells_preserve_escaped_and_inline_code_pipes(self) -> None:
        table_report = replace_once(
            REPORT,
            """| Metric | Value |
| --- | ---: |
| Summary cards | 2 |
| High impact | 1 |""",
            r"""| Token | Meaning |
| --- | --- |
| a\|b | escaped pipe |
| `a|b` | inline code |""",
        )

        body = renderer.render_report_body(parse_report(table_report))
        table = body[body.index("<table>") : body.index("</table>") + len("</table>")]

        self.assertIn('<td class="align-left">a|b</td>', table)
        self.assertIn('<td class="align-left"><code>a|b</code></td>', table)
        self.assertNotIn(r"a\|b", table)
        self.assertEqual(table.count("<tr>"), 3)
        self.assertEqual(table.count("<td"), 4)

    def test_mismatched_table_body_row_rejects_the_whole_table(self) -> None:
        malformed_report = replace_once(
            REPORT,
            """| Metric | Value |
| --- | ---: |
| Summary cards | 2 |
| High impact | 1 |""",
            """| Metric | Value |
| --- | --- |
| Valid | row |
| Too | many | cells |""",
        )

        body = renderer.render_report_body(parse_report(malformed_report))

        self.assertNotIn("<table>", body)
        self.assertIn("| Too | many | cells |", body)

    def test_ordered_list_preserves_its_first_source_ordinal(self) -> None:
        ordered_report = replace_once(
            REPORT,
            "1. Parse the report safely\n2. Render a portable atlas",
            "3. Parse the report safely\n4. Render a portable atlas",
        )

        body = renderer.render_report_body(parse_report(ordered_report))

        self.assertIn('<ol start="3">', body)
        self.assertNotIn("<ol>\n<li>Parse the report safely", body)

    def test_renders_cards_with_identity_badges_files_and_bottom_toolbar(self) -> None:
        body = renderer.render_report_body(parse_report(REPORT))
        first = details_block(body, "DS-001")
        second = details_block(body, "DS-002")

        self.assertRegex(
            first, r"<details[^>]+class=\"[^\"]*summary-card[^\"]*impact-high"
        )
        self.assertRegex(first, r"<details[^>]+\sopen(?:\s|>)")
        self.assertIn('data-summary-id="DS-001"', first)
        self.assertIn('class="badge badge--category"', first)
        self.assertIn('data-category="Architecture"', first)
        self.assertIn('class="badge badge--impact"', first)
        self.assertIn('data-impact="High"', first)
        self.assertIn('class="comment-count"', first)
        self.assertIn('data-comment-count="DS-001"', first)
        self.assertIn('class="file-list"', first)
        self.assertIn("src/report_parser.py", first)
        self.assertIn('data-copy-summary="DS-001"', first)
        self.assertIn('data-add-comment="DS-001"', first)
        self.assertNotRegex(second, r"<details[^>]+\sopen(?:\s|>)")

        toolbar = first.index('<div class="card-toolbar"')
        self.assertGreater(toolbar, first.index('class="card-content"'))
        self.assertGreater(toolbar, first.index('class="file-list"'))
        self.assertLess(toolbar, first.index("</details>"))
        self.assertEqual(first.rstrip().rsplit("</div>", 1)[-1], "\n</details>")

    def test_rendering_the_same_report_twice_is_byte_identical(self) -> None:
        """The template decides every visual detail, so nothing varies per run.

        Any per-run value — a timestamp, a hash of an unordered set, an id from
        object identity — would make two renders of one report differ and turn
        an artifact diff into noise.
        """
        template = renderer.load_template()
        korean = parse_report(REPORT)
        english = parse_report(ENGLISH_REPORT)
        for label, kwargs in (
            ("single", {}),
            ("bilingual", {"alternate_report": english}),
            ("quiz", {}),
        ):
            document = parse_report(QUIZ_REPORT) if label == "quiz" else korean
            renders = {
                renderer.assemble_html(document, template, **kwargs) for _ in range(3)
            }
            with self.subTest(report=label):
                self.assertEqual(len(renders), 1)

    def test_heading_anchors_are_unique_when_titles_repeat(self) -> None:
        repeated = REPORT.replace("## Notes", "## Changes", 1)
        rendered = renderer.assemble_html(
            parse_report(repeated), renderer.load_template()
        )
        inventory = _MarkupInventory()
        inventory.feed(rendered)
        ids = [attrs["id"] for _, attrs in inventory.elements if "id" in attrs]

        self.assertEqual(len(ids), len(set(ids)))
        self.assertIn("changes", ids)
        self.assertIn("changes-2", ids)
        self.assertIn('href="#changes"', rendered)
        self.assertIn('href="#changes-2"', rendered)

    def test_unsafe_fence_info_never_becomes_an_html_attribute(self) -> None:
        malicious = REPORT.replace(
            "```python\n",
            '```python" onclick="alert(1)\n',
            1,
        )

        rendered = renderer.render_report_body(parse_report(malicious))
        inventory = _MarkupInventory()
        inventory.feed(rendered)
        code_attributes = [attrs for tag, attrs in inventory.elements if tag == "code"]

        self.assertFalse(any("onclick" in attrs for attrs in code_attributes))
        self.assertFalse(
            any("python" in (attrs.get("class") or "") for attrs in code_attributes)
        )


class HtmlAssemblyTests(unittest.TestCase):
    def test_assembles_bilingual_report_with_korean_default_and_language_toggle(
        self,
    ) -> None:
        korean = parse_report(REPORT)
        english = parse_report(ENGLISH_REPORT)

        rendered = renderer.assemble_html(
            korean,
            renderer.load_template(),
            alternate_report=english,
        )
        inventory = _MarkupInventory()
        inventory.feed(rendered)
        ids = [attrs["id"] for _, attrs in inventory.elements if "id" in attrs]

        self.assertIn('<html lang="ko" data-sidebar-collapsed="false">', rendered)
        self.assertIn('data-language-part="ko"', rendered)
        self.assertIn('data-language-part="en"', rendered)
        self.assertIn('data-set-lang="ko">한국어</button>', rendered)
        self.assertIn('data-set-lang="en">English</button>', rendered)
        self.assertIn("function setLanguage(", rendered)
        self.assertIn("applyTheme(currentTheme)", rendered)
        self.assertIn("setSidebarCollapsed(currentSidebarCollapsed, false)", rendered)
        self.assertEqual(len(ids), len(set(ids)))
        self.assertEqual(
            extract_json_script(rendered, "summary-data"),
            {
                "ko": [
                    {
                        "id": card.id,
                        "title": card.title,
                        "section": card.section,
                        "category": card.category,
                        "impact": card.impact,
                        "files": list(card.files),
                        "markdown": card.markdown,
                    }
                    for card in korean.cards
                ],
                "en": [
                    {
                        "id": card.id,
                        "title": card.title,
                        "section": card.section,
                        "category": card.category,
                        "impact": card.impact,
                        "files": list(card.files),
                        "markdown": card.markdown,
                    }
                    for card in english.cards
                ],
            },
        )
        self.assertEqual(
            extract_json_script(rendered, "raw-markdown"),
            {"ko": REPORT, "en": ENGLISH_REPORT},
        )

    def test_bilingual_report_rejects_drift_between_translation_contracts(
        self,
    ) -> None:
        korean = parse_report(REPORT)
        drifted = parse_report(
            replace_once(
                ENGLISH_REPORT,
                "**Files:** `src/report_parser.py`, `tests/test_report_parser.py`",
                "**Files:** `src/other.py`",
            )
        )

        with self.assertRaisesRegex(
            ReportFormatError,
            r"DS-001.*Files",
        ):
            renderer.assemble_html(
                korean,
                renderer.load_template(),
                alternate_report=drifted,
            )

    def test_bilingual_runtime_reads_context_from_active_metadata_part(self) -> None:
        rendered = renderer.assemble_html(
            parse_report(REPORT),
            renderer.load_template(),
            alternate_report=parse_report(ENGLISH_REPORT),
        )
        runtime = extract_runtime_script(rendered)

        self.assertIn("function activeMetadataRoot()", runtime)
        self.assertIn("const metadataRoot = activeMetadataRoot();", runtime)
        self.assertIn(
            'metadataRoot.querySelectorAll(".metadata-cell")',
            runtime,
        )
        self.assertIn(
            'metadataRoot.querySelector(".report-header")',
            runtime,
        )

    def test_generated_report_has_plain_product_copy_without_editorial_atlas_chrome(
        self,
    ) -> None:
        rendered = renderer.assemble_html(
            parse_report(REPORT), renderer.load_template()
        )

        for editorial_copy in (
            "Engineering change atlas",
            "Offline review plate",
            "Atlas index",
            "Portable review artifact",
            "Cobalt marks structure",
            "Amber marks impact",
        ):
            with self.subTest(editorial_copy=editorial_copy):
                self.assertNotIn(editorial_copy, rendered)

    def test_non_quiz_long_prose_and_section_titles_render_on_wrapping_surfaces(
        self,
    ) -> None:
        long_section = "OrdinarySectionIdentifier" * 24
        long_prose = "OrdinaryExecutiveSummaryProse" * 24
        report = replace_once(REPORT, "## Notes", f"## {long_section}")
        report = replace_once(
            report,
            "Generated footer outside the summary cards.",
            long_prose,
        )

        rendered = renderer.assemble_html(
            parse_report(report),
            renderer.load_template(),
        )

        self.assertGreaterEqual(rendered.count(long_section), 2)
        self.assertIn(f"<p>{long_prose}</p>", rendered)
        self.assertIn('class="section-index-item section-index-item--h2"', rendered)

    def test_generated_report_uses_shared_shell_with_escaped_sidebar_repository(
        self,
    ) -> None:
        report = REPORT.replace(
            "**Repository:** chann/skills",
            "**Repository:** repo<&>",
            1,
        )
        rendered = renderer.assemble_html(
            parse_report(report), renderer.load_template()
        )
        inventory = _MarkupInventory()
        inventory.feed(rendered)

        def has_class(tag_name: str, class_name: str) -> bool:
            return any(
                tag == tag_name
                and class_name in (attrs.get("class") or "").split()
                for tag, attrs in inventory.elements
            )

        html_attrs = next(attrs for tag, attrs in inventory.elements if tag == "html")
        navigation = next(
            attrs
            for tag, attrs in inventory.elements
            if tag == "nav" and attrs.get("id") == "report-sections"
        )
        headings = [
            attrs
            for tag, attrs in inventory.elements
            if tag == "h1" and attrs.get("id") == "report-title"
        ]

        self.assertEqual(html_attrs["data-sidebar-collapsed"], "false")
        for tag_name, class_name in (
            ("div", "layout"),
            ("div", "sidebar-header"),
            ("div", "sidebar-body"),
            ("div", "sidebar-footer"),
            ("div", "main-column"),
            ("div", "topbar"),
            ("div", "controls"),
            ("div", "control"),
        ):
            with self.subTest(tag=tag_name, class_name=class_name):
                self.assertTrue(has_class(tag_name, class_name))

        self.assertTrue(
            any(
                tag == "aside" and "data-sidebar" in attrs
                for tag, attrs in inventory.elements
            )
        )
        self.assertEqual(navigation.get("class"), "sidebar-nav")
        self.assertEqual(len(headings), 1)
        self.assertEqual(rendered.count('<div class="control">'), 3)
        self.assertRegex(
            rendered,
            r'<div class="control control--theme" role="group"[^>]*aria-label="Theme">',
        )
        for mode in ("auto", "light", "dark"):
            with self.subTest(mode=mode):
                self.assertRegex(
                    rendered,
                    rf'<button type="button" data-set-theme="{mode}"',
                )
        for hook in (
            "data-copy-feedback",
            "data-copy-report",
            "data-print-report",
        ):
            with self.subTest(hook=hook):
                self.assertRegex(
                    rendered,
                    rf'<div class="control">\s*<button[^>]*\b{hook}\b',
                )
        for hook in (
            "data-sidebar",
            "data-sidebar-toggle",
            "data-sidebar-expand",
        ):
            with self.subTest(hook=hook):
                self.assertIn(hook, rendered)
        for tag, attrs in inventory.elements:
            for name, value in attrs.items():
                if name in {"class", "id"} or name.startswith("data-"):
                    self.assertNotRegex(name, r"^data-atlas-")
                    self.assertNotRegex(value or "", r"\batlas-")

        self.assertIn('<div class="repo">repo&lt;&amp;&gt;</div>', rendered)
        self.assertNotIn("repo<&>", rendered)

    def test_sidebar_expand_is_outside_layout(self) -> None:
        rendered = renderer.assemble_html(
            parse_report(REPORT), renderer.load_template()
        )
        inventory = _MarkupInventory()
        inventory.feed(rendered)
        expand_index = next(
            index
            for index, (tag, attrs) in enumerate(inventory.elements)
            if tag == "button" and "data-sidebar-expand" in attrs
        )

        self.assertFalse(
            any(
                tag == "div" and "layout" in (attrs.get("class") or "").split()
                for tag, attrs in inventory.ancestors[expand_index]
            )
        )

    def test_report_main_contains_header_body_and_footer(self) -> None:
        rendered = renderer.assemble_html(
            parse_report(REPORT), renderer.load_template()
        )
        inventory = _MarkupInventory()
        inventory.feed(rendered)

        def element_index(tag_name: str, class_name: str | None = None) -> int:
            return next(
                index
                for index, (tag, attrs) in enumerate(inventory.elements)
                if tag == tag_name
                and (
                    class_name is None
                    or class_name in (attrs.get("class") or "").split()
                )
            )

        header_index = element_index("header", "report-header")
        body_heading_index = next(
            index
            for index, (tag, attrs) in enumerate(inventory.elements)
            if tag == "h2" and attrs.get("id") == "executive-summary"
        )
        footer_index = element_index("footer", "report-footer")

        for label, index in (
            ("metadata", header_index),
            ("report body", body_heading_index),
            ("footer", footer_index),
        ):
            with self.subTest(region=label):
                self.assertTrue(
                    any(
                        tag == "main" and attrs.get("id") == "report-main"
                        for tag, attrs in inventory.ancestors[index]
                    )
                )
        self.assertEqual(
            inventory.ancestors[body_heading_index][-1][1].get("id"),
            "report-main",
        )

    def test_card_header_grid_assigns_each_element_to_an_explicit_column(self) -> None:
        template = renderer.load_template()

        self.assertRegex(
            css_rule(template, ".card-summary"),
            r"grid-template-columns:\s*auto\s+minmax\(0,\s*1fr\)\s+auto\s*;",
        )
        self.assertRegex(
            css_rule(template, ".card-summary::before"), r"grid-column:\s*1\s*;"
        )
        self.assertRegex(css_rule(template, ".card-heading"), r"grid-column:\s*2\s*;")
        self.assertRegex(css_rule(template, ".card-badges"), r"grid-column:\s*3\s*;")

        mobile = template[template.index("@media (max-width: 860px)") :]
        self.assertRegex(
            css_rule(mobile, ".card-summary"),
            r"grid-template-columns:\s*auto\s+minmax\(0,\s*1fr\)\s*;",
        )
        mobile_badges = css_rule(mobile, ".card-badges")
        self.assertRegex(mobile_badges, r"grid-column:\s*2\s*;")
        self.assertRegex(mobile_badges, r"grid-row:\s*2\s*;")

    def test_sidebar_toggle_controls_a_stable_unique_navigation_target(self) -> None:
        heading_collision = REPORT.replace("## Notes", "## Report Sections", 1)
        rendered = renderer.assemble_html(
            parse_report(heading_collision),
            renderer.load_template(),
        )
        inventory = _MarkupInventory()
        inventory.feed(rendered)

        toggle = next(
            attrs
            for tag, attrs in inventory.elements
            if tag == "button" and "data-sidebar-toggle" in attrs
        )
        navigation = next(
            attrs
            for tag, attrs in inventory.elements
            if tag == "nav" and attrs.get("id") == "report-sections"
        )
        expand = next(
            attrs
            for tag, attrs in inventory.elements
            if tag == "button" and "data-sidebar-expand" in attrs
        )
        ids = [attrs["id"] for _, attrs in inventory.elements if "id" in attrs]

        self.assertEqual(navigation["id"], "report-sections")
        self.assertEqual(navigation["class"], "sidebar-nav")
        self.assertEqual(toggle["aria-controls"], "report-sections")
        self.assertEqual(toggle["aria-expanded"], "true")
        self.assertEqual(expand["aria-controls"], "report-sections")
        self.assertEqual(expand["aria-expanded"], "true")
        self.assertEqual(len(ids), len(set(ids)))
        self.assertIn("report-sections-2", ids)
        self.assertIn('href="#report-sections-2"', rendered)

    def test_assembles_offline_report_with_navigation_metadata_and_data(self) -> None:
        parsed = parse_report(REPORT)
        rendered = renderer.assemble_html(parsed, renderer.load_template())

        self.assertRegex(rendered, re.compile(r"(?i)^<!doctype html>"))
        self.assertIn('<html lang="ko" data-sidebar-collapsed="false">', rendered)
        self.assertIn(
            '<nav id="report-sections" class="sidebar-nav" aria-label="Report sections">',
            rendered,
        )
        self.assertIn('<main id="report-main"', rendered)
        self.assertIn('role="status"', rendered)
        self.assertIn('aria-live="polite"', rendered)
        self.assertIn('data-set-theme="auto"', rendered)
        self.assertIn('data-set-theme="light"', rendered)
        self.assertIn('data-set-theme="dark"', rendered)
        self.assertIn("data-sidebar-toggle", rendered)
        self.assertIn('data-default-theme="auto"', rendered)
        self.assertIn("@media print", rendered)
        self.assertRegex(rendered, r"@media\s*\([^)]*max-width")
        self.assertIn("@media (prefers-reduced-motion: reduce)", rendered)
        self.assertIn(":focus-visible", rendered)
        self.assertIn("<dt>Date</dt>", rendered)
        self.assertIn("<dd>2026-07-13</dd>", rendered)
        self.assertIn("<dt>Repository</dt>", rendered)
        self.assertIn("<dd>chann/skills</dd>", rendered)
        self.assertIn("<dt>Scope</dt>", rendered)
        self.assertIn("<dd><code>main..dev</code></dd>", rendered)
        self.assertIn('href="#executive-summary"', rendered)
        self.assertIn('href="#architecture"', rendered)
        self.assertIn('href="#tests"', rendered)
        self.assertNotRegex(rendered, re.compile(r"(?i)https?://"))
        self.assertNotRegex(
            rendered,
            re.compile(r"(?i)<(?:script|img)[^>]+\bsrc=|<link\b|@import\b|url\s*\("),
        )
        for placeholder in TEMPLATE_PLACEHOLDERS:
            with self.subTest(placeholder=placeholder):
                self.assertNotIn(placeholder, rendered)

        summary_data = extract_json_script(rendered, "summary-data")
        self.assertEqual(len(summary_data), 2)
        for actual, expected in zip(summary_data, parsed.cards, strict=True):
            self.assertEqual(
                actual,
                {
                    "id": expected.id,
                    "title": expected.title,
                    "section": expected.section,
                    "category": expected.category,
                    "impact": expected.impact,
                    "files": list(expected.files),
                    "markdown": expected.markdown,
                },
            )
        self.assertEqual(extract_json_script(rendered, "raw-markdown"), REPORT)
        self.assertEqual(
            extract_json_script(rendered, "comment-scope"),
            renderer.stable_comment_scope(parsed),
        )

    def test_report_values_are_escaped_in_text_attributes_and_json(self) -> None:
        malicious = REPORT.replace(
            "# main..dev Diff Summary",
            '# Atlas <img src=x onerror="alert(1)">',
            1,
        )
        malicious = malicious.replace(
            "**Repository:** chann/skills",
            '**Repository:** team "atlas" <repo>',
            1,
        )
        malicious = malicious.replace(
            "**Scope:** main..dev",
            '**Scope:** main..dev" data-pwned="yes',
            1,
        )
        malicious = malicious.replace(
            "**Language:** KO",
            '**Language:** ko" data-pwned="yes',
            1,
        )
        malicious = malicious.replace(
            "```python\n",
            '```python" onclick="alert(1)\n',
            1,
        )
        parsed = parse_report(malicious)

        rendered = renderer.assemble_html(parsed, renderer.load_template())
        inventory = _MarkupInventory()
        inventory.feed(rendered)

        html_attrs = next(attrs for tag, attrs in inventory.elements if tag == "html")
        header_attrs = next(
            attrs
            for tag, attrs in inventory.elements
            if tag == "header" and "report-header" in (attrs.get("class") or "")
        )
        self.assertEqual(
            html_attrs,
            {
                "lang": 'ko" data-pwned="yes',
                "data-sidebar-collapsed": "false",
            },
        )
        self.assertEqual(header_attrs["data-repository"], 'team "atlas" <repo>')
        self.assertEqual(header_attrs["data-scope"], 'main..dev" data-pwned="yes')
        self.assertNotIn("data-pwned", header_attrs)
        self.assertFalse(any(tag == "img" for tag, _ in inventory.elements))
        self.assertFalse(
            any(
                "onclick" in attrs or "onerror" in attrs
                for _, attrs in inventory.elements
            )
        )
        self.assertIn("&lt;img src=x onerror=&quot;alert(1)&quot;&gt;", rendered)
        self.assertEqual(extract_json_script(rendered, "raw-markdown"), malicious)

    def test_json_payloads_remain_single_scripts_for_hostile_report_text(self) -> None:
        hostile_text = "</script><script>breakout()</script> & \u2028 \u2029"
        hostile = REPORT.replace(
            "Generated footer outside the summary cards.",
            hostile_text,
            1,
        )

        rendered = renderer.assemble_html(
            parse_report(hostile), renderer.load_template()
        )
        inventory = _MarkupInventory()
        inventory.feed(rendered)
        scripts = [attrs for tag, attrs in inventory.elements if tag == "script"]

        self.assertEqual(len(scripts), 5)
        self.assertTrue(
            all(attrs.get("type") == "application/json" for attrs in scripts[:3])
        )
        self.assertIn("data-diff-summary-runtime", scripts[3])
        self.assertIn("data-diff-summary-highlight", scripts[4])
        self.assertTrue(all("src" not in attrs for attrs in scripts))
        self.assertEqual(extract_json_script(rendered, "raw-markdown"), hostile)
        self.assertNotIn(hostile_text, rendered)

    def test_placeholder_replacement_is_single_pass(self) -> None:
        mapping = {
            placeholder: f"value-for-{placeholder}"
            for placeholder in TEMPLATE_PLACEHOLDERS
        }
        mapping["__REPORT_BODY__"] = (
            "<p>User text keeps __REPORT_BODY__ and __REPORT_TITLE__ unchanged.</p>"
        )

        replaced = renderer.replace_placeholders(renderer.load_template(), mapping)

        self.assertIn(
            "User text keeps __REPORT_BODY__ and __REPORT_TITLE__ unchanged.",
            replaced,
        )
        self.assertNotIn("value-for-<p>", replaced)

    def test_assemble_preserves_placeholder_like_user_content(self) -> None:
        placeholder_report = REPORT.replace(
            "Generated footer outside the summary cards.",
            "Literal __REPORT_BODY__ and __REPORT_TITLE__ are review content.",
            1,
        )

        rendered = renderer.assemble_html(
            parse_report(placeholder_report),
            renderer.load_template(),
        )

        self.assertIn(
            "Literal __REPORT_BODY__ and __REPORT_TITLE__ are review content.",
            rendered,
        )
        self.assertEqual(
            extract_json_script(rendered, "raw-markdown"), placeholder_report
        )

    def test_missing_or_duplicate_template_placeholders_are_rejected(self) -> None:
        parsed = parse_report(REPORT)
        template = renderer.load_template()

        for placeholder in TEMPLATE_PLACEHOLDERS:
            with self.subTest(placeholder=placeholder, case="missing"):
                missing = template.replace(placeholder, "", 1)
                with self.assertRaisesRegex(
                    ReportFormatError,
                    rf"{re.escape(placeholder)}.*exactly once",
                ):
                    renderer.assemble_html(parsed, missing)

            with self.subTest(placeholder=placeholder, case="duplicate"):
                duplicate = template.replace(placeholder, placeholder * 2, 1)
                with self.assertRaisesRegex(
                    ReportFormatError,
                    rf"{re.escape(placeholder)}.*exactly once",
                ):
                    renderer.assemble_html(parsed, duplicate)

    def test_default_theme_accepts_only_auto_light_or_dark(self) -> None:
        parsed = parse_report(REPORT)
        template = renderer.load_template()

        for theme in ("auto", "light", "dark"):
            with self.subTest(theme=theme):
                rendered = renderer.assemble_html(parsed, template, default_theme=theme)
                self.assertIn(f'data-default-theme="{theme}"', rendered)

        for theme in ("", "paper", "AUTO", 'dark" onclick="alert(1)'):
            with self.subTest(theme=theme):
                with self.assertRaisesRegex(ReportFormatError, "default theme"):
                    renderer.assemble_html(parsed, template, default_theme=theme)


class ReportGenerationTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary_directory = tempfile.TemporaryDirectory()
        self.directory = Path(self.temporary_directory.name)
        self.input_path = self.directory / "change-summary.md"
        self.input_path.write_text(REPORT, encoding="utf-8")

    def tearDown(self) -> None:
        self.temporary_directory.cleanup()

    def test_generate_report_writes_default_sibling_and_returns_absolute_path(
        self,
    ) -> None:
        output_path = renderer.generate_report(self.input_path)

        self.assertEqual(output_path, self.input_path.with_suffix(".html").absolute())
        self.assertTrue(output_path.is_file())
        rendered = output_path.read_text(encoding="utf-8")
        self.assertRegex(rendered, re.compile(r"(?i)^<!doctype html>"))
        self.assertIn('data-default-theme="auto"', rendered)
        self.assertEqual(extract_json_script(rendered, "raw-markdown"), REPORT)

    def test_symlink_input_is_rejected_without_creating_a_sibling_output(self) -> None:
        source_directory = self.directory / "source"
        source_directory.mkdir()
        source_path = source_directory / "actual-summary.md"
        source_path.write_text(REPORT, encoding="utf-8")
        link_directory = self.directory / "links"
        link_directory.mkdir()
        input_link = link_directory / "linked-summary.md"
        input_link.symlink_to(source_path)

        expected = input_link.with_suffix(".html").absolute()
        with self.assertRaisesRegex(ReportFormatError, "input.*regular file"):
            renderer.generate_report(input_link)

        self.assertFalse(expected.exists())
        self.assertFalse(source_path.with_suffix(".html").exists())

    def test_symlinked_output_parent_is_rejected_without_writing_outside(self) -> None:
        outside = self.directory / "outside"
        outside.mkdir()
        linked_parent = self.directory / ".diff-summaries"
        linked_parent.symlink_to(outside, target_is_directory=True)
        output_path = linked_parent / "report.html"

        with self.assertRaisesRegex(ReportFormatError, "output parent.*symlink"):
            renderer.generate_report(self.input_path, output_path=output_path)

        self.assertFalse((outside / "report.html").exists())

    def test_symlinked_input_parent_is_rejected_without_copying_outside_markdown(
        self,
    ) -> None:
        outside = self.directory / "outside-source"
        outside.mkdir()
        (outside / "report.md").write_text(REPORT, encoding="utf-8")
        linked_parent = self.directory / "linked-source"
        linked_parent.symlink_to(outside, target_is_directory=True)
        output_path = self.directory / "safe-output.html"

        with self.assertRaisesRegex(ReportFormatError, "input parent.*symlink"):
            renderer.generate_report(
                linked_parent / "report.md",
                output_path=output_path,
            )

        self.assertFalse(output_path.exists())

    def test_markdown_stdin_mode_atomically_writes_both_report_files(self) -> None:
        artifact_root = self.directory / ".diff-summaries"
        markdown_path = artifact_root / "stdin-report.md"

        generated = renderer.generate_report_from_markdown(REPORT, markdown_path)

        self.assertEqual(generated, markdown_path.with_suffix(".html").absolute())
        self.assertEqual(markdown_path.read_text(encoding="utf-8"), REPORT)
        self.assertRegex(generated.read_text(encoding="utf-8"), r"(?i)^<!doctype html>")
        self.assertEqual(list(artifact_root.glob(".*.tmp")), [])

    def test_directory_mode_derives_collision_safe_artifact_paths(self) -> None:
        artifact_root = self.directory / ".diff-summaries"

        generated = renderer.generate_report_in_directory(REPORT, artifact_root)

        expected_stem = f"2026-07-13_{renderer.scope_tag('main..dev')}"
        self.assertEqual(
            generated, (artifact_root / f"{expected_stem}.html").absolute()
        )
        self.assertEqual(
            (artifact_root / f"{expected_stem}.md").read_text(encoding="utf-8"),
            REPORT,
        )
        self.assertTrue(generated.is_file())

    def test_bilingual_directory_mode_writes_two_markdown_files_and_shared_html(
        self,
    ) -> None:
        artifact_root = self.directory / ".diff-summaries"
        expected_stem = f"2026-07-13_{renderer.scope_tag('main..dev')}"

        generated = renderer.generate_bilingual_report_in_directory(
            REPORT,
            ENGLISH_REPORT,
            artifact_root,
        )

        self.assertEqual(
            generated, (artifact_root / f"{expected_stem}.html").absolute()
        )
        self.assertEqual(
            (artifact_root / f"{expected_stem}.md").read_text(encoding="utf-8"),
            REPORT,
        )
        self.assertEqual(
            (artifact_root / f"{expected_stem}.en.md").read_text(encoding="utf-8"),
            ENGLISH_REPORT,
        )
        self.assertEqual(
            extract_json_script(generated.read_text(encoding="utf-8"), "raw-markdown"),
            {"ko": REPORT, "en": ENGLISH_REPORT},
        )

    def test_directory_mode_rejects_invalid_dates_and_symlinked_parent(self) -> None:
        invalid_report = replace_once(
            REPORT,
            "**Date:** 2026-07-13",
            "**Date:** 2026-02-30",
        )
        artifact_root = self.directory / ".diff-summaries"
        with self.assertRaisesRegex(ReportFormatError, "real calendar date"):
            renderer.generate_report_in_directory(invalid_report, artifact_root)
        self.assertFalse(artifact_root.exists())

        outside = self.directory / "outside-derived"
        outside.mkdir()
        artifact_root.symlink_to(outside, target_is_directory=True)
        with self.assertRaisesRegex(ReportFormatError, "output parent.*symlink"):
            renderer.generate_report_in_directory(REPORT, artifact_root)
        self.assertEqual(list(outside.iterdir()), [])

    def test_explicit_symlink_output_replaces_link_without_touching_target(
        self,
    ) -> None:
        sentinel_path = self.directory / "sentinel.html"
        sentinel_path.write_text("sentinel output", encoding="utf-8")
        output_link = self.directory / "linked-output.html"
        output_link.symlink_to(sentinel_path)

        generated = renderer.generate_report(self.input_path, output_path=output_link)

        self.assertEqual(generated, output_link.absolute())
        self.assertFalse(output_link.is_symlink())
        self.assertRegex(
            output_link.read_text(encoding="utf-8"), r"(?i)^<!doctype html>"
        )
        self.assertEqual(sentinel_path.read_text(encoding="utf-8"), "sentinel output")

    def test_output_aliases_of_the_markdown_input_are_rejected(self) -> None:
        original = self.input_path.read_text(encoding="utf-8")
        symlink_alias = self.directory / "source-alias.html"
        symlink_alias.symlink_to(self.input_path)
        hardlink_alias = self.directory / "source-hardlink.html"
        hardlink_alias.hardlink_to(self.input_path)

        for alias in (symlink_alias, hardlink_alias):
            with self.subTest(alias=alias.name):
                with self.assertRaisesRegex(ReportFormatError, "output path.*input"):
                    renderer.generate_report(self.input_path, output_path=alias)

        self.assertTrue(symlink_alias.is_symlink())
        self.assertEqual(self.input_path.read_text(encoding="utf-8"), original)

    def test_generate_report_honors_explicit_output_and_each_theme(self) -> None:
        for theme in ("auto", "light", "dark"):
            with self.subTest(theme=theme):
                output_path = self.directory / theme / "atlas.html"
                output_path.parent.mkdir()

                generated = renderer.generate_report(
                    self.input_path,
                    output_path=output_path,
                    theme=theme,
                )

                self.assertEqual(generated, output_path.absolute())
                self.assertIn(
                    f'data-default-theme="{theme}"',
                    generated.read_text(encoding="utf-8"),
                )

    def test_generate_report_rejects_invalid_theme_before_writing(self) -> None:
        output_path = self.directory / "invalid-theme.html"

        with self.assertRaisesRegex(ReportFormatError, "default theme"):
            renderer.generate_report(
                self.input_path,
                output_path=output_path,
                theme="paper",
            )

        self.assertFalse(output_path.exists())
        self.assertEqual(list(self.directory.glob(".*.tmp")), [])

    def test_invalid_markdown_leaves_no_output_or_temporary_file(self) -> None:
        self.input_path.write_text(
            replace_once(REPORT, METADATA_LINES["Date"] + "\n", ""),
            encoding="utf-8",
        )
        output_path = self.directory / "invalid.html"

        with self.assertRaisesRegex(ReportFormatError, "Date"):
            renderer.generate_report(self.input_path, output_path=output_path)

        self.assertFalse(output_path.exists())
        self.assertEqual(list(self.directory.glob(".*.tmp")), [])

    def test_generate_report_refuses_to_overwrite_its_markdown_source(self) -> None:
        original = self.input_path.read_text(encoding="utf-8")

        with self.assertRaisesRegex(ReportFormatError, "output path.*input"):
            renderer.generate_report(self.input_path, output_path=self.input_path)

        self.assertEqual(self.input_path.read_text(encoding="utf-8"), original)
        self.assertEqual(list(self.directory.glob(".*.tmp")), [])

    def test_failed_atomic_replace_keeps_existing_output_and_removes_temp_file(
        self,
    ) -> None:
        output_path = self.directory / "existing.html"
        output_path.write_text("existing output", encoding="utf-8")

        with mock.patch.object(
            Path, "replace", side_effect=PermissionError("read only")
        ):
            with self.assertRaisesRegex(PermissionError, "read only"):
                renderer.generate_report(self.input_path, output_path=output_path)

        self.assertEqual(output_path.read_text(encoding="utf-8"), "existing output")
        self.assertEqual(list(self.directory.glob(".*.tmp")), [])

    def test_open_happens_only_after_complete_file_is_written(self) -> None:
        output_path = self.directory / "opened.html"
        calls: list[str] = []

        def assert_written(arguments, **kwargs):
            self.assertTrue(output_path.is_file())
            self.assertTrue(output_path.read_text(encoding="utf-8").endswith("\n"))
            self.assertEqual(arguments[0], "/usr/bin/open")
            self.assertNotIn("BROWSER", kwargs["env"])
            self.assertNotIn("PYTHONPATH", kwargs["env"])
            calls.append(arguments[1])
            return subprocess.CompletedProcess(arguments, 0, b"", b"")

        with mock.patch.object(renderer.subprocess, "run", side_effect=assert_written):
            generated = renderer.generate_report(
                self.input_path,
                output_path=output_path,
                open_report=True,
            )

        self.assertEqual(calls, [generated.as_uri()])

    def test_browser_open_failure_warns_but_keeps_generated_file(self) -> None:
        output_path = self.directory / "retained.html"
        standard_error = io.StringIO()

        failed = subprocess.CompletedProcess(
            ["/usr/bin/open"],
            1,
            b"",
            b"launcher failed",
        )
        with mock.patch.object(renderer.subprocess, "run", return_value=failed):
            with redirect_stderr(standard_error):
                generated = renderer.generate_report(
                    self.input_path,
                    output_path=output_path,
                    open_report=True,
                )

        self.assertEqual(generated, output_path.absolute())
        self.assertTrue(generated.is_file())
        self.assertIn("warning", standard_error.getvalue().lower())
        self.assertIn(str(generated), standard_error.getvalue())


class ReportCliTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary_directory = tempfile.TemporaryDirectory()
        self.directory = Path(self.temporary_directory.name)
        self.input_path = self.directory / "cli-summary.md"
        self.input_path.write_text(REPORT, encoding="utf-8")

    def tearDown(self) -> None:
        self.temporary_directory.cleanup()

    def run_cli(self, *arguments: str) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [sys.executable, str(SCRIPT_PATH), *arguments],
            cwd=ROOT,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=False,
        )

    def test_cli_generates_explicit_output_and_prints_report_facts(self) -> None:
        output_path = self.directory / "cli-output.html"

        result = self.run_cli(
            str(self.input_path),
            "--output",
            str(output_path),
            "--theme",
            "dark",
        )

        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stderr, "")
        self.assertTrue(output_path.is_file())
        self.assertIn("2 summary cards", result.stdout)
        self.assertIn("Language: ko", result.stdout)
        self.assertIn("Comment scope: chann/skills::main..dev::", result.stdout)
        self.assertIn(f"HTML: {output_path.absolute()}", result.stdout)
        self.assertIn(
            'data-default-theme="dark"',
            output_path.read_text(encoding="utf-8"),
        )

    def test_cli_markdown_stdin_mode_writes_source_and_html_atomically(self) -> None:
        artifact_root = self.directory / ".diff-summaries"
        markdown_path = artifact_root / "stdin-cli.md"

        result = subprocess.run(
            [
                sys.executable,
                str(SCRIPT_PATH),
                str(markdown_path),
                "--markdown-stdin",
            ],
            cwd=ROOT,
            input=REPORT,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=False,
        )

        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(markdown_path.read_text(encoding="utf-8"), REPORT)
        self.assertTrue(markdown_path.with_suffix(".html").is_file())
        self.assertIn(f"Markdown: {markdown_path.absolute()}", result.stdout)
        self.assertIn(
            f"HTML: {markdown_path.with_suffix('.html').absolute()}", result.stdout
        )

    def test_cli_output_directory_derives_and_reports_collision_safe_paths(
        self,
    ) -> None:
        artifact_root = self.directory / ".diff-summaries"
        expected_stem = f"2026-07-13_{renderer.scope_tag('main..dev')}"
        markdown_path = (artifact_root / f"{expected_stem}.md").absolute()
        html_path = (artifact_root / f"{expected_stem}.html").absolute()

        result = subprocess.run(
            [
                sys.executable,
                str(SCRIPT_PATH),
                "--markdown-stdin",
                "--output-directory",
                str(artifact_root),
            ],
            cwd=ROOT,
            input=REPORT,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=False,
        )

        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(markdown_path.read_text(encoding="utf-8"), REPORT)
        self.assertTrue(html_path.is_file())
        self.assertIn(f"Markdown: {markdown_path}", result.stdout)
        self.assertIn(f"HTML: {html_path}", result.stdout)

    def test_cli_bilingual_json_stdin_writes_aligned_language_artifacts(
        self,
    ) -> None:
        artifact_root = self.directory / ".diff-summaries"
        expected_stem = f"2026-07-13_{renderer.scope_tag('main..dev')}"
        korean_path = (artifact_root / f"{expected_stem}.md").absolute()
        english_path = (artifact_root / f"{expected_stem}.en.md").absolute()
        html_path = (artifact_root / f"{expected_stem}.html").absolute()

        result = subprocess.run(
            [
                sys.executable,
                str(SCRIPT_PATH),
                "--bilingual-json-stdin",
                "--output-directory",
                str(artifact_root),
            ],
            cwd=ROOT,
            input=json.dumps({"ko": REPORT, "en": ENGLISH_REPORT}),
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=False,
        )

        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(korean_path.read_text(encoding="utf-8"), REPORT)
        self.assertEqual(english_path.read_text(encoding="utf-8"), ENGLISH_REPORT)
        self.assertTrue(html_path.is_file())
        self.assertIn("Languages: ko,en", result.stdout)
        self.assertIn(f"Markdown (ko): {korean_path}", result.stdout)
        self.assertIn(f"Markdown (en): {english_path}", result.stdout)
        self.assertIn(f"HTML: {html_path}", result.stdout)

    def test_cli_output_directory_requires_stdin_and_excludes_explicit_paths(
        self,
    ) -> None:
        artifact_root = self.directory / ".diff-summaries"
        for arguments in (
            ("--output-directory", str(artifact_root)),
            (
                str(self.input_path),
                "--markdown-stdin",
                "--output-directory",
                str(artifact_root),
            ),
        ):
            with self.subTest(arguments=arguments):
                result = self.run_cli(*arguments)
                self.assertEqual(result.returncode, 1)
                self.assertIn("error:", result.stderr.lower())
                self.assertFalse(artifact_root.exists())

    def test_cli_invalid_markdown_is_nonzero_and_leaves_no_artifacts(self) -> None:
        self.input_path.write_text("# incomplete\n", encoding="utf-8")
        output_path = self.directory / "should-not-exist.html"

        result = self.run_cli(str(self.input_path), "-o", str(output_path))

        self.assertNotEqual(result.returncode, 0)
        self.assertEqual(result.stdout, "")
        self.assertRegex(result.stderr, r"(?i)error:.*Date")
        self.assertFalse(output_path.exists())
        self.assertEqual(list(self.directory.glob(".*.tmp")), [])

    def test_cli_missing_input_is_nonzero_and_does_not_create_default_output(
        self,
    ) -> None:
        missing_input = self.directory / "missing.md"

        result = self.run_cli(str(missing_input))

        self.assertNotEqual(result.returncode, 0)
        self.assertEqual(result.stdout, "")
        self.assertIn("error:", result.stderr.lower())
        self.assertIn(str(missing_input), result.stderr)
        self.assertFalse(missing_input.with_suffix(".html").exists())

    def test_cli_rejects_unknown_theme_without_writing(self) -> None:
        output_path = self.directory / "bad-theme.html"

        result = self.run_cli(
            str(self.input_path),
            "-o",
            str(output_path),
            "--theme",
            "paper",
        )

        self.assertEqual(result.returncode, 2)
        self.assertIn("invalid choice", result.stderr)
        self.assertFalse(output_path.exists())

    def test_cli_missing_output_directory_is_nonzero_and_leaves_no_temp(self) -> None:
        output_path = self.directory / "missing" / "report.html"

        result = self.run_cli(str(self.input_path), "-o", str(output_path))

        self.assertNotEqual(result.returncode, 0)
        self.assertEqual(result.stdout, "")
        self.assertIn("error:", result.stderr.lower())
        self.assertIn(str(output_path.parent), result.stderr)
        self.assertFalse(output_path.exists())
        self.assertFalse(output_path.parent.exists())

    def test_debug_controls_tracebacks_for_unexpected_failures(self) -> None:
        for arguments, expects_traceback in (
            ([str(self.input_path)], False),
            ([str(self.input_path), "--debug"], True),
        ):
            with self.subTest(debug=expects_traceback):
                standard_error = io.StringIO()
                with mock.patch.object(
                    renderer,
                    "_generate_report",
                    side_effect=RuntimeError("unexpected failure"),
                ):
                    with redirect_stderr(standard_error):
                        return_code = renderer.main(arguments)

                self.assertEqual(return_code, 1)
                self.assertEqual(
                    "Traceback" in standard_error.getvalue(), expects_traceback
                )
                self.assertEqual(
                    "RuntimeError" in standard_error.getvalue(), expects_traceback
                )
                self.assertIn("unexpected failure", standard_error.getvalue())


def quiz_block(rendered: str, quiz_id: str) -> str:
    marker = f'data-quiz-id="{quiz_id}"'
    marker_index = rendered.index(marker)
    start = rendered.rfind("<section", 0, marker_index)
    end = rendered.index("</section>", marker_index) + len("</section>")
    return rendered[start:end]


class QuizParsingTests(unittest.TestCase):
    def test_report_without_quiz_parses_with_empty_quiz_tuple(self) -> None:
        parsed = parse_report(REPORT)

        self.assertEqual(parsed.quiz, ())

    def test_parses_quiz_questions_options_answers_and_exact_slices(self) -> None:
        parsed = parse_report(QUIZ_REPORT)

        self.assertEqual(len(parsed.cards), 2)
        self.assertEqual(len(parsed.quiz), 2)
        first, second = parsed.quiz
        self.assertEqual(
            (first.id, first.title, first.answer_index),
            ("QZ-001", "What does separating the parser protect?", 1),
        )
        self.assertEqual(
            first.options,
            (
                "Rendering speed",
                "Input contract validation in `parse_report`",
                'Browser storage of <script>alert("quiz")</script>',
            ),
        )
        self.assertEqual(
            first.explanation,
            "`parse_report` validates the report contract in one place "
            "before rendering.",
        )
        self.assertEqual(
            (second.id, second.answer_index, second.options),
            ("QZ-002", 0, ("`main..dev`", "`main...dev`")),
        )

        first_start = QUIZ_REPORT.index("#### [QZ-001]")
        second_start = QUIZ_REPORT.index("#### [QZ-002]")
        self.assertEqual(first.markdown, QUIZ_REPORT[first_start:second_start])
        self.assertEqual(second.markdown, QUIZ_REPORT[second_start:])
        with self.assertRaises(FrozenInstanceError):
            first.answer_index = 0  # type: ignore[misc]

    def test_quiz_changes_do_not_change_the_stable_comment_scope(self) -> None:
        scope = renderer.stable_comment_scope(parse_report(REPORT))

        with_quiz = renderer.stable_comment_scope(parse_report(QUIZ_REPORT))
        edited_quiz = renderer.stable_comment_scope(
            parse_report(
                replace_once(
                    QUIZ_REPORT,
                    "Which scope stays byte-identical?",
                    "Which comparison scope is preserved?",
                )
            )
        )

        self.assertEqual(scope, with_quiz)
        self.assertEqual(scope, edited_quiz)

    def test_quiz_like_lines_inside_fenced_code_stay_inert(self) -> None:
        fenced = """```markdown
## Quiz
#### [QZ-999] Fake fenced question
- [x] fake fenced option
**Explanation:** fenced
```

"""
        report = replace_once(
            QUIZ_REPORT,
            "짧은 근거 문단이 질문 앞에 올 수 있습니다.",
            fenced + "짧은 근거 문단이 질문 앞에 올 수 있습니다.",
        )

        parsed = parse_report(report)

        self.assertEqual([question.id for question in parsed.quiz], ["QZ-001", "QZ-002"])
        self.assertEqual(len(parsed.quiz[0].options), 3)
        self.assertIn("#### [QZ-999] Fake fenced question", parsed.quiz[0].markdown)

    def test_rejects_malformed_quiz_question_heading(self) -> None:
        report = replace_once(QUIZ_REPORT, "#### [QZ-001]", "#### [QZ-01]")
        heading_line = source_line_number(report, "#### [QZ-01]")

        with self.assertRaisesRegex(
            ReportFormatError,
            rf"malformed quiz question heading at line {heading_line}.*QZ-01",
        ):
            parse_report(report)

    def test_rejects_quiz_content_before_the_first_question(self) -> None:
        malformed = replace_once(
            QUIZ_REPORT,
            "#### [QZ-001]",
            "####[QZ-001] Missing required heading space",
        )
        malformed_line = source_line_number(
            malformed, "####[QZ-001] Missing required heading space"
        )
        with self.assertRaisesRegex(
            ReportFormatError,
            rf"Quiz section.*content before.*line {malformed_line}",
        ):
            parse_report(malformed)

        stray_option = replace_once(
            QUIZ_REPORT,
            "#### [QZ-001]",
            "- [x] Stray answer marker\n\n#### [QZ-001]",
        )
        stray_line = source_line_number(stray_option, "- [x] Stray answer marker")
        with self.assertRaisesRegex(
            ReportFormatError,
            rf"Quiz section.*content before.*line {stray_line}",
        ):
            parse_report(stray_option)

    def test_rejects_plain_or_fenced_content_before_the_first_question(self) -> None:
        for preamble in (
            "Introductory quiz prose is not allowed here.",
            "```text\nnot a question\n```",
        ):
            report = replace_once(
                QUIZ_REPORT,
                "#### [QZ-001]",
                f"{preamble}\n\n#### [QZ-001]",
            )
            preamble_line = source_line_number(report, preamble.splitlines()[0])
            with self.subTest(preamble=preamble), self.assertRaisesRegex(
                ReportFormatError,
                rf"Quiz section.*content before.*line {preamble_line}",
            ):
                parse_report(report)

    def test_rejects_an_empty_quiz_section(self) -> None:
        report = REPORT + "\n## Quiz\n"
        quiz_line = source_line_number(report, "## Quiz")

        with self.assertRaisesRegex(
            ReportFormatError,
            rf"Quiz section at line {quiz_line}.*at least one question",
        ):
            parse_report(report)

    def test_rejects_quiz_before_a_later_level_two_section(self) -> None:
        quiz = QUIZ_REPORT[len(REPORT) + 1 :]
        report = replace_once(
            REPORT,
            "## Notes",
            f"{quiz}\n## Notes",
        )
        quiz_line = source_line_number(report, "## Quiz")
        later_line = source_line_number(report, "## Notes")

        with self.assertRaisesRegex(
            ReportFormatError,
            rf"Quiz section at line {quiz_line}.*final level-two.*line {later_line}",
        ):
            parse_report(report)

    def test_rejects_over_indented_quiz_question_heading(self) -> None:
        report = replace_once(QUIZ_REPORT, "#### [QZ-002]", "    #### [QZ-002]")
        heading_line = source_line_number(report, "    #### [QZ-002]")

        with self.assertRaisesRegex(
            ReportFormatError,
            rf"over-indented.*line {heading_line}.*QZ-002",
        ):
            parse_report(report)

    def test_rejects_wrong_level_or_malformed_later_question_headings(self) -> None:
        for malformed_heading in (
            "##### [QZ-002] Wrong level",
            "####[QZ-002] Missing heading space",
            "    #### [QZ-02] Over-indented and malformed",
        ):
            report = replace_once(
                QUIZ_REPORT,
                "#### [QZ-002] Which scope stays byte-identical?",
                malformed_heading,
            )
            line = source_line_number(report, malformed_heading)
            with self.subTest(heading=malformed_heading), self.assertRaisesRegex(
                ReportFormatError,
                rf"(?:malformed|over-indented).*line {line}",
            ):
                parse_report(report)

    def test_rejects_summary_cards_inside_the_quiz_section(self) -> None:
        card = """#### [DS-003] Card in the quiz section

**Category:** Test
**Impact:** Low
**Files:** `tests/test_report_parser.py`

Invalid placement.

"""
        report = replace_once(QUIZ_REPORT, "#### [QZ-001]", card + "#### [QZ-001]")

        with self.assertRaisesRegex(
            ReportFormatError, r"summary card DS-003.*inside the Quiz section"
        ):
            parse_report(report)

    def test_rejects_quiz_questions_outside_the_quiz_section(self) -> None:
        stray = """#### [QZ-001] Stray question?

- [x] Yes
- [ ] No

**Explanation:** Stray.

"""
        report = replace_once(REPORT, "## Notes", stray + "## Notes")

        with self.assertRaisesRegex(
            ReportFormatError,
            r"quiz question QZ-001.*under the level-two Quiz section",
        ):
            parse_report(report)

    def test_rejects_level_three_sections_inside_the_quiz(self) -> None:
        report = replace_once(
            QUIZ_REPORT,
            "#### [QZ-002]",
            "### Grouped questions\n\n#### [QZ-002]",
        )

        with self.assertRaisesRegex(
            ReportFormatError, r"Quiz section must not contain level-three"
        ):
            parse_report(report)

    def test_rejects_duplicate_quiz_sections(self) -> None:
        report = QUIZ_REPORT + "\n## Quiz\n"
        duplicate_line = report.count("\n", 0, report.rindex("## Quiz")) + 1

        with self.assertRaisesRegex(
            ReportFormatError, rf"duplicate Quiz section.*line {duplicate_line}"
        ):
            parse_report(report)

    def test_rejects_duplicate_and_non_sequential_quiz_ids(self) -> None:
        duplicate = replace_once(QUIZ_REPORT, "#### [QZ-002]", "#### [QZ-001]")
        duplicate_line = source_line_number(
            duplicate, "#### [QZ-001] Which scope stays byte-identical?"
        )
        with self.assertRaisesRegex(
            ReportFormatError,
            rf"duplicate quiz question ID.*QZ-001.*heading line {duplicate_line}",
        ):
            parse_report(duplicate)

        gap = replace_once(QUIZ_REPORT, "#### [QZ-002]", "#### [QZ-003]")
        gap_line = source_line_number(gap, "#### [QZ-003]")
        with self.assertRaisesRegex(
            ReportFormatError,
            rf"QZ-003.*heading line {gap_line}.*expected QZ-002",
        ):
            parse_report(gap)

    def test_rejects_missing_options_and_option_count_bounds(self) -> None:
        two_options = "- [x] `main..dev`\n- [ ] `main...dev`"
        missing = replace_once(QUIZ_REPORT, two_options + "\n\n", "")
        with self.assertRaisesRegex(
            ReportFormatError, r"QZ-002.*missing its options list"
        ):
            parse_report(missing)

        single = replace_once(QUIZ_REPORT, two_options, "- [x] `main..dev`")
        with self.assertRaisesRegex(ReportFormatError, r"QZ-002.*at least 2 options"):
            parse_report(single)

        seven = replace_once(
            QUIZ_REPORT,
            two_options,
            "- [x] `main..dev`\n"
            + "\n".join(f"- [ ] option {index}" for index in range(6)),
        )
        with self.assertRaisesRegex(ReportFormatError, r"QZ-002.*at most 6 options"):
            parse_report(seven)

    def test_rejects_bare_or_over_indented_option_like_lines(self) -> None:
        for malformed_option in (
            "-",
            "    - [x] Hidden extra correct-looking option",
        ):
            report = replace_once(
                QUIZ_REPORT,
                "- [ ] Rendering speed",
                f"{malformed_option}\n- [ ] Rendering speed",
            )
            line = source_line_number(
                report, f"{malformed_option}\n- [ ] Rendering speed"
            )
            with self.subTest(option=malformed_option), self.assertRaisesRegex(
                ReportFormatError,
                rf"QZ-001.*malformed quiz option at line {line}",
            ):
                parse_report(report)

    def test_rejects_zero_or_multiple_correct_marks(self) -> None:
        none_correct = replace_once(QUIZ_REPORT, "- [x] `main..dev`", "- [ ] `main..dev`")
        with self.assertRaisesRegex(
            ReportFormatError, r"QZ-002.*exactly one correct option"
        ):
            parse_report(none_correct)

        both_correct = replace_once(
            QUIZ_REPORT, "- [ ] `main...dev`", "- [x] `main...dev`"
        )
        with self.assertRaisesRegex(
            ReportFormatError, r"QZ-002.*exactly one correct option"
        ):
            parse_report(both_correct)

    def test_rejects_each_malformed_option_line(self) -> None:
        for malformed in (
            "- [X] `main...dev`",
            "* [ ] `main...dev`",
            "- `main...dev`",
            "- [] `main...dev`",
        ):
            with self.subTest(malformed=malformed):
                report = replace_once(QUIZ_REPORT, "- [ ] `main...dev`", malformed)
                line = source_line_number(report, malformed)
                with self.assertRaisesRegex(
                    ReportFormatError,
                    rf"QZ-002.*malformed quiz option at line {line}",
                ):
                    parse_report(report)

    def test_rejects_duplicate_option_text(self) -> None:
        report = replace_once(QUIZ_REPORT, "- [ ] `main...dev`", "- [ ] `main..dev`")

        with self.assertRaisesRegex(ReportFormatError, r"QZ-002.*duplicate option"):
            parse_report(report)

    def test_rejects_visually_empty_or_render_duplicate_option_text(self) -> None:
        empty = replace_once(QUIZ_REPORT, "- [ ] `main...dev`", "- [ ] ** **")
        empty_line = source_line_number(empty, "- [ ] ** **")
        with self.assertRaisesRegex(
            ReportFormatError,
            rf"QZ-002.*empty option text.*line {empty_line}",
        ):
            parse_report(empty)

        duplicate = replace_once(
            QUIZ_REPORT,
            "- [ ] `main...dev`",
            "- [ ] **main..dev**",
        )
        with self.assertRaisesRegex(
            ReportFormatError, r"QZ-002.*duplicate option text"
        ):
            parse_report(duplicate)

    def test_rejects_split_options_lists(self) -> None:
        report = replace_once(
            QUIZ_REPORT,
            "- [x] `main..dev`\n- [ ] `main...dev`",
            "- [x] `main..dev`\n\nInterrupting prose.\n\n- [ ] `main...dev`",
        )

        with self.assertRaisesRegex(
            ReportFormatError, r"QZ-002.*one contiguous options list"
        ):
            parse_report(report)

    def test_rejects_missing_duplicate_empty_or_early_explanation(self) -> None:
        explanation = "**Explanation:** The requested two-dot scope is preserved exactly."
        missing = replace_once(QUIZ_REPORT, explanation + "\n", "")
        with self.assertRaisesRegex(
            ReportFormatError, r"QZ-002.*missing.*Explanation"
        ):
            parse_report(missing)

        duplicate = replace_once(
            QUIZ_REPORT, explanation, f"{explanation}\n{explanation}"
        )
        with self.assertRaisesRegex(
            ReportFormatError, r"QZ-002.*duplicate.*Explanation"
        ):
            parse_report(duplicate)

        empty = replace_once(QUIZ_REPORT, explanation, "**Explanation:**   ")
        with self.assertRaisesRegex(ReportFormatError, r"QZ-002.*empty Explanation"):
            parse_report(empty)

        visually_empty = replace_once(
            QUIZ_REPORT,
            "**Explanation:** The requested two-dot scope is preserved exactly.",
            "**Explanation:** ** **",
        )
        with self.assertRaisesRegex(
            ReportFormatError, r"QZ-002.*empty Explanation"
        ):
            parse_report(visually_empty)

        early = replace_once(QUIZ_REPORT, explanation + "\n", "")
        early = replace_once(
            early,
            "- [x] `main..dev`",
            f"{explanation}\n\n- [x] `main..dev`",
        )
        with self.assertRaisesRegex(
            ReportFormatError, r"QZ-002.*Explanation.*after.*options"
        ):
            parse_report(early)

    def test_rejects_content_after_the_explanation(self) -> None:
        report = QUIZ_REPORT + "\nTrailing prose after the explanation.\n"

        with self.assertRaisesRegex(
            ReportFormatError, r"QZ-002.*after the Explanation"
        ):
            parse_report(report)


class QuizRenderingTests(unittest.TestCase):
    def test_report_without_quiz_renders_no_quiz_markup(self) -> None:
        body = renderer.render_report_body(parse_report(REPORT))

        self.assertNotIn("quiz-question", body)
        self.assertNotIn("data-quiz-option", body)

    def test_renders_interactive_quiz_blocks_with_marked_answer(self) -> None:
        body = renderer.render_report_body(parse_report(QUIZ_REPORT))
        first = quiz_block(body, "QZ-001")
        second = quiz_block(body, "QZ-002")

        self.assertIn('<h2 id="quiz">Quiz</h2>', body)
        self.assertIn('<section class="quiz-question" data-quiz-id="QZ-001"', body)
        for index in range(3):
            self.assertIn(f'data-quiz-option="{index}"', first)
        self.assertEqual(first.count("data-quiz-correct"), 1)
        self.assertEqual(second.count("data-quiz-correct"), 1)
        self.assertLess(
            first.index('data-quiz-option="1"'),
            first.index("data-quiz-correct"),
        )
        self.assertIn("짧은 근거 문단이 질문 앞에 올 수 있습니다.", first)
        self.assertLess(first.index("짧은 근거 문단"), first.index("quiz-options"))
        self.assertIn('data-quiz-status', first)
        self.assertIn("hidden", first[first.index("data-quiz-status") - 80 :])
        self.assertIn('<details class="quiz-explanation">', first)
        self.assertIn("Explanation", first)
        self.assertIn("<code>parse_report</code>", first)
        self.assertIn("<code>main..dev</code>", second)

    def test_quiz_option_and_explanation_text_is_escaped(self) -> None:
        body = renderer.render_report_body(parse_report(QUIZ_REPORT))
        first = quiz_block(body, "QZ-001")

        self.assertIn("&lt;script&gt;alert(&quot;quiz&quot;)&lt;/script&gt;", first)
        self.assertNotIn('<script>alert("quiz")</script>', first)

    def test_quiz_buttons_are_typed_and_labeled(self) -> None:
        rendered = renderer.assemble_html(
            parse_report(QUIZ_REPORT), renderer.load_template()
        )
        inventory = _MarkupInventory()
        inventory.feed(rendered)
        option_buttons = [
            attrs
            for tag, attrs in inventory.elements
            if tag == "button" and "data-quiz-option" in attrs
        ]

        self.assertEqual(len(option_buttons), 5)
        self.assertTrue(all(attrs.get("type") == "button" for attrs in option_buttons))
        self.assertTrue(all(attrs.get("aria-label") for attrs in option_buttons))
        self.assertTrue(
            all(attrs.get("data-quiz-id") for attrs in option_buttons)
        )
        self.assertTrue(
            all(attrs.get("aria-pressed") == "false" for attrs in option_buttons)
        )
        rendered_labels = {
            attrs.get("data-quiz-label"): attrs.get("aria-label")
            for attrs in option_buttons
        }
        for option_text in (
            "Rendering speed",
            "Input contract validation in parse_report",
            "main..dev",
        ):
            with self.subTest(option=option_text):
                self.assertIn(option_text, rendered_labels)
                self.assertIn(option_text, rendered_labels[option_text])
        self.assertNotIn("`", " ".join(rendered_labels))
        self.assertNotIn("**", " ".join(rendered_labels))

    def test_quiz_report_stays_offline_with_unchanged_payload_scripts(self) -> None:
        rendered = renderer.assemble_html(
            parse_report(QUIZ_REPORT), renderer.load_template()
        )
        inventory = _MarkupInventory()
        inventory.feed(rendered)
        scripts = [attrs for tag, attrs in inventory.elements if tag == "script"]

        self.assertEqual(len(scripts), 5)
        self.assertIn('href="#quiz"', rendered)
        self.assertNotRegex(rendered, re.compile(r"(?i)https?://"))
        self.assertNotRegex(
            rendered,
            re.compile(r"(?i)<(?:script|img)[^>]+\bsrc=|<link\b|@import\b|url\s*\("),
        )
        self.assertEqual(extract_json_script(rendered, "raw-markdown"), QUIZ_REPORT)

    def test_template_prints_quiz_as_an_answer_key(self) -> None:
        template = renderer.load_template()
        print_styles = template[template.index("@media print") :]

        self.assertIn(".quiz-option", print_styles)
        self.assertIn(".quiz-explanation", print_styles)
        self.assertIn('window.addEventListener("beforeprint"', template)
        self.assertIn('window.addEventListener("afterprint"', template)


class QuizRuntimeTests(unittest.TestCase):
    def setUp(self) -> None:
        self.rendered = renderer.assemble_html(
            parse_report(QUIZ_REPORT), renderer.load_template()
        )
        self.runtime = extract_runtime_script(self.rendered)

    def quiz_scenario(self, **overrides) -> dict:
        scenario = {
            "defaultTheme": "auto",
            "summaryData": [
                {
                    "id": "DS-001",
                    "title": "Runtime contract",
                    "markdown": "#### [DS-001] Runtime contract\n",
                }
            ],
            "rawMarkdown": QUIZ_REPORT,
            "commentScope": "chann/skills::main..dev::runtime",
            "domCardIds": ["DS-001"],
            "storage": {},
            "quizQuestions": [
                {
                    "id": "QZ-001",
                    "options": 3,
                    "correct": 1,
                    "labels": [
                        "Rendering speed",
                        "Input contract validation in parse_report",
                        "Browser storage",
                    ],
                }
            ],
            "action": "quiz-answer",
            "quizAnswerId": "QZ-001",
        }
        scenario.update(overrides)
        return run_runtime_harness(self.runtime, scenario)

    def test_correct_answer_marks_disables_and_reveals_the_explanation(self) -> None:
        result = self.quiz_scenario(quizAnswerIndex=1)

        question = result["quiz"][0]
        self.assertEqual(result["quizAnswerResults"], [True])
        self.assertEqual(question["answered"], "true")
        self.assertFalse(question["statusHidden"])
        self.assertEqual(question["statusTone"], "success")
        self.assertTrue(question["statusText"])
        self.assertTrue(question["explanationOpen"])
        self.assertTrue(all(option["disabled"] for option in question["options"]))
        self.assertIn("is-selected", question["options"][1]["classes"])
        self.assertIn("is-correct", question["options"][1]["classes"])
        self.assertNotIn("is-incorrect", question["options"][1]["classes"])
        self.assertEqual(question["options"][1]["ariaPressed"], "true")
        self.assertTrue(
            all(
                option["ariaPressed"] == ("true" if index == 1 else "false")
                for index, option in enumerate(question["options"])
            )
        )

    def test_incorrect_answer_highlights_the_correct_option_once(self) -> None:
        result = self.quiz_scenario(quizAnswerIndex=0, quizRepeatIndex=1)

        question = result["quiz"][0]
        self.assertEqual(result["quizAnswerResults"], [False, False])
        self.assertEqual(question["statusTone"], "error")
        self.assertTrue(question["explanationOpen"])
        self.assertIn("is-selected", question["options"][0]["classes"])
        self.assertIn("is-incorrect", question["options"][0]["classes"])
        self.assertIn("is-correct", question["options"][1]["classes"])
        self.assertNotIn("is-selected", question["options"][1]["classes"])
        self.assertTrue(all(option["disabled"] for option in question["options"]))
        self.assertEqual(question["options"][0]["ariaPressed"], "true")
        self.assertIn("Input contract validation in parse_report", question["statusText"])
        self.assertIn(
            "Input contract validation in parse_report",
            question["options"][1]["ariaLabel"],
        )
        self.assertRegex(question["options"][1]["ariaLabel"], r"(?i)correct answer")

    def test_unknown_question_or_option_answers_nothing(self) -> None:
        result = self.quiz_scenario(quizAnswerId="QZ-404", quizAnswerIndex=0)

        question = result["quiz"][0]
        self.assertEqual(result["quizAnswerResults"], [False])
        self.assertIsNone(question["answered"])
        self.assertTrue(question["statusHidden"])
        self.assertFalse(question["explanationOpen"])

        out_of_range = self.quiz_scenario(quizAnswerIndex=9)
        self.assertEqual(out_of_range["quizAnswerResults"], [False])
        self.assertIsNone(out_of_range["quiz"][0]["answered"])

    def test_print_expands_explanations_then_restores_each_open_state(self) -> None:
        result = self.quiz_scenario(
            action="quiz-print",
            quizQuestions=[
                {"id": "QZ-001", "options": 3, "correct": 1},
                {
                    "id": "QZ-002",
                    "options": 2,
                    "correct": 0,
                    "explanationOpen": True,
                },
            ],
        )

        self.assertEqual(
            result["quizPrintStates"],
            {
                "beforePrint": [False, True],
                "duringPrint": [True, True],
                "afterPrint": [False, True],
            },
        )


class MarkdownOnlyCliTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary_directory = tempfile.TemporaryDirectory()
        self.directory = Path(self.temporary_directory.name)
        self.artifact_root = self.directory / ".diff-summaries"

    def tearDown(self) -> None:
        self.temporary_directory.cleanup()

    def run_cli(self, *arguments: str, stdin: str | None = None):
        return subprocess.run(
            [sys.executable, str(SCRIPT_PATH), *arguments],
            cwd=ROOT,
            input=stdin,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=False,
        )

    def test_markdown_only_writes_only_the_markdown_artifact(self) -> None:
        expected_stem = f"2026-07-13_{renderer.scope_tag('main..dev')}"

        result = self.run_cli(
            "--markdown-stdin",
            "--output-directory",
            str(self.artifact_root),
            "--markdown-only",
            stdin=REPORT,
        )

        markdown_path = (self.artifact_root / f"{expected_stem}.md").absolute()
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(markdown_path.read_text(encoding="utf-8"), REPORT)
        self.assertFalse((self.artifact_root / f"{expected_stem}.html").exists())
        self.assertEqual(
            sorted(path.name for path in self.artifact_root.iterdir()),
            [f"{expected_stem}.md"],
        )
        self.assertIn("2 summary cards", result.stdout)
        self.assertIn(f"Markdown: {markdown_path}", result.stdout)
        self.assertNotIn("HTML:", result.stdout)

    def test_markdown_only_still_validates_the_report_contract(self) -> None:
        invalid = replace_once(REPORT, METADATA_LINES["Date"] + "\n", "")

        result = self.run_cli(
            "--markdown-stdin",
            "--output-directory",
            str(self.artifact_root),
            "--markdown-only",
            stdin=invalid,
        )

        self.assertEqual(result.returncode, 1)
        self.assertRegex(result.stderr, r"(?i)error:.*Date")
        self.assertFalse(self.artifact_root.exists())

    def test_markdown_only_rejects_incompatible_argument_shapes(self) -> None:
        input_path = self.directory / "cli-summary.md"
        input_path.write_text(REPORT, encoding="utf-8")
        cases = (
            ((str(input_path), "--markdown-only"), "--markdown-only"),
            (
                (str(input_path), "--markdown-stdin", "--markdown-only"),
                "--markdown-only",
            ),
            (
                (
                    "--markdown-stdin",
                    "--output-directory",
                    str(self.artifact_root),
                    "--markdown-only",
                    "--open",
                ),
                "--markdown-only",
            ),
            (
                (
                    "--markdown-stdin",
                    "--output-directory",
                    str(self.artifact_root),
                    "--markdown-only",
                    "--output",
                    str(self.directory / "forbidden.html"),
                ),
                "--output-directory",
            ),
            (
                (
                    str(input_path),
                    "--markdown-stdin",
                    "--output-directory",
                    str(self.artifact_root),
                    "--markdown-only",
                ),
                "--output-directory",
            ),
        )
        for arguments, expected_error in cases:
            with self.subTest(arguments=arguments):
                result = self.run_cli(*arguments, stdin=REPORT)
                self.assertEqual(result.returncode, 1)
                self.assertIn(expected_error, result.stderr)
                self.assertFalse(self.artifact_root.exists())

    def test_quiz_question_count_is_reported_in_generation_output(self) -> None:
        with_quiz = self.run_cli(
            "--markdown-stdin",
            "--output-directory",
            str(self.artifact_root),
            stdin=QUIZ_REPORT,
        )
        without_quiz = self.run_cli(
            "--markdown-stdin",
            "--output-directory",
            str(self.artifact_root),
            "--markdown-only",
            stdin=REPORT,
        )

        self.assertEqual(with_quiz.returncode, 0, with_quiz.stderr)
        self.assertIn("Quiz questions: 2", with_quiz.stdout)
        self.assertEqual(without_quiz.returncode, 0, without_quiz.stderr)
        self.assertNotIn("Quiz questions", without_quiz.stdout)

    def test_single_quiz_question_uses_the_stable_plural_output_key(self) -> None:
        one_question_report = QUIZ_REPORT[: QUIZ_REPORT.index("#### [QZ-002]")]

        result = self.run_cli(
            "--markdown-stdin",
            "--output-directory",
            str(self.artifact_root),
            "--markdown-only",
            stdin=one_question_report,
        )

        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("Quiz questions: 1", result.stdout)
        self.assertNotIn("Quiz question: 1", result.stdout)


class SkillRendererIntegrationTests(unittest.TestCase):
    def test_documented_report_template_is_parseable_and_renderable(self) -> None:
        skill_text = (
            ROOT / "code-review" / "skills" / "diff-summary" / "SKILL.md"
        ).read_text(encoding="utf-8")
        match = re.search(
            r"Use this top-level structure:\n\n```markdown\n(?P<report>.*?)\n```",
            skill_text,
            re.DOTALL,
        )
        if match is None:
            self.fail("SKILL.md must include its canonical Markdown template")

        documented_report = match.group("report") + "\n"
        parsed = parse_report(documented_report)
        rendered = renderer.assemble_html(parsed, renderer.load_template())

        self.assertEqual([card.id for card in parsed.cards], ["DS-001"])
        self.assertEqual(parsed.cards[0].category, "Architecture")
        self.assertEqual(
            extract_json_script(rendered, "raw-markdown"), documented_report
        )

    def test_documented_quiz_example_is_parseable_and_renderable(self) -> None:
        main_skill_text = (
            ROOT / "code-review" / "skills" / "diff-summary" / "SKILL.md"
        ).read_text(encoding="utf-8")
        quiz_skill_text = (
            ROOT / "code-review" / "skills" / "diff-summary-quiz" / "SKILL.md"
        ).read_text(encoding="utf-8")
        report_match = re.search(
            r"Use this top-level structure:\n\n```markdown\n(?P<report>.*?)\n```",
            main_skill_text,
            re.DOTALL,
        )
        quiz_match = re.search(
            r"```markdown\n(?P<quiz>## Quiz\n.*?)\n```",
            quiz_skill_text,
            re.DOTALL,
        )
        if report_match is None or quiz_match is None:
            self.fail(
                "both the canonical report template and the documented quiz "
                "example are required"
            )

        combined = report_match.group("report") + "\n\n" + quiz_match.group("quiz") + "\n"
        parsed = parse_report(combined)
        rendered = renderer.assemble_html(parsed, renderer.load_template())

        self.assertGreaterEqual(len(parsed.quiz), 1)
        self.assertEqual(parsed.quiz[0].id, "QZ-001")
        self.assertIn('data-quiz-id="QZ-001"', rendered)


class InteractionRuntimeContractTests(unittest.TestCase):
    def setUp(self) -> None:
        self.rendered = renderer.assemble_html(
            parse_report(REPORT), renderer.load_template()
        )
        self.runtime = extract_runtime_script(self.rendered)

    def runtime_scenario(self, **overrides) -> dict:
        scenario = {
            "defaultTheme": "auto",
            "summaryData": [
                {
                    "id": "DS-001",
                    "title": "Runtime contract",
                    "markdown": "#### [DS-001] Runtime contract\n",
                }
            ],
            "rawMarkdown": REPORT,
            "commentScope": "chann/skills::main..dev::runtime",
            "domCardIds": ["DS-001"],
            "storage": {},
        }
        scenario.update(overrides)
        return run_runtime_harness(self.runtime, scenario)

    def test_inline_runtime_follows_all_json_payloads_and_has_valid_javascript(
        self,
    ) -> None:
        payload_positions = [
            self.rendered.index(f'<script id="{element_id}" type="application/json">')
            for element_id in ("summary-data", "raw-markdown", "comment-scope")
        ]
        runtime_position = self.rendered.index("<script data-diff-summary-runtime>")

        self.assertEqual(payload_positions, sorted(payload_positions))
        self.assertGreater(runtime_position, payload_positions[-1])
        self.assertNotRegex(
            self.rendered[
                runtime_position : self.rendered.index(">", runtime_position) + 1
            ],
            r"\bsrc\s*=",
        )

        with tempfile.TemporaryDirectory() as temporary_directory:
            runtime_path = Path(temporary_directory) / "diff-summary-runtime.js"
            runtime_path.write_text(self.runtime, encoding="utf-8")
            checked = subprocess.run(
                ["node", "--check", str(runtime_path)],
                cwd=ROOT,
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                check=False,
            )

        self.assertEqual(checked.returncode, 0, checked.stdout)

    def test_runtime_declares_required_functions_without_unsafe_dom_sinks(self) -> None:
        required_functions = (
            "safeStorageGet",
            "safeStorageSet",
            "safeStorageRemove",
            "loadComments",
            "saveComments",
            "copyText",
            "fallbackCopy",
            "renderComments",
            "openCommentEditor",
            "editComment",
            "deleteComment",
            "clearComments",
            "jumpToComment",
            "buildFeedbackMarkdown",
            "answerQuiz",
            "applyTheme",
            "setLanguage",
            "setSidebarCollapsed",
            "setSidebarWidth",
        )
        for function_name in required_functions:
            with self.subTest(function=function_name):
                self.assertRegex(
                    self.runtime,
                    rf"\bfunction\s+{re.escape(function_name)}\s*\(",
                )

        forbidden_sinks = (
            r"\.innerHTML\b",
            r"\binsertAdjacentHTML\b",
            r"\beval\s*\(",
            r"\bnew\s+Function\b",
            r"\bFunction\s*\(",
            r"\bdocument\.write\b",
        )
        for pattern in forbidden_sinks:
            with self.subTest(pattern=pattern):
                self.assertNotRegex(self.runtime, pattern)
        self.assertIn("document.createElement", self.runtime)
        self.assertIn(".textContent", self.runtime)

    def test_payload_and_storage_failures_are_guarded_and_reported(self) -> None:
        self.assertRegex(
            self.runtime,
            re.compile(
                r"function\s+readJsonPayload\s*\([^)]*\)\s*\{.*?try\s*\{.*?JSON\.parse"
                r".*?catch\s*\([^)]*\)\s*\{.*?announce\(",
                re.DOTALL,
            ),
        )
        for element_id in ("summary-data", "raw-markdown", "comment-scope"):
            with self.subTest(payload=element_id):
                self.assertIn(f'readJsonPayload("{element_id}"', self.runtime)
        for payload_state in (
            "summaryPayload.ok",
            "rawMarkdownPayload.ok",
            "commentScopePayload.ok",
        ):
            with self.subTest(payload_state=payload_state):
                self.assertIn(payload_state, self.runtime)

        storage_contracts = {
            "safeStorageGet": "localStorage.getItem",
            "safeStorageSet": "localStorage.setItem",
            "safeStorageRemove": "localStorage.removeItem",
        }
        for function_name, operation in storage_contracts.items():
            with self.subTest(function=function_name):
                self.assertRegex(
                    self.runtime,
                    re.compile(
                        rf"function\s+{function_name}\s*\([^)]*\)\s*\{{.*?try\s*\{{"
                        rf".*?{re.escape(operation)}.*?catch\s*\([^)]*\)\s*\{{.*?announce\(",
                        re.DOTALL,
                    ),
                )
        self.assertEqual(self.runtime.count("localStorage."), 3)
        self.assertIn('"diff-summary:comments:" + commentScope', self.runtime)
        self.assertIn("let interactionsReady =", self.runtime)
        self.assertRegex(
            self.runtime,
            r"const\s+commentStorageKey\s*=\s*interactionsReady\s*\?",
        )
        self.assertIn("if (!commentStorageKey)", self.runtime)
        self.assertIn("safeStorageRemove(commentStorageKey)", self.runtime)

    def test_comment_runtime_validates_records_and_supports_editor_lifecycle(
        self,
    ) -> None:
        for field in ("id", "summaryId", "text", "createdAt", "updatedAt"):
            with self.subTest(field=field):
                self.assertRegex(self.runtime, rf"record\.{field}\b")
        self.assertIn("Number.isFinite(record.createdAt)", self.runtime)
        self.assertIn("Number.isFinite(record.updatedAt)", self.runtime)
        self.assertIn(
            "Number.isFinite(new Date(record.createdAt).getTime())",
            self.runtime,
        )
        self.assertIn(
            "Number.isFinite(new Date(record.updatedAt).getTime())",
            self.runtime,
        )
        self.assertNotIn(".toISOString()", self.runtime)
        self.assertIn("cardsById.has(record.summaryId)", self.runtime)
        self.assertIn("record.text.trim()", self.runtime)
        self.assertIn("crypto.randomUUID", self.runtime)
        self.assertIn('event.key === "Escape"', self.runtime)
        self.assertIn(
            '(event.metaKey || event.ctrlKey) && event.key === "Enter"', self.runtime
        )
        self.assertIn("parentNode.insertBefore(editor, toolbar)", self.runtime)
        self.assertIn('cardElement.querySelector(".comment-thread")', self.runtime)
        self.assertIn("activeEditor.trigger", self.runtime)
        self.assertIn("closeCommentEditor(false)", self.runtime)
        self.assertIn("article.tabIndex = -1", self.runtime)
        self.assertIn("targetComment.focus", self.runtime)
        self.assertIn("window.confirm", self.runtime)
        self.assertIn("createdAt: existing.createdAt", self.runtime)
        self.assertRegex(self.runtime, r"updatedAt:\s*Math\.max\(")
        self.assertIn("const saved = saveComments()", self.runtime)
        self.assertGreaterEqual(self.runtime.count("if (saveComments()) {"), 1)
        self.assertIn('cardElement.querySelector("[data-add-comment]")', self.runtime)
        self.assertIn("if (safeStorageRemove(commentStorageKey))", self.runtime)

        self.assertIn("data-comment-list", self.rendered)
        self.assertIn("data-comment-empty", self.rendered)
        self.assertIn("data-copy-feedback", self.rendered)
        self.assertIn("data-copy-report", self.rendered)
        self.assertIn("data-clear-comments", self.rendered)

    def test_sidebar_control_labels_do_not_create_heading_id_collisions(self) -> None:
        colliding_report = REPORT.replace(
            "## Notes",
            "## Comment Panel Title\n\n## Sidebar Footer Title",
            1,
        )
        rendered = renderer.assemble_html(
            parse_report(colliding_report),
            renderer.load_template(),
        )
        inventory = _MarkupInventory()
        inventory.feed(rendered)
        ids = [attrs["id"] for _, attrs in inventory.elements if "id" in attrs]

        self.assertEqual(len(ids), len(set(ids)))

    def test_copy_contract_uses_exact_embedded_markdown_and_checked_fallback(
        self,
    ) -> None:
        self.assertIn("navigator.clipboard.writeText(text)", self.runtime)
        self.assertIn('document.execCommand("copy") === true', self.runtime)
        self.assertIn("copyText(card.markdown", self.runtime)
        self.assertIn("copyText(rawMarkdown", self.runtime)
        self.assertIn("rawMarkdown !== null", self.runtime)
        self.assertIn("buildFeedbackMarkdown()", self.runtime)
        self.assertIn("card.markdown", self.runtime)
        self.assertIn("strings.feedbackIntro", self.runtime)
        self.assertIn("strings.noCommentsPayload", self.runtime)
        self.assertIn("reportContext.repository", self.runtime)
        self.assertIn("reportContext.scope", self.runtime)
        self.assertIn("reportContext.command", self.runtime)
        self.assertIn("reportContext.head", self.runtime)
        self.assertIn('announce(successMessage, "success")', self.runtime)
        self.assertIn("showManualCopy(text, copyOrigin)", self.runtime)
        self.assertIn('announce(failureMessage, "error")', self.runtime)

    def test_explicit_stored_theme_overrides_each_default_theme_at_runtime(
        self,
    ) -> None:
        template = renderer.load_template()
        self.assertIn('body[data-default-theme="dark"]:not([data-theme])', template)
        self.assertIn('body[data-default-theme="light"]:not([data-theme])', template)

        for default_theme, stored_theme in (("dark", "light"), ("light", "dark")):
            with self.subTest(default=default_theme, stored=stored_theme):
                result = self.runtime_scenario(
                    defaultTheme=default_theme,
                    storage={"diff-summary:theme": stored_theme},
                )

                self.assertEqual(result["before"]["currentTheme"], stored_theme)
                self.assertEqual(result["before"]["bodyTheme"], stored_theme)
                self.assertEqual(result["before"]["defaultTheme"], default_theme)

    def test_card_identity_mismatch_fails_closed_for_comments_and_feedback(
        self,
    ) -> None:
        result = self.runtime_scenario(domCardIds=["DS-999"])

        self.assertFalse(result["before"]["interactionsReady"])
        self.assertIsNone(result["before"]["commentStorageKey"])
        self.assertEqual(result["before"]["bodyInteractionsReady"], "false")
        self.assertTrue(result["controls"]["addDisabled"])
        self.assertTrue(result["controls"]["feedbackDisabled"])
        self.assertTrue(result["controls"]["clearDisabled"])
        self.assertFalse(
            any(
                call[0] in {"get", "set", "remove"}
                and isinstance(call[1], str)
                and call[1].startswith("diff-summary:comments:")
                for call in result["storageCalls"]
            )
        )
        self.assertEqual(result["tone"], "error")

    def test_malformed_comments_preserve_storage_warning_when_reset_fails(self) -> None:
        comment_key = "diff-summary:comments:chann/skills::main..dev::runtime"
        result = self.runtime_scenario(
            storage={comment_key: "{"},
            storageRemoveThrows=True,
        )

        self.assertIn(["remove", comment_key], result["storageCalls"])
        self.assertEqual(result["tone"], "warning")
        self.assertEqual(
            result["status"],
            "Browser storage is unavailable. Changes will remain in this tab only.",
        )

    def test_copy_failure_opens_selectable_manual_dialog_and_restores_focus(
        self,
    ) -> None:
        payload = "Exact reviewer payload\nwith a second line"
        result = self.runtime_scenario(
            action="copy-failure",
            copyText=payload,
            clipboardRejects=True,
            execCommandResult=False,
        )

        self.assertTrue(result["afterCopy"]["manualCopyOpen"])
        self.assertEqual(result["afterCopy"]["manualCopyText"], payload)
        self.assertEqual(result["afterCopy"]["manualCopySelection"], [0, len(payload)])
        self.assertEqual(result["afterCopy"]["activeFocus"], "manual-copy-text")
        self.assertFalse(result["afterDismiss"]["manualCopyOpen"])
        self.assertEqual(result["afterDismiss"]["activeFocus"], "origin")

    def test_comment_commit_restores_add_trigger_after_storage_success_or_failure(
        self,
    ) -> None:
        for storage_set_throws in (False, True):
            with self.subTest(storage_set_throws=storage_set_throws):
                result = self.runtime_scenario(
                    action="comment-commit",
                    commentText="Focus must return after this comment is saved.",
                    storageSetThrows=storage_set_throws,
                )

                state = result["afterCommentCommit"]
                self.assertFalse(state["editorOpen"])
                self.assertEqual(state["activeFocus"], "origin")
                if storage_set_throws:
                    self.assertEqual(result["tone"], "warning")
                    self.assertIn("storage is unavailable", result["status"])
                else:
                    self.assertEqual(result["tone"], "success")
                    self.assertEqual(result["status"], "Comment saved.")

    def test_user_sidebar_collapse_moves_focus_to_external_expand_control(
        self,
    ) -> None:
        result = self.runtime_scenario(action="sidebar-focus")

        self.assertEqual(result["before"]["activeFocus"], "origin")
        self.assertEqual(
            result["sidebarFocusStates"]["afterCollapse"],
            "sidebar-expand",
        )

    def test_print_control_calls_window_print_once(self) -> None:
        result = self.runtime_scenario(action="print-control")

        self.assertEqual(result["printCalls"], 1)

    def test_print_control_is_localized_in_english_and_korean(self) -> None:
        for language, expected_text, expected_label in (
            ("en", "Print", "Print report"),
            ("ko", "인쇄", "보고서 인쇄"),
        ):
            with self.subTest(language=language):
                result = self.runtime_scenario(language=language)

                self.assertEqual(result["printControl"]["textContent"], expected_text)
                self.assertEqual(result["printControl"]["ariaLabel"], expected_label)

    def test_user_sidebar_expand_moves_focus_to_internal_toggle(self) -> None:
        result = self.runtime_scenario(action="sidebar-focus")

        self.assertEqual(
            result["sidebarFocusStates"]["afterExpand"],
            "sidebar-toggle",
        )

    def test_persisted_and_programmatic_sidebar_state_preserve_focus(self) -> None:
        result = self.runtime_scenario(
            action="sidebar-programmatic",
            storage={"diff-summary:sidebar:collapsed": "true"},
        )

        self.assertEqual(result["before"]["activeFocus"], "origin")
        self.assertEqual(
            result["sidebarFocusStates"],
            {"afterCollapse": "origin", "afterExpand": "origin"},
        )

    def test_theme_sidebar_resizer_and_localized_controls_have_accessible_hooks(
        self,
    ) -> None:
        inventory = _MarkupInventory()
        inventory.feed(self.rendered)
        buttons = [attrs for tag, attrs in inventory.elements if tag == "button"]
        resizer = next(
            attrs
            for tag, attrs in inventory.elements
            if "data-sidebar-resizer" in attrs
        )
        ids = [attrs["id"] for _, attrs in inventory.elements if "id" in attrs]

        self.assertTrue(all(attrs.get("type") == "button" for attrs in buttons))
        self.assertTrue(all(attrs.get("aria-label") for attrs in buttons))
        self.assertEqual(len(ids), len(set(ids)))
        self.assertEqual(resizer["role"], "separator")
        self.assertEqual(resizer["tabindex"], "0")
        self.assertEqual(resizer["aria-orientation"], "vertical")
        self.assertIsNotNone(resizer["aria-valuemin"])
        self.assertIsNotNone(resizer["aria-valuemax"])
        self.assertIsNotNone(resizer["aria-valuenow"])

        for storage_key in (
            "diff-summary:theme",
            "diff-summary:sidebar:collapsed",
            "diff-summary:sidebar:width",
        ):
            with self.subTest(storage_key=storage_key):
                self.assertIn(storage_key, self.runtime)
        self.assertIn('removeAttribute("data-theme")', self.runtime)
        self.assertIn("body.dataset.theme = theme", self.runtime)
        self.assertIn("dataset.sidebarCollapsed = String(collapsed)", self.runtime)
        self.assertIn("const root = document.documentElement;", self.runtime)
        self.assertIn('const rail = document.querySelector("aside[data-sidebar]");', self.runtime)
        self.assertIn(
            'const sidebarExpand = document.querySelector("[data-sidebar-expand]");',
            self.runtime,
        )
        self.assertIn("root.dataset.sidebarCollapsed = String(collapsed)", self.runtime)
        self.assertNotIn('rail.classList.toggle("is-collapsed"', self.runtime)
        self.assertIn('root.style.setProperty("--sidebar-width"', self.runtime)
        self.assertIn("const SIDEBAR_MIN = 96;", self.runtime)
        self.assertIn("const SIDEBAR_MAX = 480;", self.runtime)
        self.assertIn("storedWidth === null ? 220 : storedWidth", self.runtime)
        self.assertRegex(
            self.runtime,
            r'target\.matches\("\[data-sidebar-toggle\]"\)\)\s*\{\s*'
            r"setSidebarCollapsed\(true\);",
        )
        self.assertRegex(
            self.runtime,
            r'target\.matches\("\[data-sidebar-expand\]"\)\)\s*\{\s*'
            r"setSidebarCollapsed\(false\);",
        )
        self.assertIn("Math.min(SIDEBAR_MAX", self.runtime)
        self.assertIn("Math.max(SIDEBAR_MIN", self.runtime)
        self.assertIn('event.key === "ArrowLeft"', self.runtime)
        self.assertIn('event.key === "ArrowRight"', self.runtime)
        self.assertIn('addEventListener("pointerdown"', self.runtime)
        self.assertIn('addEventListener("pointermove"', self.runtime)

        template = renderer.load_template()
        for selector in (
            ".comment-editor",
            ".comment-thread",
            ".comment-panel",
            ".comment-list",
            ".comment-edit",
            ".comment-delete",
            ".sidebar-resizer",
        ):
            with self.subTest(selector=selector):
                self.assertIn(selector, template)
        print_styles = template[template.index("@media print") :]
        self.assertIn(".comment-thread", print_styles)
        self.assertIn(".comment-editor", print_styles)
        self.assertIn(".sidebar-resizer", print_styles)


if __name__ == "__main__":
    unittest.main()
