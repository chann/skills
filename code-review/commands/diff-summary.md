---
description: Summarize an exact git diff scope as one explanatory Markdown report and interactive HTML report, then open it in a browser.
argument-hint: "[scope]"
---

Apply the **diff-summary** skill internally. Do not echo or announce this routing instruction.

Follow its evidence-first summary contract for the requested code changes. Do not add a user-visible command or skill preamble.

Collect the requested scope through the skill's packaged evidence collector and its JSON standard-input contract. Do not run Git directly or interpolate `$ARGUMENTS` into a shell command.

Preserve the exact user-specified scope from `$ARGUMENTS`, including the distinction between `..` and `...`. When no scope is supplied, use the skill's default current-changes scope.

The command is complete only after it:

1. Writes one Markdown summary in the prompt language.
2. Generates the matching self-contained HTML report.
3. Opens the HTML report in a browser.
4. Reports artifact and verification facts only: the exact scope and evidence command, card count and language, both absolute output paths, browser-open fact or warning, fresh verification, and material unknowns.

Do not repeat card or Executive Summary prose, including for a one-card mechanical diff, and do not promise a fixed card count. This is explanatory change intelligence; route defect findings to `code-review` and a raw patch display to `diff-viewer`.
