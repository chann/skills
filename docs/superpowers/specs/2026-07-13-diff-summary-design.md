# Diff Summary Skill Design

**Date:** 2026-07-13
**Status:** Approved for implementation

## Problem

The `code-review` plugin can find defects and `diff-viewer` can display raw patches, but neither produces an explanatory report about what changed across code, architecture, patterns, contracts, tests, and operational behavior. Users need that middle layer for prompts such as `코드를 요약해줘`, `main..dev 코드를 요약해줘`, `summarize this diff`, and `what changed between branches`.

The result must be useful without reading every changed line, remain grounded in the selected diff, and support asynchronous review through per-summary comments and Markdown copy actions in a browser-readable HTML report.

## Goals

- Add an installable `diff-summary` skill to the existing `code-review` plugin.
- Automatically trigger on natural Korean and English requests to summarize code or diffs.
- Preserve explicit git ranges exactly, including the semantic distinction between `..` and `...`.
- Analyze major changes across behavior, architecture, data flow, patterns, contracts, dependencies, testing, and operations.
- Write a Markdown source report and a self-contained HTML report under `.diff-summaries/`.
- Give every major summary a stable `DS-001`-style ID, an inline comment thread, and a `Copy Markdown` action.
- Support report-level Markdown copy and feedback export containing the original summaries and reviewer comments.
- Package the runtime inside the `diff-summary` skill so a single-selector install works without sibling-skill files.
- Preserve the existing contracts of `code-review`, `code-review-html`, and `diff-viewer`.

## Non-goals

- Do not turn the summary into a defect review or assign review severities. Users asking for defects should use `code-review`.
- Do not embed the complete raw diff or provide line-range commenting. Users asking to inspect patches should use `diff-viewer`.
- Do not infer runtime, test, deployment, or migration success from code shape alone.
- Do not require a JavaScript build step, package manager, web server, or network access to view the report.
- Do not generate a second translated report unless the user explicitly requests translation in a future extension.

## Placement and Packaging

Add the skill as the fifth member of the `code-review` plugin:

```text
code-review/
├── commands/diff-summary.md
├── skills/diff-summary/
│   ├── SKILL.md
│   ├── agents/openai.yaml
│   ├── scripts/generate_summary_report.py
│   └── assets/summary-template.html
└── .claude-plugin/plugin.json
```

The plugin version moves from `2.2.0` to `2.3.0`. The command wrapper provides `/diff-summary`; Codex and other skill loaders discover the skill through `skills/diff-summary/SKILL.md`. The frontmatter description is the authoritative natural-language trigger surface.

## Skill Boundaries and Triggering

The trigger description must explicitly cover:

- Korean: `코드를 요약해줘`, `변경사항을 요약해줘`, `diff 요약`, `main..dev 코드를 요약해줘`, `브랜치 변경 요약`, `PR 변경 요약`
- English: `summarize the code changes`, `summarize this diff`, `change summary`, `main..dev summary`, `what changed between branches`, `summarize this PR`

It must also state the boundary:

- `diff-summary`: explanatory, evidence-based change summary
- `code-review`: defects, risks, and suggested fixes
- `diff-viewer`: raw browser-readable patch

When a prompt asks both for a summary and a review, run both workflows and keep their output sections distinct rather than silently routing the whole request to one skill.

## Scope Resolution

The skill records both the user-facing scope and the exact command used.

| User intent | Command |
|---|---|
| No explicit scope / current changes | `git diff --no-ext-diff --no-color HEAD` |
| Staged changes | `git diff --no-ext-diff --no-color --staged` |
| Unstaged changes | `git diff --no-ext-diff --no-color` |
| Last commit | `git diff --no-ext-diff --no-color HEAD~1..HEAD` |
| Last N commits | `git diff --no-ext-diff --no-color HEAD~N..HEAD` |
| Explicit range such as `main..dev` | `git diff --no-ext-diff --no-color main..dev` |
| Explicit merge-base range such as `main...dev` | `git diff --no-ext-diff --no-color main...dev` |
| Specific commit | `git show --no-ext-diff --no-color --format=fuller <sha>` |
| Pull request | `gh pr diff <number>` plus `gh pr view <number> --json ...` when available |

An explicit range is opaque user input: validate that its revisions resolve, but never rewrite `..` to `...` or vice versa. Run matching `--stat`, `--numstat`, and `--name-status` commands for verified metadata. Record untracked files separately because ordinary git diff output does not include their contents.

If the scope cannot be resolved, stop before writing a report and show the failing command. If the diff is empty, report the empty scope and do not manufacture summary cards.

## Evidence Collection and Analysis

Collect evidence in this order:

1. Resolve repository root, branch, HEAD, user scope, and exact comparison command.
2. Capture the diff plus `--stat`, `--numstat`, and `--name-status` views.
3. Inspect changed files and nearby repository context only when required to explain a changed symbol, boundary, or test.
4. Inspect relevant tests, manifests, schemas, migrations, and configuration touched by the diff.
5. Separate verified diff evidence from interpretation and explicitly mark unknown runtime outcomes.

Analyze each applicable dimension:

1. Purpose and user-visible impact
2. Behavior and control-flow changes
3. Architecture, boundaries, dependencies, and data flow
4. Patterns, abstractions, conventions, and consistency
5. API, schema, configuration, persistence, and dependency contracts
6. Security, performance, concurrency, and compatibility implications
7. Tests, migrations, deployment, observability, and operational impact
8. File-by-file change map and unresolved questions

Omit dimensions with no meaningful evidence. Do not pad the report with generic statements.

## Markdown Report Contract

Write `.diff-summaries/<YYYY-MM-DD>_<scope-tag>.md` in the prompt language. Use this shape:

```markdown
# Diff Summary Report

**Date:** 2026-07-13
**Repository:** example
**Scope:** main..dev
**Command:** `git diff --no-ext-diff --no-color main..dev`
**HEAD:** a1b2c3d
**Language:** ko

## Executive Summary

| Metric | Value |
|---|---|
| Files changed | 12 |
| Lines added | +340 |
| Lines removed | -92 |
| Primary areas | API, storage, tests |

Two or three evidence-based sentences describing the change set.

## Major Changes

### Architecture

#### [DS-001] Split report generation from diff collection
**Category:** Architecture
**Impact:** High
**Files:** `src/report.py`, `src/diff.py`

Concise description of what changed and why it matters.

**Evidence:** `ReportBuilder` now consumes a `DiffContext` instead of invoking git.

**Implications:** Callers can test report construction independently.

## Change Map

| File | Status | Role | Key change |
|---|---|---|---|

## Verification and Unknowns

- Verified evidence
- Unverified runtime or deployment behavior

_Generated by diff-summary skill · 2026-07-13 12:00 KST_
```

Every `#### [DS-NNN]` block is one interactive summary card. IDs are unique and sequential in report order. Categories use a controlled set: `Overview`, `Behavior`, `Architecture`, `Pattern`, `API`, `Data`, `Dependency`, `Security`, `Performance`, `Test`, `Operations`, and `Compatibility`. Impact is descriptive (`High`, `Medium`, `Low`, or `Informational`), not a review severity.

Every card cites files, symbols, configuration keys, or diff evidence. Cards may explain risks or unknowns, but do not prescribe fixes unless the user also asked for recommendations.

## HTML Report and Interaction Model

`generate_summary_report.py` converts the Markdown report into `.html` using only the Python standard library and a bundled template.

The page includes:

- Responsive summary dashboard with scope, metrics, categories, and change-map navigation
- Collapsible and resizable sidebar with section navigation and comment list
- Light, dark, and system themes stored as a guarded user preference
- Category and impact badges on every summary card
- Expand/collapse controls for long cards
- Per-card `Copy Markdown` and `Comment` actions placed after card content
- Inline comment creation, editing, deletion, count badges, and sidebar jump links
- `Clear comments`, `Copy report`, and `Copy feedback` controls
- Clipboard API with a checked textarea fallback
- Print styling that expands cards and hides controls
- Plain, escaped code blocks and styled diff blocks without external CDN assets

Comments are stored as `{id, summaryId, text, createdAt, updatedAt}`. The key is scoped to a stable report fingerprint containing repository identity, exact scope, HEAD, and a normalized summary-card content hash that excludes volatile date/footer metadata. Regenerating the same summaries reuses its thread; a materially changed report gets a new thread. All local-storage reads and writes are guarded so restricted `file://` environments do not prevent the report from rendering.

Raw Markdown and card data are embedded as JSON with `<`, `>`, `&`, Unicode line separators, and `</script>` sequences escaped. Markdown fence language tokens are allowlisted before insertion into attributes. User text is inserted with `textContent`, never `innerHTML`.

## Generator Responsibilities

The generator is intentionally presentation-only. It:

- Parses metadata, headings, tables, lists, fenced code, and `DS-*` cards.
- Rejects duplicate or malformed `DS-*` IDs with a clear error.
- Extracts the exact Markdown slice for each card.
- Builds a deterministic comment scope and safe JSON payload.
- Applies the HTML template in a single replacement pass so report content cannot be interpreted as a template token.
- Writes the sibling `.html` path by default and accepts `-o`, `--theme`, and `--open` options.

It does not invoke git or generate analytical prose. The skill workflow owns evidence collection and report authoring.

## Error Handling

- Not a git repository: stop with a direct explanation.
- Invalid revision/range: show the exact failed revision check or git command.
- Empty diff: summarize the empty state in the conversation; do not create placeholder cards.
- Missing or malformed Markdown metadata: exit non-zero with the field name.
- Missing template or unwritable output: exit non-zero without partial output.
- Duplicate card ID: exit non-zero and list the duplicate ID.
- Browser open failure: retain the generated files and report the path and open error.
- Clipboard or local-storage restriction: keep the report usable and show an unobtrusive status message.

## Documentation and Compatibility

Update the plugin and root English/Korean READMEs, `USAGE.md`, and `ARCHITECTURE.md` with:

- The fifth code-review skill and `/diff-summary` command
- Correct repeated `--skill diff-summary` selector examples
- Supported prompt and scope examples
- `.diff-summaries/` output files and interaction features
- The distinction among summary, review, and raw diff viewing

Add `.diff-summaries/` to this repository's `.gitignore` because it is a generated local artifact. The skill only suggests this ignore entry in target repositories and never edits their `.gitignore` automatically.

## Verification Strategy

Use test-driven development for every generator behavior.

1. Package tests verify the skill, command, script, template, UI metadata, plugin version, and trigger phrases.
2. Parser tests cover metadata, cards, tables, code, Unicode, malformed IDs, and duplicate IDs.
3. Assembly tests cover per-card controls, action placement, safe JSON, deterministic scopes, single-pass token replacement, and absence of external assets.
4. CLI tests generate a real HTML file and verify failure behavior without partial output.
5. Browser tests exercise card copy, add/edit/delete/clear comments, persistence after reload, report copy, feedback copy, theme persistence, and restricted-storage fallback.
6. Skill-forward tests ask a fresh agent to handle at least:
   - `코드를 요약해줘`
   - `main..dev 코드를 요약해줘`
   - `summarize the last commit`
   - `summarize this PR`
7. Repository gates run targeted tests, the full unittest suite, the pytest suite through `uvx`, skill validation, `npx skills` discovery, `git diff --check`, and a final code review.

## Acceptance Criteria

The feature is complete only when:

- `diff-summary` appears in skill discovery and can be installed by its exact selector.
- Natural Korean and English summary prompts match its frontmatter description without conflating review or raw viewing.
- Explicit two-dot and three-dot ranges are preserved and recorded.
- A realistic multi-file diff produces useful code, architecture, pattern, contract, test, and operational summaries where evidence exists.
- Every `DS-*` card supports Markdown copy and persistent comment CRUD in the generated HTML.
- The report, copy controls, and comments work from a local HTML file without network access.
- Injection and malformed-report tests pass.
- Existing code-review and diff-viewer contracts and tests remain green.
- Documentation, plugin version, validation, commit, and push are complete.
