---
name: code-review
description: Use when the user asks to review code, review changes, review a commit, review a PR, audit code quality, check for security issues, or generate a code review report. Trigger on phrases like "review my changes", "코드 리뷰", "check my code", "review the last commit", "what do you think of this diff", "compare branches", "code audit" — even if they don't say "code review" explicitly.
---

# Code Review Skill

## Overview

Structured code review from git diffs. Analyzes changes for correctness, security, complexity, maintainability, and language-specific best practices, then presents findings either inline or as a persistent report.

**Core principle:** Diff in → severity-tagged findings out, scoped strictly to what changed.

**Announce at start:** "I'm using the code-review skill to review the requested changes."

## Commands

| Command | Output | When to use |
|---|---|---|
| `/code-review` (or implicit trigger) | Findings shown in conversation; no file | Quick interactive review |
| `/code-review:md`, `/code-review:markdown` | Markdown file at `.reviews/<date>_<sha>.md` | Persistent record, share via git |
| `/code-review:html` | Markdown file + self-contained HTML | Browser-readable report with badges, syntax highlighting, sidebar nav |

## Command Examples

### `/code-review` — interactive

```
User: review my changes
→ git diff && git diff --staged
→ Analyze
→ Print findings in conversation; write nothing
```

```
User: 마지막 커밋 코드 리뷰해줘
→ git diff HEAD~1..HEAD
→ Analyze; output narrative in Korean (section headings translated)
→ Print findings in conversation
```

### `/code-review:md` — markdown report

```
User: /code-review:md review staged changes
→ git diff --staged
→ Analyze
→ mkdir -p .reviews/
→ Write .reviews/2026-05-03_staged.md
→ Print 1-3 top findings + path to report
```

```
User: /code-review:markdown review branch feature-auth compared to main
→ git diff main...feature-auth
→ Analyze
→ Write .reviews/2026-05-03_<latest-sha>.md
→ Suggest adding `.reviews/` to .gitignore (do NOT modify it)
```

### `/code-review:html` — HTML + markdown

```
User: /code-review:html review PR #42
→ gh pr diff 42
→ diff_stats.py reports has_security_sensitive_files: true
→ Load python.md + common-vulnerabilities.md
→ Analyze; find SQL injection (CRITICAL)
→ Write .reviews/2026-05-03_a1b2c3d.md
→ python <skill-path>/scripts/generate_html_report.py .reviews/2026-05-03_a1b2c3d.md
→ open .reviews/2026-05-03_a1b2c3d.html
→ Print summary in conversation
```

## Determining Review Scope

Parse the user's request to figure out what code to review, then run the matching git command:

| User intent | Git command |
|---|---|
| "review my changes" / no specific scope | `git diff` (unstaged) + `git diff --staged` (staged) |
| "review staged changes" | `git diff --staged` |
| "review last commit" | `git diff HEAD~1..HEAD` |
| "review commit `<sha>`" | `git diff <sha>~1..<sha>` |
| "review last N commits" | `git diff HEAD~N..HEAD` |
| "review branch X" / "compare to main" | `git diff main...<branch>` (three-dot merge-base) |
| "review PR #N" | `gh pr diff N` |

If the user's intent is ambiguous, default to reviewing staged + unstaged changes. If there are no changes at all, tell the user and suggest possible causes (forgot to stage? wrong branch?).

Get the short SHA for the report filename:
- For a specific commit: use that commit's short SHA
- For a range: use the latest commit's short SHA
- For staged/unstaged changes with no commit: use `staged` or `working`

## Review Process

Follow these steps in order:

### 1. Gather context

Run the appropriate git diff command. Then run the diff stats helper to get a machine-readable summary:

```bash
git diff [range] --numstat | python <skill-path>/scripts/diff_stats.py
```

This outputs JSON with files changed, languages detected, and whether security-sensitive files were touched.

### 2. Load references

Based on the languages detected by `diff_stats.py`, read the relevant reference files. Only load what's needed — never read all of them at once:

- `.py` files → read `references/python.md`
- `.js`, `.ts`, `.jsx`, `.tsx` files → read `references/javascript-typescript.md`
- `.go` files → read `references/go.md` (if it exists)
- `.rs` files → read `references/rust.md` (if it exists)
- `.java`, `.kt` files → read `references/java.md` (if it exists)

Always read `references/review-criteria.md` for the review framework and severity definitions.

If `diff_stats.py` reports `has_security_sensitive_files: true`, also read `references/common-vulnerabilities.md`.

### 3. Analyze the diff

Read each changed file's diff and analyze against five dimensions:

1. **Correctness** — Does the code do what the author intended? Logic errors, edge cases, type mismatches, error handling gaps.
2. **Security** — Injection risks, auth gaps, sensitive data exposure, insecure crypto, input validation.
3. **Complexity & Consistency** — Does this increase cognitive load? Does it break existing patterns or naming conventions?
4. **Maintainability** — Will future developers understand this? Tight coupling, missing docs for public APIs, magic values, testability.
5. **Best Practices** — Language/framework-specific idioms and anti-patterns (guided by the loaded reference files).

For each finding, assign a severity:

| Severity | Meaning | Action required |
|----------|---------|-----------------|
| **CRITICAL** | Data loss, security breach, or crash in production | Must fix before merge |
| **HIGH** | Bug, vulnerability, or serious design flaw | Should fix before merge |
| **MEDIUM** | Code smell, inconsistency, moderate risk | Recommended fix |
| **LOW** | Style, naming, minor improvement | Nice to have |
| **INFO** | Positive observation or contextual note | No action needed |

Every finding must reference a specific file and line range. Show the problematic code and a suggested fix. If uncertain about something, use INFO severity and frame it as a question rather than asserting a problem that may not exist.

### 4. Present findings or write the markdown report

**Default (bare `/code-review`):** Present the review using the template format below directly in the conversation. Do NOT write any files.

**When invoked via `/code-review:md`, `/code-review:markdown`, or `/code-review:html`:** Create the `.reviews/` directory in the repository root if it doesn't exist. Write the report file following this exact template:

```markdown
# Code Review Report

**Date:** YYYY-MM-DD
**Reviewer:** Claude (automated)
**Scope:** [e.g., "Staged changes", "Commits a1b2c3d..f4e5d6a on branch feature-auth"]
**Repository:** [repo name]

---

## Executive Summary

| Metric | Value |
|--------|-------|
| Files changed | N |
| Lines added | +N |
| Lines removed | -N |
| Languages | Python, TypeScript |
| Findings | N critical, N high, N medium, N low |
| Overall risk | LOW / MEDIUM / HIGH / CRITICAL |

[2-3 sentence summary of the overall quality and the most important observations.]

---

## Findings

### CRITICAL

#### [CR-001] Short title describing the finding
**File:** `path/to/file.py` (lines 42-58)
**Category:** Security | Correctness | Complexity | Maintainability | Best Practice

[Description of the issue, why it matters, and what the risk is.]

**Current code:**
\```python
# the problematic code
\```

**Suggested fix:**
\```python
# the recommended approach
\```

---

[Continue with HIGH, MEDIUM, LOW sections using the same structure.
Omit any severity section that has zero findings.]

---

## Positive Observations

- [Things the code does well — good patterns, clean abstractions, thorough testing, etc.]

---

## File-by-File Summary

| File | Status | Findings | Risk |
|------|--------|----------|------|
| `src/auth.py` | Modified | CR-001 (CRITICAL), CR-003 (MEDIUM) | HIGH |
| `tests/test_auth.py` | Modified | None | LOW |

---

_Generated by code-review skill · YYYY-MM-DD HH:MM UTC_
```

Save to: `.reviews/<YYYY-MM-DD>_<short-sha>.md`

### 5. Generate HTML (`/code-review:html` only)

Only when invoked via `/code-review:html`. Run:

```bash
python <skill-path>/scripts/generate_html_report.py .reviews/<report>.md
```

This produces a self-contained `.html` file next to the markdown, with severity badges, collapsible sections, and a sidebar navigation. Then open it:

```bash
open .reviews/<report>.html
```

### 6. Present summary

After completing the review, show the user a brief conversation summary:
- Total findings by severity
- Overall risk assessment
- Path to the report file(s) (if files were generated)
- The top 1-3 most important findings inline (so they get the critical stuff without opening the file)

## Report Language

Write the report in the same language as the user's prompt. If the user writes in Korean, the report should be in Korean. If in English, write in English. Default to English when the language is ambiguous.

What to translate:
- Section headings (e.g., "Executive Summary" → "요약", "Findings" → "발견 사항")
- Finding descriptions, summaries, and the overall narrative
- Table headers and metadata labels

What stays in English always:
- Finding IDs: `CR-001`, `CR-002`, etc.
- Severity labels: `CRITICAL`, `HIGH`, `MEDIUM`, `LOW`, `INFO`
- Code snippets (code is code)
- File paths and technical identifiers

Add a `**Language:**` field in the report metadata header so the HTML generator can set the correct `lang` attribute:

```markdown
**Language:** ko
```

Use the [BCP 47 language tag](https://en.wikipedia.org/wiki/IETF_language_tag): `en`, `ko`, `ja`, `zh`, etc.

## Quick Reference

**Filename convention:**
- Commit-based: `.reviews/2026-04-08_a1b2c3d.md`
- Staged: `.reviews/2026-04-08_staged.md`
- Working tree: `.reviews/2026-04-08_working.md`

**Report language:** Match the user's prompt language. Translate section headings + narrative; keep finding IDs (`CR-001`), severity labels, code, and file paths in English. Add `**Language:** <bcp47>` field so the HTML generator sets `lang` correctly.

**Large diffs (>1000 lines):** Focus on CRITICAL/HIGH. Group similar MEDIUM/LOW findings by pattern ("12 instances of unused imports") rather than listing each one separately.

## Common Mistakes

**Generic findings without location**
- **Problem:** "Consider adding error handling" with no file/line
- **Fix:** Every finding cites file + line range, shows current code, suggests fix

**Reviewing unchanged code**
- **Problem:** Comment on code outside the diff
- **Fix:** Scope is the diff. Don't expand to the whole repo.

**Manufactured findings on trivial diffs**
- **Problem:** Inventing issues for whitespace/version-bump-only diffs
- **Fix:** Call it trivial in 2-3 lines. Don't pad.

**Loading every reference file**
- **Problem:** Reading `python.md` when the diff is JS-only
- **Fix:** Only load references for languages reported by `diff_stats.py`

**False positives stated as facts**
- **Problem:** "This is a bug" when you cannot verify
- **Fix:** Use INFO + a question: "This might cause X under Y conditions — worth verifying?"

**Missing positive observations**
- **Problem:** Only listing issues; reviewers tune out
- **Fix:** Always include the Positive Observations section, even on small diffs

## Red Flags

**Never:**
- Write files for bare `/code-review` (conversation only)
- Modify `.gitignore` automatically (suggest, don't apply)
- Comment on code outside the diff
- Skip the Positive Observations section
- Manufacture findings to fill space

**Always:**
- Cite file + line range in every finding
- Show before/after code
- Default to INFO severity when uncertain
- Match the user's prompt language for narrative
- Suggest adding `.reviews/` to `.gitignore` if absent

## Integration

**Pairs with:**
- **conventional-commit** — Review before committing for a final quality gate
- Triggers via plugin commands; runs against any `git diff` output, so works on any repo with git history
