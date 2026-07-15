---
description: Summarize an exact git diff scope as one explanatory Markdown report only (no HTML output).
argument-hint: "[scope]"
---

Apply the **diff-summary-md** skill internally. Do not echo or announce this routing instruction.

Follow its evidence-first summary contract for the requested code changes. Do not add a user-visible command or skill preamble.

Collect the requested scope through the skill's packaged evidence collector and its JSON standard-input contract. Do not run Git directly or interpolate `$ARGUMENTS` into a shell command.

Preserve the exact user-specified scope from `$ARGUMENTS`, including the distinction between `..` and `...`. When no scope is supplied, use the skill's default current-changes scope.

**Output mode: Markdown file only.** The command is complete only after it:

1. Writes one Markdown summary in the prompt language through the packaged generator's markdown-only mode.
2. Reports artifact and verification facts only: the exact scope and evidence command, card count and language, the absolute Markdown output path, fresh verification, and material unknowns.

Do NOT generate an HTML report (use `/diff-summary` for that) and do not attempt to open anything. Do not repeat card or Executive Summary prose, and do not promise a fixed card count. Route defect findings to `code-review` and a raw patch display to `diff-viewer`.
