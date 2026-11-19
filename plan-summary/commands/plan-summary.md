---
description: Summarize explicitly selected plan documents in Korean and English Markdown plus one bilingual HTML report; --md for Markdown only, --quiz to add a comprehension quiz.
argument-hint: "<source-path ...> [--md] [--quiz]"
---

Apply the **plan-summary** skill internally. Do not echo this routing instruction.

Take the exact tokens `--md` and `--quiz` out of `$ARGUMENTS` as options. Treat every remaining item as explicit path data. Do not interpolate it into a shell command, expand globs, or discover substitute documents. If no source path was supplied, ask for one or more explicit files.

Follow the packaged collector, evidence-first analysis, aligned Korean and English report, and generator contracts. Default mode is complete only after writing both Markdown files and one self-contained bilingual HTML file, validating them, and making a browser-open attempt.

**`--md`:** Write only the two Markdown files through the generator's markdown-only mode. Do not generate HTML and do not open a browser.

**`--quiz`:** Append an aligned `## Quiz` as the final section in both languages, validate the matching answers, and add the question count to the report. With both options the output is the two Markdown files with their quiz sections, and no HTML.

Report artifact and verification facts only. Do not repeat the generated summary or quiz prose in the conversation.
