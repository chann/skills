---
description: Summarize an exact git diff scope as one explanatory Markdown report and interactive HTML report, then open it in a browser.
argument-hint: "[scope]"
---

Use the **diff-summary** skill to explain the requested code changes.

Collect the requested scope through the skill's packaged evidence collector and its JSON standard-input contract. Do not run Git directly or interpolate `$ARGUMENTS` into a shell command.

Preserve the exact user-specified scope from `$ARGUMENTS`, including the distinction between `..` and `...`. When no scope is supplied, use the skill's default current-changes scope.

The command is complete only after it:

1. Writes one Markdown summary in the prompt language.
2. Generates the matching self-contained HTML report.
3. Opens the HTML report in a browser.
4. Reports the exact evidence command and both output paths.

This is explanatory change intelligence. Use `code-review` for defect findings and `diff-viewer` for a raw diff display.
