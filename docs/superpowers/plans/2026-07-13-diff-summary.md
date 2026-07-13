# Diff Summary Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add a self-contained `diff-summary` skill that turns an exact git diff scope into evidence-based Markdown and interactive offline HTML with per-summary comments and Markdown copy.

**Architecture:** Keep analysis in `SKILL.md` and presentation in a standard-library Python renderer. The renderer parses stable `DS-*` Markdown cards, safely embeds structured data into a bundled offline template, and scopes browser comments by repository, exact comparison, HEAD, and normalized card content. Package it as an independent fifth skill inside the existing `code-review` plugin.

**Tech Stack:** Portable `SKILL.md`, Python 3.10+ standard library, HTML/CSS/vanilla JavaScript, `unittest`, `uvx pytest`, `npx skills`, browser automation.

---

## File Map

- Create `code-review/skills/diff-summary/SKILL.md`: trigger surface, exact-scope rules, evidence workflow, report contract, and boundaries.
- Create `code-review/skills/diff-summary/agents/openai.yaml`: Codex UI name, description, and default `$diff-summary` prompt.
- Create `code-review/skills/diff-summary/scripts/generate_summary_report.py`: Markdown parser, safe renderer, stable comment scope, CLI, and optional browser open.
- Create `code-review/skills/diff-summary/assets/summary-template.html`: offline report styling and comment/copy/theme/sidebar behavior.
- Create `code-review/commands/diff-summary.md`: Claude slash-command wrapper.
- Create `tests/test_diff_summary_skill_package.py`: packaging, discovery, trigger, workflow, and version contract.
- Create `tests/diff_summary/__init__.py`: recursive unittest discovery marker.
- Create `tests/diff_summary/test_summary_report.py`: parser, security, assembly, CLI, and template behavior.
- Modify `code-review/.claude-plugin/plugin.json`: advertise the fifth skill and bump to `2.3.0`.
- Modify `tests/test_code_review_skill_package.py`: update current plugin version assertion.
- Modify `.gitignore`: ignore generated `.diff-summaries/` artifacts in this repository.
- Modify `code-review/README.md`, `code-review/README.ko.md`, `README.md`, `README.ko.md`, `USAGE.md`, and `ARCHITECTURE.md`: install, invoke, distinguish, and explain the new skill.
- Keep `docs/superpowers/specs/2026-07-13-diff-summary-design.md` and this plan as committed design evidence.

### Task 1: Lock the package and trigger contract, then scaffold the skill

**Files:**
- Create: `tests/test_diff_summary_skill_package.py`
- Create: `code-review/skills/diff-summary/` with the system `skill-creator` initializer
- Create: `code-review/commands/diff-summary.md`
- Modify: `code-review/.claude-plugin/plugin.json`
- Modify: `tests/test_code_review_skill_package.py`

- [ ] **Step 1: Write the failing package test**

Create a `unittest.TestCase` that checks the real tracked paths and discovery output:

```python
import json
import os
import re
import subprocess
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PLUGIN = ROOT / "code-review"
SKILL = PLUGIN / "skills" / "diff-summary"


class DiffSummarySkillPackageTests(unittest.TestCase):
    def test_package_shape_and_metadata(self) -> None:
        expected = [
            SKILL / "SKILL.md",
            SKILL / "agents" / "openai.yaml",
            SKILL / "scripts" / "generate_summary_report.py",
            SKILL / "assets" / "summary-template.html",
            PLUGIN / "commands" / "diff-summary.md",
        ]
        for path in expected:
            with self.subTest(path=path):
                self.assertTrue(path.is_file(), str(path))

        metadata = json.loads((PLUGIN / ".claude-plugin" / "plugin.json").read_text())
        self.assertEqual(metadata["version"], "2.3.0")
        self.assertIn("diff-summary", metadata["description"])

    def test_trigger_description_covers_natural_prompts_and_boundaries(self) -> None:
        text = (SKILL / "SKILL.md").read_text(encoding="utf-8")
        for phrase in (
            "코드를 요약해줘",
            "main..dev 코드를 요약해줘",
            "summarize this diff",
            "what changed between branches",
            "Preserve an explicit user-specified range exactly",
            "Do not rewrite `..` to `...`",
            "code-review",
            "diff-viewer",
        ):
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, text)

    def test_skills_cli_discovers_diff_summary(self) -> None:
        env = os.environ.copy()
        env.update({"NO_COLOR": "1", "FORCE_COLOR": "0"})
        result = subprocess.run(
            ["npx", "--yes", "skills", "add", ".", "-l", "--full-depth"],
            cwd=ROOT,
            env=env,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            timeout=60,
            check=False,
        )
        self.assertEqual(result.returncode, 0, result.stdout)
        self.assertRegex(result.stdout, re.compile(r"(?m)^[^A-Za-z0-9]*diff-summary\s*$"))
```

- [ ] **Step 2: Run the package test and verify RED**

Run:

```bash
PYTHONDONTWRITEBYTECODE=1 python -m unittest tests.test_diff_summary_skill_package -v
```

Expected: FAIL because `code-review/skills/diff-summary` and plugin version `2.3.0` do not exist yet.

- [ ] **Step 3: Initialize the skill through `skill-creator`**

Run:

```bash
python /Users/heechanpark/.codex/skills/.system/skill-creator/scripts/init_skill.py \
  diff-summary \
  --path code-review/skills \
  --resources scripts,assets \
  --interface 'display_name=Diff Summary' \
  --interface 'short_description=Summarize code changes as interactive HTML' \
  --interface 'default_prompt=Use $diff-summary to summarize the current code changes as an interactive HTML report.'
```

Keep `agents/openai.yaml`; remove only initializer placeholders after replacing them with real content.

- [ ] **Step 4: Add the command wrapper and plugin metadata**

Write `commands/diff-summary.md` with `argument-hint: "[scope]"`, route to the `diff-summary` skill, require Markdown plus HTML generation and browser opening, and pass the user's exact scope without normalizing dot syntax.

Update `plugin.json` to:

```json
{
  "name": "code-review",
  "description": "Automated code review and change intelligence from git diffs. Generates structured review reports, explanatory diff summaries, and browser-readable raw diff reports.",
  "version": "2.3.0"
}
```

Update `tests/test_code_review_skill_package.py` to expect `2.3.0` and require both `diff-viewer` and `diff-summary` in the metadata description.

- [ ] **Step 5: Re-run only the package shape assertions**

Run:

```bash
PYTHONDONTWRITEBYTECODE=1 python -m unittest \
  tests.test_diff_summary_skill_package.DiffSummarySkillPackageTests.test_package_shape_and_metadata -v
```

Expected: PASS. Discovery and trigger tests remain RED until later tasks.

### Task 2: Implement strict Markdown parsing and stable summary identities

**Files:**
- Create: `tests/diff_summary/__init__.py`
- Create: `tests/diff_summary/test_summary_report.py`
- Create: `code-review/skills/diff-summary/scripts/generate_summary_report.py`

- [ ] **Step 1: Write parser tests first**

Use this representative source:

```python
SAMPLE = """# Diff Summary Report

**Date:** 2026-07-13
**Repository:** skills
**Scope:** main..dev
**Command:** `git diff --no-ext-diff --no-color main..dev`
**HEAD:** a1b2c3d
**Language:** en

## Major Changes

### Architecture

#### [DS-001] Split collection from rendering
**Category:** Architecture
**Impact:** High
**Files:** `src/diff.py`, `src/report.py`

Rendering now consumes a collected context.

**Evidence:** `ReportBuilder` accepts `DiffContext`.

### Test

#### [DS-002] Cover scope semantics
**Category:** Test
**Impact:** Medium
**Files:** `tests/test_scope.py`

Two-dot and three-dot scopes have separate regression cases.
"""
```

Tests must assert:

```python
report = parse_report(SAMPLE)
self.assertEqual(report.metadata.repository, "skills")
self.assertEqual(report.metadata.scope, "main..dev")
self.assertEqual(report.metadata.head, "a1b2c3d")
self.assertEqual([card.id for card in report.cards], ["DS-001", "DS-002"])
self.assertEqual(report.cards[0].category, "Architecture")
self.assertIn("#### [DS-001]", report.cards[0].markdown)
self.assertNotIn("#### [DS-002]", report.cards[0].markdown)
```

Add negative tests for missing `Repository`, `Scope`, `Command`, `HEAD`, or `Language`; malformed IDs; duplicate IDs; non-sequential IDs; unsupported category/impact; unsafe fence tokens; and Korean Unicode content.

- [ ] **Step 2: Run parser tests and verify RED**

Run:

```bash
PYTHONDONTWRITEBYTECODE=1 python -m unittest tests.diff_summary.test_summary_report -v
```

Expected: import failure because the generator API does not exist.

- [ ] **Step 3: Implement parser types and validation**

Implement these public types and functions:

```python
@dataclass(frozen=True)
class ReportMetadata:
    title: str
    date: str
    repository: str
    scope: str
    command: str
    head: str
    language: str


@dataclass(frozen=True)
class SummaryCard:
    id: str
    title: str
    section: str
    category: str
    impact: str
    files: tuple[str, ...]
    markdown: str


@dataclass(frozen=True)
class ParsedReport:
    metadata: ReportMetadata
    cards: tuple[SummaryCard, ...]
    markdown: str


class ReportFormatError(ValueError):
    pass


CATEGORIES = {
    "Overview", "Behavior", "Architecture", "Pattern", "API", "Data",
    "Dependency", "Security", "Performance", "Test", "Operations",
    "Compatibility",
}
IMPACTS = {"High", "Medium", "Low", "Informational"}


def safe_fence_language(value: str) -> str:
    return re.sub(r"[^A-Za-z0-9_.+-]", "", value)[:32]


def parse_report(markdown: str) -> ParsedReport:
    lines = markdown.splitlines()
    if not lines or not lines[0].startswith("# "):
        raise ReportFormatError("missing report title")

    fields: dict[str, str] = {}
    field_re = re.compile(r"^\*\*(Date|Repository|Scope|Command|HEAD|Language):\*\*\s*(.+)$")
    for line in lines:
        match = field_re.match(line.strip())
        if match:
            fields[match.group(1)] = match.group(2).strip().strip("`")
    missing = [name for name in ("Date", "Repository", "Scope", "Command", "HEAD", "Language")
               if not fields.get(name)]
    if missing:
        raise ReportFormatError("missing metadata: " + ", ".join(missing))

    cards: list[SummaryCard] = []
    section = ""
    index = 0
    while index < len(lines):
        stripped = lines[index].strip()
        if stripped.startswith("### ") and not stripped.startswith("#### "):
            section = stripped[4:].strip()
            index += 1
            continue
        if not stripped.startswith("#### "):
            index += 1
            continue

        heading = stripped[5:].strip()
        id_match = re.match(r"^\[(DS-\d{3})\]\s+(.+)$", heading)
        if not id_match:
            raise ReportFormatError(f"malformed summary heading: {heading}")
        expected = f"DS-{len(cards) + 1:03d}"
        if id_match.group(1) != expected:
            raise ReportFormatError(f"expected {expected}, found {id_match.group(1)}")

        end = index + 1
        while end < len(lines) and not re.match(r"^#{2,4}\s", lines[end].strip()):
            end += 1
        block_lines = lines[index:end]
        block = "\n".join(block_lines).strip()
        card_fields: dict[str, str] = {}
        for block_line in block_lines[1:]:
            match = re.match(r"^\*\*(Category|Impact|Files):\*\*\s*(.+)$", block_line.strip())
            if match:
                card_fields[match.group(1)] = match.group(2).strip()
        if card_fields.get("Category") not in CATEGORIES:
            raise ReportFormatError(f"unsupported category in {expected}")
        if card_fields.get("Impact") not in IMPACTS:
            raise ReportFormatError(f"unsupported impact in {expected}")
        files = tuple(re.findall(r"`([^`]+)`", card_fields.get("Files", "")))
        if not files:
            raise ReportFormatError(f"missing files in {expected}")
        cards.append(SummaryCard(
            id=expected,
            title=id_match.group(2).strip(),
            section=section,
            category=card_fields["Category"],
            impact=card_fields["Impact"],
            files=files,
            markdown=block,
        ))
        index = end

    if not cards:
        raise ReportFormatError("report contains no DS summary cards")
    metadata = ReportMetadata(
        title=lines[0][2:].strip(),
        date=fields["Date"],
        repository=fields["Repository"],
        scope=fields["Scope"],
        command=fields["Command"],
        head=fields["HEAD"],
        language=fields["Language"].lower(),
    )
    return ParsedReport(metadata=metadata, cards=tuple(cards), markdown=markdown)
```

Require IDs to equal `DS-001`, `DS-002`, ... in source order. Parse card metadata only from the card body and require controlled category/impact values. Preserve the exact raw Markdown slice from the `####` heading until the next `####`, `###`, `##`, or end of file.

- [ ] **Step 4: Run parser tests and verify GREEN**

Run the same unittest command. Expected: all parser tests PASS with no warnings.

- [ ] **Step 5: Refactor without changing behavior**

Extract small helpers for metadata, card boundaries, and card field parsing. Re-run the parser tests after refactoring.

### Task 3: Render safe offline HTML and deterministic report scope

**Files:**
- Modify: `tests/diff_summary/test_summary_report.py`
- Modify: `code-review/skills/diff-summary/scripts/generate_summary_report.py`
- Create: `code-review/skills/diff-summary/assets/summary-template.html`

- [ ] **Step 1: Add failing renderer and security tests**

Cover:

```python
parsed = parse_report(SAMPLE)
template = (ROOT / "code-review" / "skills" / "diff-summary" / "assets" /
            "summary-template.html").read_text(encoding="utf-8")
html = assemble_html(parsed, template, default_theme="auto")
self.assertIn('data-summary-id="DS-001"', html)
self.assertIn('data-copy-summary', html)
self.assertIn('data-add-comment', html)
self.assertLess(html.index("ReportBuilder"), html.index('class="summary-toolbar"'))
self.assertNotIn("https://", html)
self.assertNotIn("http://", html)
self.assertNotIn("__REPORT_", html)
```

Also assert:

- `stable_comment_scope(parse_report(SAMPLE))` is deterministic.
- Changing only `Date` or the generated footer preserves scope.
- Changing scope, HEAD, card ID, or card content changes scope.
- JSON embedding converts `<`, `>`, `&`, `\u2028`, `\u2029`, and `</script>` safely.
- Markdown text equal to a template token remains visible after assembly.
- Missing template placeholders raise `ReportFormatError` before output.

- [ ] **Step 2: Run the new tests and verify RED**

Expected: missing `assemble_html`, `stable_comment_scope`, and template.

- [ ] **Step 3: Implement renderer helpers**

Implement:

```python
def json_for_script(value: object) -> str:
    raw = json.dumps(value, ensure_ascii=False, separators=(",", ":"))
    return (raw.replace("&", "\\u0026")
               .replace("<", "\\u003c")
               .replace(">", "\\u003e")
               .replace("\u2028", "\\u2028")
               .replace("\u2029", "\\u2029"))


def stable_comment_scope(report: ParsedReport) -> str:
    payload = {
        "repository": report.metadata.repository,
        "scope": report.metadata.scope,
        "command": report.metadata.command,
        "head": report.metadata.head,
        "cards": [{"id": card.id, "markdown": card.markdown} for card in report.cards],
    }
    digest = hashlib.sha256(
        json.dumps(payload, ensure_ascii=False, sort_keys=True).encode("utf-8")
    ).hexdigest()[:20]
    return f"{report.metadata.repository}::{report.metadata.scope}::{digest}"
```

Build a narrow Markdown renderer that escapes all text and supports headings, paragraphs, inline code/bold, lists, tables, fenced code, and diff fences. Parse category/impact/files fields into styled card metadata. Never insert report data into an HTML attribute without escaping with `quote=True`.

- [ ] **Step 4: Build the complete offline template**

The template must contain placeholders only for title, metadata, body, navigation, card JSON, raw Markdown, scope, language, and default theme. It must include all CSS/JS inline and no external `script`, `link`, font, image, or source URL.

Use a single `replace_placeholders(template, mapping)` pass that first substitutes placeholder locations with unique sentinel values and then injects user content so content resembling `__REPORT_BODY__` is not reprocessed.

- [ ] **Step 5: Run renderer/security tests and verify GREEN**

Run:

```bash
PYTHONDONTWRITEBYTECODE=1 python -m unittest tests.diff_summary.test_summary_report -v
```

Expected: parser and assembly tests PASS.

### Task 4: Implement card comments, Markdown copy, feedback export, and resilient UI

**Files:**
- Modify: `tests/diff_summary/test_summary_report.py`
- Modify: `code-review/skills/diff-summary/assets/summary-template.html`

- [ ] **Step 1: Add failing interaction-contract tests**

Assert the generated HTML contains:

```python
required = [
    "data-copy-summary",
    "data-add-comment",
    "data-copy-report",
    "data-copy-feedback",
    "data-clear-comments",
    "data-comment-list",
    "function safeStorageGet",
    "function safeStorageSet",
    "function safeStorageRemove",
    "function copyText",
    "function renderComments",
    "function editComment",
    "function deleteComment",
    "function clearComments",
    "function buildFeedbackMarkdown",
    "navigator.clipboard.writeText",
    'document.execCommand("copy")',
]
for value in required:
    self.assertIn(value, html)
```

Require card toolbar placement after content, comments inserted before the toolbar, guarded storage calls only, Korean and English interface labels, status-region error messages, theme/sidebar persistence, comment count chips, and print CSS.

- [ ] **Step 2: Run tests and verify RED**

Expected: missing interaction functions and controls.

- [ ] **Step 3: Implement browser behavior in the template**

Use the following state contract:

```javascript
const STORAGE_KEY = "diff-summary:comments:" + defaults.commentScope;
// comment = { id, summaryId, text, createdAt, updatedAt }
```

Requirements:

- All persisted JSON is schema-checked; invalid records are ignored.
- Add opens one inline editor per page; Escape cancels and Cmd/Ctrl+Enter saves.
- Empty comments are not saved.
- Edit preserves `createdAt` and changes `updatedAt`.
- Delete and clear require confirmation and update cards/sidebar/counts immediately.
- Sidebar comment entries jump to and expand the right card.
- `Copy Markdown` copies the exact card source from embedded JSON.
- `Copy report` copies the original Markdown.
- `Copy feedback` groups original card Markdown with its current comments.
- Clipboard success is shown only after Clipboard API success or a truthy `execCommand` result.
- A denied clipboard or storage operation updates the ARIA live status and leaves other controls working.

- [ ] **Step 4: Run interaction-contract tests and verify GREEN**

Run targeted unittest; expected all tests PASS.

### Task 5: Implement the CLI and complete the portable skill workflow

**Files:**
- Modify: `tests/diff_summary/test_summary_report.py`
- Modify: `tests/test_diff_summary_skill_package.py`
- Modify: `code-review/skills/diff-summary/scripts/generate_summary_report.py`
- Modify: `code-review/skills/diff-summary/SKILL.md`
- Modify: `code-review/commands/diff-summary.md`
- Verify: `code-review/skills/diff-summary/agents/openai.yaml`

- [ ] **Step 1: Add failing CLI tests**

Test `generate_report(input_path, output_path=None, theme="auto", open_report=False)` and the subprocess CLI:

- Default output is the input path with `.html` suffix.
- `-o` writes an explicit path.
- `--theme auto|light|dark` is validated.
- `--open` calls `webbrowser.open(output.resolve().as_uri())` only after a successful atomic write.
- Invalid Markdown exits non-zero, writes the error to stderr, and leaves no output or temporary file.
- Successful output prints the card count, language, comment scope, and absolute path.

- [ ] **Step 2: Run CLI tests and verify RED**

Expected: missing CLI API and non-zero test failures.

- [ ] **Step 3: Implement atomic generation and CLI**

Use `tempfile.NamedTemporaryFile(delete=False, dir=output.parent)` followed by `Path.replace()` after a complete UTF-8 write. Catch `ReportFormatError` separately for concise user errors; let unexpected failures show their type under `--debug` only. `--open` failure is a warning after the generated file remains valid.

- [ ] **Step 4: Replace initializer content with the full skill contract**

The YAML description must include the concrete Korean/English trigger phrases and explicit review/viewer boundaries. The body must contain:

- Announcement and output paths
- Scope table with exact commands
- Explicit `..`/`...` preservation rule
- Evidence collection order and analysis dimensions
- Stable `DS-*` report template
- No-fabrication and verified/unverified rules
- Generator invocation and browser opening
- Empty/invalid scope handling
- `.diff-summaries/` ignore suggestion without automatic target-repo edits
- Conversation handoff with files/lines/card count/output paths

- [ ] **Step 5: Run CLI and package trigger tests and verify GREEN**

Run:

```bash
PYTHONDONTWRITEBYTECODE=1 python -m unittest \
  tests.diff_summary.test_summary_report \
  tests.test_diff_summary_skill_package -v
```

Expected: all targeted tests PASS and discovery reports 15 skills.

### Task 6: Integrate documentation, generated paths, and plugin version

**Files:**
- Modify: `.gitignore`
- Modify: `code-review/README.md`
- Modify: `code-review/README.ko.md`
- Modify: `README.md`
- Modify: `README.ko.md`
- Modify: `USAGE.md`
- Modify: `ARCHITECTURE.md`
- Modify: `tests/test_installation_docs.py`

- [ ] **Step 1: Extend documentation tests first**

Require the code-review English/Korean README install blocks to contain `--skill diff-summary`, require root usage docs to contain `/diff-summary` and `.diff-summaries/`, and continue rejecting `chann/skills@...` selectors.

- [ ] **Step 2: Run installation-doc tests and verify RED**

Run:

```bash
PYTHONDONTWRITEBYTECODE=1 python -m unittest tests.test_installation_docs -v
```

Expected: FAIL because docs do not mention `diff-summary`.

- [ ] **Step 3: Update all English and Korean docs consistently**

Add:

- Fifth code-review selector to global and local install commands
- `/diff-summary [scope]` to command tables
- Examples for current changes, `main..dev`, last commit, and PR
- `.diff-summaries/<date>_<scope>.md/.html` output tree
- Card comments, Markdown copy, report copy, feedback copy, themes, offline behavior
- A comparison table separating summary, review, and raw viewing
- Architecture data flow: prompt → exact scope → evidence analysis → Markdown → offline HTML
- Python requirement for `diff-summary`

Add `.diff-summaries/` next to `.reviews/` and `.diffs/` in `.gitignore`.

- [ ] **Step 4: Re-run documentation tests and verify GREEN**

Run the same unittest command; expected PASS.

### Task 7: Forward-test the skill and exercise the report in a real browser

**Files:**
- Temporary only: `/tmp/diff-summary-eval-*`
- Generated and ignored: `.diff-summaries/`

- [ ] **Step 1: Run repository verification before forward tests**

Run:

```bash
PYTHONDONTWRITEBYTECODE=1 python -m unittest discover -s tests
uvx --from pytest pytest -q
python /Users/heechanpark/.codex/skills/.system/skill-creator/scripts/quick_validate.py \
  code-review/skills/diff-summary
npx --yes skills add . -l --full-depth
git diff --check
```

Expected: zero failures, `Skill is valid!`, and `Found 15 skills` including `diff-summary`.

- [ ] **Step 2: Forward-test natural prompt routing with fresh agents**

Create isolated temporary git repositories with small multi-file diffs. Dispatch fresh agents with only the skill path, repository path, and one realistic prompt each:

- `코드를 요약해줘`
- `main..dev 코드를 요약해줘`
- `summarize the last commit`
- `summarize this PR` using a read-only fixture or documented unavailable-PR path

Verify each agent chose `diff-summary`, preserved the requested scope, produced grounded `DS-*` cards, distinguished unknowns, and generated both files. Remove temporary reports and repositories after reviewing the raw artifacts.

- [ ] **Step 3: Open a representative HTML report and test interactions**

Use the browser automation skill against the generated local report. Verify:

1. Card content and category/impact badges render.
2. `Copy Markdown` returns the exact `DS-*` block.
3. Add comment, reload, and confirm persistence.
4. Edit and delete the comment.
5. Add two comments, use sidebar jump, then clear all.
6. Copy report and feedback payload.
7. Change theme and sidebar width, reload, and confirm preferences.
8. Disable or throw from localStorage/clipboard in the page and confirm rendering plus status fallback.
9. Block network requests and confirm no resource failures.

- [ ] **Step 4: Fix every observed gap with a new RED/GREEN test**

For each issue, add the smallest failing automated regression, observe failure, implement the fix, and re-run targeted plus full tests.

### Task 8: Final review, completion audit, meaningful commits, and push

**Files:**
- Review every tracked change from `origin/main...HEAD` and the working tree.

- [ ] **Step 1: Run a spec-compliance review**

Compare every acceptance criterion in `docs/superpowers/specs/2026-07-13-diff-summary-design.md` against current files, tests, discovery output, and browser evidence. Fix missing or extra behavior before continuing.

- [ ] **Step 2: Run an independent code-quality review**

Use `code-review` on the complete diff. Review correctness, injection safety, offline behavior, accessibility, browser state handling, Python portability, trigger overlap, and documentation consistency. Resolve all HIGH/MEDIUM issues and disposition LOW/INFO items explicitly.

- [ ] **Step 3: Run the final verification suite fresh**

Repeat the full commands from Task 7, regenerate a representative HTML file, and repeat the critical browser comment/copy path. Do not rely on previous output.

- [ ] **Step 4: Show the commit plan**

Use explicit paths and propose these logical commits, adjusting only if the final diff proves a different grouping:

```text
1. docs(diff-summary): define the interactive summary workflow
   - docs/superpowers/specs/2026-07-13-diff-summary-design.md
   - docs/superpowers/plans/2026-07-13-diff-summary.md

2. feat(diff-summary): add interactive change summary reports
   - code-review/commands/diff-summary.md
   - code-review/skills/diff-summary/**
   - code-review/.claude-plugin/plugin.json
   - tests/diff_summary/**
   - tests/test_diff_summary_skill_package.py
   - tests/test_code_review_skill_package.py

3. docs(code-review): document diff summary usage
   - .gitignore
   - README.md
   - README.ko.md
   - USAGE.md
   - ARCHITECTURE.md
   - code-review/README.md
   - code-review/README.ko.md
   - tests/test_installation_docs.py
```

- [ ] **Step 5: Commit with explicit staging and push without force**

Force-add only the globally ignored, intentional design/plan files; stage every other group by explicit path. Never use `git add .`, `git add -A`, `--no-verify`, or force push. After each commit, inspect `git status --short`. Then run `git push`; stop and report a non-fast-forward rejection without auto-rebasing.

- [ ] **Step 6: Verify remote completion**

Confirm `git status --short --branch` is clean, `git log --oneline -3` shows the planned commits, and `git rev-parse HEAD` equals `git rev-parse origin/main`. Only then mark the goal complete.
