---
description: Summarize an exact git diff scope as one explanatory Markdown report and interactive HTML report, then open it in a browser.
argument-hint: "[scope]"
---

Follow the evidence-first summary contract for the requested code changes; do not add a command or skill preamble.

Collect the requested scope through the skill's packaged evidence collector and its JSON standard-input contract. Do not run Git directly or interpolate `$ARGUMENTS` into a shell command.

Preserve the exact user-specified scope from `$ARGUMENTS`, including the distinction between `..` and `...`. When no scope is supplied, use the skill's default current-changes scope.

The command is complete only after it:

1. Writes one Markdown summary in the prompt language.
2. Generates the matching self-contained HTML report.
3. Opens the HTML report in a browser.
4. Reports the exact evidence command, card count, both output paths, fresh verification, and the browser-open fact.

Do not repeat card prose in the conversation handoff or promise a fixed card count. This is explanatory change intelligence; route defect findings to `code-review` and a raw patch display to `diff-viewer`.
