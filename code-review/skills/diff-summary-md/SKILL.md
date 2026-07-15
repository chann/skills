---
name: diff-summary-md
description: Use when the user wants a Markdown-only diff or change summary artifact without an HTML report, including "요약을 마크다운 파일로만 저장해줘", "마크다운 요약만 저장", "마크다운 요약만 만들어줘", "diff 요약 마크다운으로", "markdown-only diff summary", "summarize the changes into a markdown file", "summary file without HTML", or "/diff-summary-md". For the interactive HTML report use diff-summary; for a summary with a comprehension quiz use diff-summary-quiz; for defects use code-review.
---

# Diff Summary (Markdown Only)

## Overview

Variant of the `diff-summary` skill that persists only the Markdown report to `.diff-summaries/<date>_<scope-tag>.md`. It never generates the HTML report and never attempts a browser open.

## Workflow

**Before starting, read the bundled base workflow** at `<skill-path>/references/diff-summary-workflow.md`. It is a synchronized copy of the authoritative `diff-summary` workflow, including the packaged evidence collector contract, scope preservation and validation rules, untrusted-evidence rules, analysis dimensions, evidence-first writing contract, Explanatory Depth guidance, and Stable Report Contract. Do not restate or weaken it here.

Follow the bundled base workflow exactly through report authoring, then change only the generation step:

1. Collect the requested scope through the packaged evidence collector and its JSON standard-input contract, exactly as the bundled workflow requires. Every fail-closed rule applies unchanged.
2. Author one Markdown report in the prompt language that satisfies the bundled workflow's Stable Report Contract.
3. Start the packaged generator with the same trusted absolute Python path and isolated `-I` mode, adding `--markdown-only`:

   ```text
   /absolute/trusted/python3 -I <skill-path>/scripts/generate_summary_report.py \
     --markdown-stdin \
     --output-directory ".diff-summaries" \
     --markdown-only
   ```

   The generator validates the full report contract, derives the collision-safe stem, and atomically writes only `.diff-summaries/<date>_<scope-tag>.md`. Require a zero exit status and use the exact absolute Markdown path it prints.
4. Do not generate the HTML report. Do not attempt a browser open. Route requests for the interactive page to `diff-summary` or `diff-summary-quiz` instead of adding HTML output here.

This exact selector ships its own synchronized reference, collector, generator, and template so a standalone installation remains executable. Treat those bundled files as one release unit with the authoritative `diff-summary` runtime.

## Conversation Handoff

Report only these artifact and verification facts: the exact requested scope and exact evidence command, the generated card count and report language, the absolute Markdown output path, fresh verification performed, and material unknowns that remain unverified. Do not repeat card or Executive Summary prose, and do not promise a fixed card count.

If `.diff-summaries/` is not ignored by the target repository, suggest adding it to that repository's `.gitignore`. Never edit `.gitignore` automatically.
