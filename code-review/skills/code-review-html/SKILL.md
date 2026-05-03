---
name: code-review-html
description: Use when the user asks for a styled HTML code review report, a browser-readable review, or both markdown + HTML output. Trigger on phrases like "/code-review-html", "HTML 리뷰 보고서", "styled review report", "review with badges/sidebar". For markdown-only output use `code-review-md`; for in-conversation review use `code-review`.
---

# Code Review (HTML Report)

## Overview

Variant of the `code-review` skill that produces a markdown report **and** a self-contained HTML report (severity badges, syntax highlighting, sidebar nav).

**Announce at start:** "I'm using the code-review-html skill to generate a markdown + HTML review report."

## Workflow

**Before starting, Read the main `code-review` SKILL.md** at `<plugin-root>/skills/code-review/SKILL.md` — the Review Process steps, severity table, language reference mapping, and report markdown template all live there. The variant relies on those sections.

Then follow the **Review Process** in the main SKILL.md exactly — steps 1–6 all apply, including HTML generation.

In short:

1. Determine review scope and run the matching `git diff` (see "Determining Review Scope" in the main SKILL.md).
2. Run `diff_stats.py`, load language-relevant references, and `common-vulnerabilities.md` if needed.
3. Analyze the diff against the five dimensions and assign severities.
4. Write `.reviews/<YYYY-MM-DD>_<short-sha>.md` using the template. Suggest adding `.reviews/` to `.gitignore` if absent — never modify `.gitignore` automatically.
5. Run `python <skill-path>/scripts/generate_html_report.py .reviews/<report>.md` to produce the `.html` file, then `open` it.
6. Print a brief conversation summary.

The script lives at `<plugin-root>/skills/code-review/scripts/generate_html_report.py` (in the main skill — variants share it).

## Filename

`.reviews/<YYYY-MM-DD>_<short-sha>.md` and `.reviews/<YYYY-MM-DD>_<short-sha>.html` — see "Quick Reference / Filename convention" in the main SKILL.md.

## Language

Match the user's prompt language; see "Report Language" in the main SKILL.md. Set `**Language:** <bcp47>` in the metadata header so the HTML generator emits the correct `lang` attribute.

## Red Flags

Same Never/Always lists as the main `<plugin-root>/skills/code-review/SKILL.md`. In particular: never modify `.gitignore` automatically (suggest only); never comment on code outside the diff.

## Integration

**Pairs with:** `conventional-commit` — review before committing for a final quality gate.
