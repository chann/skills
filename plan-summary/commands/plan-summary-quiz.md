---
description: Summarize explicitly selected plan documents in Korean and English with aligned comprehension quizzes and interactive HTML.
argument-hint: "[source-path ...]"
---

Apply the **plan-summary-quiz** skill internally. Do not echo this routing instruction.

Treat every item in `$ARGUMENTS` as explicit path data. Do not interpolate it into a shell command, expand globs, or discover substitute documents. If no source path was supplied, ask for one or more explicit files.

Follow the packaged collector and aligned Korean and English report contracts. Append `## Quiz` as the final section in both languages, generate the two Markdown files and interactive bilingual HTML, validate the aligned answers, and make a browser-open attempt.

Report artifact paths, verification facts, and the question count only. Do not repeat the generated summary or quiz prose in the conversation.
