---
name: code-review-md
description: Use when the user asks to save a code review to a file, write a markdown review report, persist review findings, or generate a review file in `.reviews/`. Trigger on phrases like "review my changes and save", "write the code review", "리뷰 결과 파일로 저장", "마크다운 리뷰 보고서", "/code-review-md". For interactive (no-file) review use the `code-review` skill; for HTML output use `code-review-html`.
---

# Code Review (Markdown Report)

## Overview

Variant of the `code-review` skill that persists findings to `.reviews/<YYYY-MM-DD>_<short-sha>.md`.

## Workflow

**Before starting, Read the main `code-review` SKILL.md** at `<plugin-root>/skills/code-review/SKILL.md` — the Review Process steps, severity table, language reference mapping, and report markdown template all live there. The variant relies on those sections.

The main skill's **Evidence-first writing contract** and conditional-section rules are authoritative. Do not restate or weaken them here.

Then follow the **Review Process** in the main SKILL.md exactly — steps 1–4 (gather context, load references, analyze, write the report) and step 6 (handoff). Skip step 5 (HTML).

In short:

1. Determine review scope and run the matching `git diff` (see "Determining Review Scope" in the main SKILL.md).
2. Run `diff_stats.py`, load language-relevant references, and `common-vulnerabilities.md` if security-sensitive.
3. Analyze the diff against the five dimensions and assign severities.
4. Create `.reviews/` if missing and write the report using the markdown template in the main SKILL.md ("Present findings or write the markdown report"). Suggest adding `.reviews/` to `.gitignore` if absent — never modify `.gitignore` automatically.
5. In the conversation, report only finding counts by severity, overall risk, the Markdown artifact path, and fresh verification. Do not repeat report prose or promise a fixed finding count; mention at most one urgent finding inline only when immediate action is necessary.

## Filename

`.reviews/<YYYY-MM-DD>_<short-sha>.md` — see "Quick Reference / Filename convention" in the main SKILL.md.

## Language

Match the user's prompt language; see "Report Language" in the main SKILL.md. Add `**Language:** <bcp47>` in the metadata header.

## Red Flags

Same Never/Always lists as the main `<plugin-root>/skills/code-review/SKILL.md`. In particular: never modify `.gitignore` automatically (suggest only), never comment on code outside the diff, and never use INFO for uncertainty or praise.

## Integration

**Pairs with:** `git-commit` — review before committing for a final quality gate.
