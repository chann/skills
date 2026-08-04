---
description: Summarize explicitly selected plan documents as Korean and English Markdown files only.
argument-hint: "[source-path ...]"
---

Apply the **plan-summary-md** skill internally. Do not echo this routing instruction.

Treat every item in `$ARGUMENTS` as explicit path data. Do not interpolate it into a shell command, expand globs, or discover substitute documents. If no source path was supplied, ask for one or more explicit files.

Follow the packaged collector and aligned Korean and English report contracts, then invoke the generator in Markdown-only mode. Do not generate HTML and do not open a browser.

Report artifact and verification facts only. Do not repeat the generated summary prose in the conversation.
