---
description: Summarize an exact git diff scope in Korean and English Markdown plus one interactive bilingual HTML report; --md for Markdown only, --quiz to add a comprehension quiz.
argument-hint: "[scope] [--md] [--quiz]"
---

Apply the **diff-summary** skill internally. Do not echo or announce this routing instruction.

Follow its evidence-first summary contract for the requested code changes. Do not add a user-visible command or skill preamble.

Collect the requested scope through the skill's packaged evidence collector and its JSON standard-input contract. Do not run Git directly or interpolate `$ARGUMENTS` into a shell command.

Take the exact tokens `--md` and `--quiz` out of `$ARGUMENTS` as options. Preserve the rest as the exact user-specified scope, including the distinction between `..` and `...`. When no scope is supplied, use the skill's default current-changes scope.

Default mode is complete only after it:

1. Writes aligned Korean and English Markdown summaries with the same `DS-*` IDs and evidence claims.
2. Generates the matching self-contained bilingual HTML report with Korean as the default view and an accessible language control.
3. Opens the HTML report in a browser.
4. Reports artifact and verification facts only: the exact scope and evidence command, card count and languages, all three absolute output paths, browser-open fact or warning, fresh verification, and material unknowns.

**`--md`:** Write only the two Markdown files through the generator's bilingual markdown-only mode. Do NOT generate an HTML report and do not attempt to open anything; report both absolute Markdown paths and the same verification facts.

**`--quiz`:** Also end both Markdown summaries with a validated `## Quiz` section that uses the same `QZ-*` IDs and answer positions, and add the question count to the report. With both options the output is the two Markdown files with their quiz sections, and no HTML.

Korean and English are the default output languages. Use the skill's explicit single-language mode only when the user requests one language.

Do not repeat card, Executive Summary, or quiz prose, including for a one-card mechanical diff, and do not promise a fixed card or question count. This is explanatory change intelligence; route defect findings to `interrogate` when it is installed and a raw patch display to `diff-viewer`.
