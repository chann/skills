import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPTS_DIR = ROOT / "code-review" / "skills" / "code-review" / "scripts"
sys.path.insert(0, str(SCRIPTS_DIR))

from generate_html_report import extract_findings, parse_markdown  # noqa: E402


GENERATOR = SCRIPTS_DIR / "generate_html_report.py"


def test_markdown_tables_render_in_named_focusable_scroll_regions() -> None:
    markdown = """# Code Review Report

**Language:** en

## Executive Summary

| Metric | Value |
|--------|-------|
| Files changed | 2 |
"""

    html, _meta, _sidebar = parse_markdown(markdown)

    wrapper = (
        '<div class="table-scroll" role="region" '
        'aria-label="Executive Summary" tabindex="0">'
    )
    wrapper_index = html.index(wrapper)
    table_index = html.index("<table>", wrapper_index)
    table_end_index = html.index("</table>", table_index)
    wrapper_end_index = html.index("</div>", table_end_index)

    assert wrapper_index < table_index < table_end_index < wrapper_end_index
    assert "<table>" in html
    assert '<table class="table-scroll"' not in html


def test_generic_table_scroll_region_does_not_capture_fenced_diff_tables() -> None:
    markdown = """# Code Review Report

**Language:** en

## Evidence

| File | Status |
|------|--------|
| src/cache.py | Modified |

```diff
--- a/src/cache.py
+++ b/src/cache.py
@@ -1 +1 @@
-stale = True
+stale = False
```
"""

    html, _meta, _sidebar = parse_markdown(markdown)

    wrapper_start = html.index('<div class="table-scroll"')
    table_end = html.index("</table>", wrapper_start)
    wrapper_end = html.index("</div>", table_end)
    wrapper_html = html[wrapper_start:wrapper_end]

    assert html.count('class="table-scroll"') == 1
    assert html.count('<table class="diff-table') == 2
    assert 'aria-label="Evidence"' in wrapper_html
    assert "diff-table" not in wrapper_html


def test_finding_actions_render_after_finding_content_with_full_markdown_label() -> None:
    markdown = """# Code Review Report

**Language:** en

## Findings

### HIGH

#### [CR-001] Fix cache invalidation
**File:** `src/cache.py` (lines 1-3)

The cache can return stale data.

**Suggested fix:**
```python
invalidate_cache()
```

---
"""

    html, _meta, _sidebar = parse_markdown(markdown)

    content_index = html.index("The cache can return stale data.")
    code_index = html.index("invalidate_cache()")
    toolbar_index = html.index('class="finding-toolbar"')
    close_index = html.index("</div></details>")

    assert content_index < code_index < toolbar_index < close_index
    assert '<span data-i18n="copyMd">Copy Markdown</span>' in html
    assert "Copy MD" not in html


def test_bilingual_korean_primary_keeps_parser_significant_metadata(
    tmp_path: Path,
) -> None:
    korean_report = tmp_path / "bilingual-review.ko.md"
    english_report = tmp_path / "bilingual-review.en.md"
    output = tmp_path / "bilingual-review.html"

    korean_report.write_text(
        """# 코드 리뷰 보고서

**Date:** 2026-07-14
**Reviewer:** Codex 자동 리뷰
**Scope:** 작업 트리
**Repository:** chann/skills
**Language:** ko

## 발견 사항

### HIGH

#### [CR-001] 메타데이터 키 유지
**File:** `src/report.py` (line 1)

한국어 본문은 유지됩니다.
""",
        encoding="utf-8",
    )
    english_report.write_text(
        """# Code Review Report

**Date:** 2026-07-14
**Reviewer:** Codex automated review
**Scope:** Working tree
**Repository:** chann/skills
**Language:** en

## Findings

### HIGH

#### [CR-001] Preserve metadata keys
**File:** `src/report.py` (line 1)

The English body is retained.
""",
        encoding="utf-8",
    )

    result = subprocess.run(
        [sys.executable, str(GENERATOR), str(korean_report), "-o", str(output)],
        cwd=ROOT,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        timeout=30,
        check=False,
    )

    assert result.returncode == 0, result.stdout
    assert "(ko+en)" in result.stdout
    html = output.read_text(encoding="utf-8")
    assert '<html lang="ko"' in html
    assert 'data-report-lang="ko"' in html
    assert (
        '<div class="lang-body" data-lang="ko"><h1>코드 리뷰 보고서</h1>' in html
    )
    assert '<h2 id="ko--발견-사항">발견 사항</h2>' in html
    assert (
        '<div class="lang-body" data-lang="en"><h1>Code Review Report</h1>' in html
    )
    assert '<h2 id="en--findings">Findings</h2>' in html
    assert '<button type="button" data-set-lang="ko">한국어</button>' in html
    assert '<button type="button" data-set-lang="en">English</button>' in html
    assert '<p><strong>Scope:</strong> 작업 트리</p>' in html
    assert "<p>한국어 본문은 유지됩니다.</p>" in html
    assert "<p>The English body is retained.</p>" in html
    assert '<div class="repo">chann/skills</div>' in html
    assert 'lang: "ko",' in html
    assert 'langCodes: ["ko", "en"],' in html
    assert 'commentScope: "chann/skills::bilingual-review"' in html
    assert html.count('data-finding-id="CR-001"') == 2


PROOF_REPORT = """# Code Review Report

**Language:** en

## Findings

### HIGH

#### [CR-001] Cache returns stale rows after invalidate
**File:** `src/cache.py` (lines 10-14)
**Evidence:** ran — `python3 /tmp/repro/check.py` printed:

```text
AssertionError: expected 2, got 1
```

**Observed behavior:** The cache keeps the old row.

#### [CR-002] Token compared with ==
**File:** `src/auth.py` (line 7)
**Evidence:** `cited`, not traced — `src/auth.py:7`

**Observed behavior:** A plain comparison.

### LOW

#### [CR-003] Name drift
**File:** `src/names.py` (line 3)

**Observed behavior:** No evidence field.

Dropped: 2 (said only)
"""


def test_evidence_field_renders_proof_level_pill_in_body_and_summary() -> None:
    html, _meta, _sidebar = parse_markdown(PROOF_REPORT)

    assert 'data-finding-id="CR-001" data-proof-level="ran"' in html
    assert (
        '<p class="finding-evidence"><strong>Evidence:</strong> '
        '<span class="proof proof-ran" data-proof-level="ran">ran</span> '
        '— <code>python3 /tmp/repro/check.py</code> printed:</p>'
    ) in html
    summary_start = html.index('data-finding-id="CR-001"')
    summary_end = html.index("</summary>", summary_start)
    assert 'class="proof proof-ran"' in html[summary_start:summary_end]
    # The pasted output stays a code block under the field.
    assert "AssertionError: expected 2, got 1" in html


def test_cited_not_traced_caveat_is_marked_and_backticked_level_parses() -> None:
    html, _meta, _sidebar = parse_markdown(PROOF_REPORT)

    assert 'data-finding-id="CR-002" data-proof-level="cited"' in html
    assert '<p class="finding-evidence" data-proof-caveat="not-traced">' in html
    assert '<span class="proof proof-cited" data-proof-level="cited">cited</span>' in html


def test_finding_without_evidence_has_no_proof_pill_and_dropped_line_is_text() -> None:
    html, _meta, _sidebar = parse_markdown(PROOF_REPORT)

    start = html.index('data-finding-id="CR-003"')
    end = html.index("</details>", start)
    assert "data-proof-level" not in html[start - 200:end]
    assert "<p>Dropped: 2 (said only)</p>" in html


def test_unknown_level_falls_back_to_plain_labelled_field() -> None:
    html, _meta, _sidebar = parse_markdown(
        PROOF_REPORT.replace("**Evidence:** ran", "**Evidence:** runaway")
    )

    assert (
        '<p class="finding-evidence"><strong>Evidence:</strong> runaway'
    ) in html
    assert 'data-finding-id="CR-001" data-proof-level' not in html


def test_extracted_findings_carry_proof_level_for_copy_payload() -> None:
    findings = {f["id"]: f for f in extract_findings(PROOF_REPORT)}

    assert findings["CR-001"]["proof"] == "ran"
    assert findings["CR-002"]["proof"] == "cited"
    assert findings["CR-003"]["proof"] is None
    assert "**Evidence:** ran" in findings["CR-001"]["markdown"]


def test_generated_html_ships_proof_pill_styles(tmp_path: Path) -> None:
    report = tmp_path / "proof.md"
    output = tmp_path / "proof.html"
    report.write_text(PROOF_REPORT, encoding="utf-8")

    result = subprocess.run(
        [sys.executable, str(GENERATOR), str(report), "-o", str(output)],
        cwd=ROOT,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        timeout=30,
        check=False,
    )

    assert result.returncode == 0, result.stdout
    html = output.read_text(encoding="utf-8")
    assert ".proof {" in html
    assert ".proof-ran, .proof-reproduced {" in html
    assert html.count('class="proof proof-ran"') == 2
    assert '"proof": "ran"' in html
