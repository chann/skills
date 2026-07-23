---
name: code-review-md
description: Use when the user asks for a Markdown-only code review artifact, a review file without HTML, or a review report in `.reviews/` with no browser output. Trigger on phrases like "review my changes and save as markdown", "마크다운 리뷰 보고서만", "리뷰 결과 마크다운 파일로 저장", "markdown-only review", "/code-review-md". For the default markdown + HTML review use the `code-review` skill.
---

# Code Review (Markdown Report)

## Overview

Variant of the `code-review` skill that persists findings to `.reviews/<YYYY-MM-DD>_<short-sha>.md` only, with no HTML report and no browser open.

## Workflow

**Before starting, Read the main `code-review` SKILL.md** at `<plugin-root>/skills/code-review/SKILL.md` — the Review Process steps, severity table, language reference mapping, and report markdown template all live there. The variant relies on those sections.

The main skill's **Evidence-first writing contract** and conditional-section rules are authoritative. Do not restate or weaken them here.

Then follow the **Review Process** in the main SKILL.md exactly — steps 1–4 (gather context, load references, analyze, write the report) and step 6 (handoff). Skip step 5 (HTML).

In short:

1. Determine review scope and run the matching `git diff` (see "Determining Review Scope" in the main SKILL.md).
2. Run `diff_stats.py`, load language-relevant references, and `common-vulnerabilities.md` if security-sensitive.
3. Analyze the diff against the five dimensions and assign severities.
4. In this persisted Markdown mode, create `.reviews/` if missing and write the report using the markdown template in the main SKILL.md ("Write the markdown report").
5. Use a fact-only handoff containing finding counts by severity, overall risk, the Markdown artifact path, and fresh verification. Do not repeat report prose or promise a fixed finding count.

Include a `.reviews/` ignore suggestion in this handoff only when artifacts were generated and `.reviews/` is not ignored. Never modify `.gitignore` automatically.

## Filename

`.reviews/<YYYY-MM-DD>_<short-sha>.md` — see "Quick Reference / Filename convention" in the main SKILL.md.

## Language

Match the user's prompt language; see "Report Language" in the main SKILL.md. Preserve its parser-significant English metadata keys and add `**Language:** <bcp47>` in the metadata header.

## Red Flags

Same Never/Always lists as the main `<plugin-root>/skills/code-review/SKILL.md`. In particular: never modify `.gitignore` automatically (suggest only), never comment on code outside the diff, and never use INFO for uncertainty or praise.

## Integration

**Pairs with:** `git-commit` — review before committing for a final quality gate.
