---
name: code-review
description: >
  Review code changes in git repositories and generate persistent markdown/HTML report files.
  Analyzes diffs for correctness, security, complexity, consistency, maintainability, and
  language-specific best practices. Produces date-stamped reports (e.g., 2026-04-08_a1b2c3d.md)
  in a .reviews/ directory. Use this skill when the user asks to review code, review changes,
  review a commit, review a PR, audit code quality, check for security issues, or generate a
  code review report. Trigger on phrases like "review my changes", "코드 리뷰", "check my code",
  "review the last commit", "what do you think of this diff", "compare branches", "code audit",
  or any request for a written review of code changes — even if they don't say "code review"
  explicitly. Also trigger when the user asks for a review report or wants persistent review output.
---

# Code Review Skill

Generate structured, persistent code review reports from git diffs. Unlike conversational code review, this skill produces dated markdown and HTML report files that can be archived, shared, and referenced later.

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

### 4. Write the markdown report

Create the `.reviews/` directory in the repository root if it doesn't exist. Write the report following this exact template:

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

### 5. Generate HTML (optional)

Generate HTML when the user explicitly requests it, or when they say "report" or "html". Run:

```bash
python <skill-path>/scripts/generate_html_report.py .reviews/<report>.md
```

This produces a self-contained `.html` file next to the markdown, with severity badges, collapsible sections, and a sidebar navigation. Then open it:

```bash
open .reviews/<report>.html
```

### 6. Present summary

After writing the report, show the user a brief conversation summary:
- Total findings by severity
- Overall risk assessment
- Path to the report file(s)
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

## Behavior Guidelines

**Be specific, not generic.** Every finding must point to a file and line range. "Consider adding error handling" is useless without specifying where and why. Show the code, explain the risk, suggest the fix.

**Balance criticism with praise.** The Positive Observations section is not optional. Balanced feedback is more actionable because reviewers who only criticize get tuned out.

**Only review what changed.** Do not comment on existing code that wasn't part of the diff. The scope is the diff, not the entire codebase.

**Minimize false positives.** If you're not confident something is an issue, use INFO severity and phrase it as a question: "This might cause X under Y conditions — worth verifying?" A false alarm wastes more time than a missed suggestion.

**Handle large diffs gracefully.** For diffs over ~1000 changed lines, focus on CRITICAL and HIGH findings. Group similar MEDIUM/LOW findings by pattern (e.g., "12 instances of unused imports") rather than listing each one separately.

**Trivial changes are OK to call trivial.** If the diff is only whitespace, comments, version bumps, or dependency updates, say so and produce a short report. Don't manufacture findings to fill space.

**File naming convention:**
- Commit-based: `.reviews/2026-04-08_a1b2c3d.md`
- Staged changes: `.reviews/2026-04-08_staged.md`
- Working tree: `.reviews/2026-04-08_working.md`

**Suggest adding `.reviews/` to `.gitignore`** if it's not already there, but don't modify `.gitignore` automatically.
