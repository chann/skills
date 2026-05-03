---
name: code-review-md
description: Use when the user asks to save a code review to a file, write a markdown review report, persist review findings, or generate a review file in `.reviews/`. Trigger on phrases like "review my changes and save", "write the code review", "리뷰 결과 파일로 저장", "마크다운 리뷰 보고서", "/code-review-md". For interactive (no-file) review use the `code-review` skill; for HTML output use `code-review-html`.
---

# Code Review (Markdown Report)

## Overview

Variant of the `code-review` skill that persists findings to `.reviews/<YYYY-MM-DD>_<short-sha>.md`.

**Announce at start:** "I'm using the code-review-md skill to write a markdown review report."

## Workflow

**Before starting, Read the main `code-review` SKILL.md** at `<plugin-root>/skills/code-review/SKILL.md` — the Review Process steps, severity table, language reference mapping, and report markdown template all live there. The variant relies on those sections.

Then follow the **Review Process** in the main SKILL.md exactly — steps 1–3 (gather context, load references, analyze) and step 6 (conversation summary). For step 4, **always write the markdown report** to `.reviews/`. Skip step 5 (HTML).

In short:

1. Determine review scope and run the matching `git diff` (see "Determining Review Scope" in the main SKILL.md).
2. Run `diff_stats.py`, load language-relevant references, and `common-vulnerabilities.md` if security-sensitive.
3. Analyze the diff against the five dimensions and assign severities.
4. Create `.reviews/` if missing and write the report using the markdown template in the main SKILL.md ("Present findings or write the markdown report"). Suggest adding `.reviews/` to `.gitignore` if absent — never modify `.gitignore` automatically.
5. Print a brief conversation summary: total findings by severity, overall risk, file path, top 1–3 findings.

## Filename

`.reviews/<YYYY-MM-DD>_<short-sha>.md` — see "Quick Reference / Filename convention" in the main SKILL.md.

## Language

Match the user's prompt language; see "Report Language" in the main SKILL.md. Add `**Language:** <bcp47>` in the metadata header.

## Red Flags

Same Never/Always lists as the main `<plugin-root>/skills/code-review/SKILL.md`. In particular: never modify `.gitignore` automatically (suggest only); never comment on code outside the diff; default to INFO severity when uncertain.

## Integration

**Pairs with:** `conventional-commit` — review before committing for a final quality gate.
