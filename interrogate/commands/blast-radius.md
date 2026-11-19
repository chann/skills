---
description: Find what a change could break outside its diff and prove the fact it is safe because of by running real code.
argument-hint: "[scope]"
---

Use the **blast-radius** skill to check the change.

Target:
- Use `$ARGUMENTS` as the scope when it is non-empty.
- Otherwise use the current branch against its merge base with the default branch, plus uncommitted changes.

Find the one or two facts the change is safe because of and push each down the proof ladder (`said` < `cited` < `traced` < `ran` < `reproduced`), writing any repro script in a temporary directory outside the repository. Stay read-only on the repository: no edits, no installs, no destructive commands, no repository content sent to the network. Never invent a caller or an API; "searched, found nothing" is a valid result.

Reply with what the change does, the safety fact with its level and pasted proof (or "unproven"), risks with `file:line`, likelihood, cost, and how to check, what was cleared, and the cheapest check before merging. For defects inside the diff use `/interrogate`.
