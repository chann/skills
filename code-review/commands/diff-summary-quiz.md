---
description: Summarize an exact git diff scope as Markdown and interactive HTML reports ending in a comprehension quiz, then open the HTML in a browser.
argument-hint: "[scope]"
---

Apply the **diff-summary-quiz** skill internally. Do not echo or announce this routing instruction.

Follow its evidence-first summary contract and its quiz authoring contract for the requested code changes. Do not add a user-visible command or skill preamble.

Collect the requested scope through the skill's packaged evidence collector and its JSON standard-input contract. Do not run Git directly or interpolate `$ARGUMENTS` into a shell command.

Preserve the exact user-specified scope from `$ARGUMENTS`, including the distinction between `..` and `...`. When no scope is supplied, use the skill's default current-changes scope.

The command is complete only after it:

1. Writes one Markdown summary in the prompt language that ends with a validated `## Quiz` section.
2. Generates the matching self-contained HTML report with the interactive quiz.
3. Opens the HTML report in a browser.
4. Reports artifact and verification facts only: the exact scope and evidence command, the card count, question count, and language, both absolute output paths, the browser-open fact or warning, fresh verification, and material unknowns.

Do not repeat card, Executive Summary, or quiz prose, and do not promise a fixed card or question count. Route defect findings to `code-review` and a raw patch display to `diff-viewer`.
