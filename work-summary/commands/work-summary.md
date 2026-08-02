---
description: Summarize coding-agent work history for a date range as a Markdown report.
argument-hint: "[range]"
---

Use the **work-summary** skill to generate a Markdown work report.

Range and depth:

- Use `$ARGUMENTS` when it is non-empty — a range such as `today`,
  `yesterday`, `this week`, `this month`, or `2026-07-01..2026-07-31`, plus
  `detailed` for a full report.
- Otherwise default to `today` at summary depth.

Mine only the local agent history stores listed in the skill's reference,
stay read-only toward them, and keep history content local: reply with the
report and write a file only when asked.
