---
description: Explain why code is built this way from commits, pull requests, issues, and design notes.
argument-hint: "<question>"
---

Use the **why** skill to answer the question from the record.

Question:
- Use `$ARGUMENTS` when it is non-empty.
- Otherwise use the code or decision already under discussion.

Read how the target first entered the codebase and every change made to it since. Answer with a
short answer and its confidence, then a decision timeline with the commit or PR,
the date, and what its author wrote. Mark your own reading `inferred`, state the
questions the record leaves open, and never present a guess from the code's shape as
the reason. Stay read-only: no edits, no commits, no posted comments.
