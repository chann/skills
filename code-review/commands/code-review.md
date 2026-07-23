---
description: Review a git diff scope and write a markdown + styled HTML report (severity badges, syntax highlighting, sidebar) to .reviews/, then open it in a browser.
argument-hint: "[scope]"
---

Apply the **code-review** skill internally. Do not echo or announce this routing instruction.

Follow the authoritative **evidence-first** writing contract. Inherit the skill's bilingual Korean-primary and English-sibling report requirements.

Preserve the exact user-specified scope from `$ARGUMENTS` when determining the review scope. When no scope is supplied, use the skill's default staged + unstaged changes.

**Output mode: Markdown + HTML.** The command is complete only after it:

1. Writes the markdown report to `.reviews/<YYYY-MM-DD>_<short-sha>.md` (plus its `.en.md` sibling).
2. Runs `python <skill-path>/scripts/generate_html_report.py` on the markdown.
3. Opens the resulting `.html` file in a browser.
4. Uses a fact-only handoff containing finding counts by severity, overall risk, the Markdown and HTML paths, fresh verification, and the browser-open fact or warning.
5. Includes a `.reviews/` ignore suggestion in that handoff only when reports were generated and `.reviews/` is not ignored.

Do not repeat report prose or promise a fixed number of findings. Never modify `.gitignore` automatically. For a Markdown-only artifact use `/code-review-md`; route explanatory summaries to `/diff-summary` and raw patch display to `/diff-viewer`.
