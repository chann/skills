---
description: Turn what this session or repository taught into enforcement, not prose, after your approval.
argument-hint: "[session | repo]"
---

Use the **reflect** skill to capture what the work taught.

Scope:
- Use `$ARGUMENTS` when it is `session` or `repo`.
- Otherwise reflect on this conversation.

Keep only lessons that will still hold in six months and would change what a
future agent does. Route each to the strongest place that works — a script,
lint, test, or hook first, then the owning skill, then the agent instruction
file. Present Accepted, Rejected, and Backlog, and stop. Edit nothing until the
user approves, edit sources rather than installed copies, prove a new check
fails on the past mistake, and never push.
