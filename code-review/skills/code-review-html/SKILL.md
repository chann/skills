---
name: code-review-html
description: Use when the user asks for a styled HTML code review report, a browser-readable review, or both markdown + HTML output. Trigger on phrases like "/code-review-html", "HTML 리뷰 보고서", "styled review report", "review with badges/sidebar". For markdown-only output use `code-review-md`; for in-conversation review use `code-review`.
---

# Code Review (HTML Report)

## Overview

Variant of the `code-review` skill that produces markdown reports **and** a self-contained, interactive HTML report.

The HTML report is **bilingual** (Korean + English with a full-page language toggle, Korean shown by default) and includes: severity badges, syntax highlighting with a light/dark/auto theme and an 8-option code scheme selector, a compact collapsible/resizable sidebar, per-finding "Copy Markdown", per-finding comments stored in the browser, and a "Copy feedback" button that emits a regeneration payload to refine the review.

**Announce at start:** "I'm using the code-review-html skill to generate a bilingual markdown + HTML review report."

## Workflow

**Before starting, Read the main `code-review` SKILL.md** at `<plugin-root>/skills/code-review/SKILL.md` — the Review Process steps, severity table, language reference mapping, and report markdown template all live there. The variant relies on those sections.

Then follow the **Review Process** in the main SKILL.md exactly — steps 1–6 all apply, including HTML generation.

In short:

1. Determine review scope and run the matching `git diff` (see "Determining Review Scope" in the main SKILL.md).
2. Run `diff_stats.py`, load language-relevant references, and `common-vulnerabilities.md` if needed.
3. Analyze the diff against the five dimensions and assign severities. Give every finding a stable `[CR-001]`-style ID.
4. Write **two** markdown files with identical structure (same IDs, same code blocks):
   - `.reviews/<YYYY-MM-DD>_<short-sha>.md` — Korean, `**Language:** ko` (the main report).
   - `.reviews/<YYYY-MM-DD>_<short-sha>.en.md` — English, `**Language:** en`.

   Keep prose concise and professional (see "Writing style" in the main SKILL.md). Suggest adding `.reviews/` to `.gitignore` if absent — never modify `.gitignore` automatically.
5. Run `python <skill-path>/scripts/generate_html_report.py .reviews/<report>.md` (it auto-detects the `.en.md` sibling and merges both into one HTML), then `open` it.
6. Print a brief conversation summary.

The script lives at `<plugin-root>/skills/code-review/scripts/generate_html_report.py` (in the main skill — variants share it).

## Filename

- `.reviews/<YYYY-MM-DD>_<short-sha>.md` — Korean report (primary)
- `.reviews/<YYYY-MM-DD>_<short-sha>.en.md` — English report (translation)
- `.reviews/<YYYY-MM-DD>_<short-sha>.html` — merged bilingual HTML

See "Quick Reference / Filename convention" in the main SKILL.md.

## Language

Bilingual by default — write both Korean and English (see "Bilingual HTML reports" in the main SKILL.md). Set `**Language:** ko` / `en` in each file's header so the generator labels and toggles them correctly, and keep finding IDs identical across the two files so per-finding comments stay attached when the reader switches language. If the user explicitly asks for a single language, write just that file; the generator falls back to a single-language report with the toggle hidden.

## Red Flags

Same Never/Always lists as the main `<plugin-root>/skills/code-review/SKILL.md`. In particular: never modify `.gitignore` automatically (suggest only); never comment on code outside the diff.

## Integration

**Pairs with:** `git-commit` — review before committing for a final quality gate.
