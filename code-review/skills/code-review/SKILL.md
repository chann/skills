---
name: code-review
description: Use when the user asks to review code, review changes, review a commit, review a PR, audit code quality, check for security issues, or generate a code review report. Trigger on phrases like "review my changes", "코드 리뷰", "check my code", "review the last commit", "what do you think of this diff", "compare branches", "code audit", "HTML 리뷰 보고서", "styled review report" — even if they don't say "code review" explicitly. Produces severity-tagged findings as a Markdown report plus a self-contained bilingual HTML report under `.reviews/`, opened in a browser. For a Markdown-only artifact use `code-review-md`.
---

# Code Review Skill

## Overview

Structured code review from git diffs. Analyzes changes for correctness, security, complexity, maintainability, and language-specific best practices, then persists findings as a Markdown report **and** a self-contained, interactive HTML report — the same artifact pattern as `diff-summary` and `diff-viewer`.

The HTML report is **bilingual** (Korean + English with a full-page language toggle, Korean shown by default) and includes: severity badges, syntax highlighting with a light/dark/auto theme and an 8-option code scheme selector, a compact collapsible/resizable sidebar, per-finding "Copy Markdown", per-finding comments stored in the browser, and a "Copy feedback" button that emits a regeneration payload to refine the review.

**Core principle:** Diff in → severity-tagged findings out, scoped strictly to what changed.

## Commands

| Command | Skill | Output | When to use |
|---|---|---|---|
| `/code-review [scope]` (or implicit trigger) | `code-review` | Markdown report + bilingual HTML under `.reviews/`, opened in browser | Default review |
| `/code-review-md [scope]` | `code-review-md` | Markdown file at `.reviews/<date>_<sha>.md` (no HTML) | Markdown-only record, share via git |

## Command Examples

### `/code-review` — markdown + HTML

```
User: /code-review review PR #42
→ gh pr diff 42
→ diff_stats.py reports has_security_sensitive_files: true
→ Load python.md + common-vulnerabilities.md
→ Analyze; find SQL injection (CRITICAL)
→ Write .reviews/2026-05-03_a1b2c3d.md      (Korean, **Language:** ko)
→ Write .reviews/2026-05-03_a1b2c3d.en.md   (English, same IDs/structure)
→ python <skill-path>/scripts/generate_html_report.py .reviews/2026-05-03_a1b2c3d.md
→ open .reviews/2026-05-03_a1b2c3d.html     (Korean shown by default; toggle to English)
→ Report finding counts, risk, artifact paths, fresh verification, and browser-open result
```

```
User: 마지막 커밋 코드 리뷰해줘
→ git diff HEAD~1..HEAD
→ Analyze; write the Korean report and its English sibling
→ Generate + open the bilingual HTML report
→ Report finding counts, risk, artifact paths, fresh verification, and browser-open result
```

### `/code-review-md` — markdown only

```
User: /code-review-md review staged changes
→ git diff --staged
→ Analyze
→ mkdir -p .reviews/
→ Write .reviews/2026-05-03_staged.md
→ Report finding counts, risk, report path, and fresh verification
→ If `.reviews/` is not ignored, suggest adding it to .gitignore (do NOT modify it)
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
| **INFO** | Verified context that materially affects a review decision but requires no code change | No action needed |

Never use INFO solely for uncertainty or praise. Missing evidence belongs under one specific **Open Questions** item only when it changes severity or action; otherwise omit it.

**Every finding needs a stable ID** in its title: `#### [CR-001] ...`, `[CR-002]`, and so on. The HTML report keys per-finding comments to this ID, so the **same ID must mark the same finding in both language files** (see Report Language). IDs stay in English; never renumber them between languages.

### Evidence-first writing contract

This contract is authoritative for Markdown and HTML reviews.

- For every actionable finding, write in this order: **observed behavior** → **practical consequence** → **smallest justified correction**.
- Cite the changed path and line before making the claim, and quote only the smallest excerpt needed to establish the evidence.
- State verified facts directly. Prefix a consequential inference with `Inference:` and tie it to the cited evidence.
- Keep prose proportional to the evidence. Do not restate code, repeat a conclusion, manufacture INFO items, or add generic praise such as "solid", "robust", "clean", or "well-structured".
- When there are no actionable findings, state that directly and include only material residual risks or verification gaps.
- Do not add an announcement, generic preface, congratulations, or an overall-quality claim in either output mode.

#### Persisted report modes (`/code-review` and `/code-review-md`)

- Start the report with its title and parser-significant metadata, then present findings.
- Use a fact-only handoff after generation: finding counts by severity, overall risk, generated artifact paths, fresh verification, and the browser-open result or warning for HTML.
- Do not repeat report prose or promise a fixed finding count.
- The `.reviews/` ignore suggestion is allowed in this handoff only when persisted artifacts were generated and `.reviews/` is not ignored.

### 4. Write the markdown report

Create the `.reviews/` directory in the repository root if it doesn't exist. Use this minimal report shape, omitting zero-finding severity headings:

```markdown
# Code Review Report

**Date:** YYYY-MM-DD
**Reviewer:** automated review
**Scope:** [e.g., "Staged changes", "Commits a1b2c3d..f4e5d6a on branch feature-auth"]
**Repository:** [repo name]
**Language:** en
**Risk:** LOW / MEDIUM / HIGH / CRITICAL
**Findings:** N critical, N high, N medium, N low, N info

## Findings

### HIGH

#### [CR-001] Short title describing the finding
**File:** `path/to/file.py` (lines 42-58)
**Category:** Security | Correctness | Complexity | Maintainability | Best Practice

**Evidence excerpt:**
\```python
# smallest excerpt needed to support the claim
\```

**Observed behavior:** [What the changed code demonstrably does.]
**Practical consequence:** [The concrete failure mode, risk, or maintenance cost.]
**Smallest justified correction:** [The narrowest change supported by the evidence.]
```

### Conditional sections

- **Decision Summary:** Include only when a cross-cutting risk needs one non-repeated decision statement.
- **Positive Observations:** Include only when a concrete, evidenced pattern lowers risk or review effort.
- **Open Questions:** Include only when missing evidence changes severity or action; keep it to one specific item for that gap.
- **File Summary:** Include only when multi-file navigation helps the reader without repeating findings.

Omit filler, empty headings, and any conclusion already stated in a finding.

Save to: `.reviews/<YYYY-MM-DD>_<short-sha>.md`

### 5. Generate HTML (default; skip for `/code-review-md`)

Default for `/code-review` and implicit triggers; skip this step only when invoked via the `code-review-md` skill / `/code-review-md`. The HTML report is **bilingual**: write a Korean report and an English report (see Report Language), then merge them into one HTML file.

Filenames — primary Korean report plus an `.en.md` sibling with identical structure (same finding IDs, same code blocks):

```
.reviews/<YYYY-MM-DD>_<short-sha>.md      # Korean (main)
.reviews/<YYYY-MM-DD>_<short-sha>.en.md   # English
```

Run the generator on the primary file; it auto-detects the `.en.md` sibling and emits one self-contained HTML:

```bash
python <skill-path>/scripts/generate_html_report.py .reviews/<report>.md
open .reviews/<report>.html
```

The HTML includes: a full-page language toggle (Korean shown by default), light/dark/auto theme + code syntax scheme selector, a compact collapsible sidebar, per-finding "Copy Markdown", per-finding comments (stored in the browser), and a "Copy feedback" button that produces a regeneration payload — paste it back into a new `/code-review` run to revise the review against the reviewer's comments.

If only one language file exists, the generator still works and the language toggle is hidden (single-language fallback). Pass `--alt <path>` to point at a translation explicitly, or `--theme`/`--code-scheme` to change the defaults.

### 6. Finish by output mode

- **Markdown + HTML (`/code-review`):** Apply the fact-only handoff above, including the browser-open result or warning. The only permitted addition is the conditional `.reviews/` ignore suggestion.
- **Markdown only (`/code-review-md`):** Apply the same fact-only handoff without HTML artifact or browser-open facts.

## Report Language

Write the report in the same language as the user's prompt. If the user writes in Korean, the report should be in Korean. If in English, write in English. Default to English when the language is ambiguous.

Translate narrative headings, finding descriptions, conditional prose, and table headers or values when appropriate.

Keep these parser-significant metadata keys exactly in English: `Date`, `Reviewer`, `Scope`, `Repository`, and `Language`. Translate their values when appropriate, and set `**Language:** ko` for a Korean report.

What stays in English always:
- Parser-significant metadata keys: `Date`, `Reviewer`, `Scope`, `Repository`, `Language`
- Finding IDs: `CR-001`, `CR-002`, etc.
- Severity labels: `CRITICAL`, `HIGH`, `MEDIUM`, `LOW`, `INFO`
- Code snippets (code is code)
- File paths and technical identifiers

Add a `**Language:**` field in the report metadata header so the HTML generator can set the correct `lang` attribute:

```markdown
**Language:** ko
```

Use the [BCP 47 language tag](https://en.wikipedia.org/wiki/IETF_language_tag): `en`, `ko`, `ja`, `zh`, etc.

### Bilingual HTML reports (`/code-review`)

The HTML report is **bilingual by default**: produce a Korean report and an English report so the reader can toggle languages. Korean is the default displayed language.

- Write both files with **identical structure** — same headings, same finding IDs (`[CR-001]`), same code blocks. Only the prose (titles, descriptions, summaries, table labels) is translated; code, IDs, file paths, and severity labels are shared verbatim.
- Set the `**Language:**` header in each file (`ko` in the primary, `en` in the `.en.md`).
- The primary file carries the `<YYYY-MM-DD>_<short-sha>.md` name; the translation adds the language suffix (`.en.md`).
- Per-finding comments in the HTML are keyed by finding ID, so keeping IDs aligned across both files is what lets a comment stay attached when the reader switches language.

If the user explicitly asks for a single language, write just that one file — the generator falls back to a single-language report with no toggle.

## Quick Reference

**Filename convention:**
- Commit-based: `.reviews/2026-04-08_a1b2c3d.md`
- Staged: `.reviews/2026-04-08_staged.md`
- Working tree: `.reviews/2026-04-08_working.md`

**Report language:** Match the user's prompt language for narrative prose. Keep `Date`, `Reviewer`, `Scope`, `Repository`, and `Language` metadata keys in English; keep finding IDs (`CR-001`), severity labels, code, and file paths in English. Add `**Language:** <bcp47>` so the HTML generator sets `lang` correctly.

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
- **Fix:** State the verified no-findings result directly. Don't pad.

**Loading every reference file**
- **Problem:** Reading `python.md` when the diff is JS-only
- **Fix:** Only load references for languages reported by `diff_stats.py`

**False positives stated as facts**
- **Problem:** "This is a bug" when you cannot verify
- **Fix:** If the missing evidence changes severity or action, ask one specific question under **Open Questions**; otherwise omit the claim.

**Generic praise as a finding**
- **Problem:** Praise consumes attention without changing a review decision
- **Fix:** Omit it unless a concrete pattern demonstrably lowers risk or review effort.

## Red Flags

**Never:**
- Generate an HTML report for `/code-review-md` (markdown only)
- Modify `.gitignore` automatically (suggest, don't apply)
- Comment on code outside the diff
- Manufacture findings to fill space
- Use INFO as a substitute for evidence

**Always:**
- Cite file + line range in every finding
- Quote only the smallest evidence excerpt and propose the smallest justified correction
- Match the user's prompt language for narrative
- Keep parser-significant metadata keys in English for persisted reports

## Integration

**Pairs with:**
- **git-commit** — Review before committing for a final quality gate
- Triggers via plugin commands; runs against any `git diff` output, so works on any repo with git history
