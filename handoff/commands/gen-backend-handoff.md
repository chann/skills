---
description: Generate a backend/server handoff from code changes, API changes, database changes, git diffs, commit ranges, branch comparisons, or session context.
argument-hint: "[scope]"
---

Use the **gen-backend-handoff** skill to create a backend handoff.

Scope:
- If `$ARGUMENTS` is non-empty, treat it as the requested git scope or context selector.
- Otherwise use the current working tree and staged changes.

Write the document under `.handoffs/`. Keep the handoff evidence-based, preserve the requested scope, and do not claim tests, deploys, or runtime behavior unless verified.
