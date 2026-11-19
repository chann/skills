---
description: Write a frontend, backend, or session handoff, separating proven state from unproven.
argument-hint: "[frontend | backend | session] [scope]"
---

Use the **handoff** skill to write a handoff document.

Audience and scope:
- If `$ARGUMENTS` starts with `frontend`, `backend`, or `session`, that is the audience; the rest is the git scope (or, for `session`, a note about what the next session is for).
- Otherwise resolve the audience from the request's wording, then by inference, and state it with the reason in the first line.
- With no scope, use the current working tree and staged changes. Never broaden an explicit range such as `main...feature`.

Write the document under `.handoffs/`. Name the command behind every proven claim and mark everything else "Not verified in this handoff". Redact secrets from quoted commands and logs. Do not commit or push.
