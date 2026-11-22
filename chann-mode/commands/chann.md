---
description: Run a non-trivial task in the owner's working style - restate the goal, pick a playbook, route each step to the skill that owns it, and reply with labelled evidence.
argument-hint: "<task>"
---

Use the **chann** skill for this task.

Task:
- Use `$ARGUMENTS` as the task when it is non-empty.
- Otherwise use the task already under discussion. With none, ask for the task
  and nothing else.

Restate the goal, name the least change that satisfies it, and proceed without a
confirmation round for reversible work. Read the chosen playbook from the
installed skill directory. Copy its steps into the host's task list or use a
chat checklist before the first edit. Keep push, PR, and deploy actions within
the user's authorization. The first line of every delegate's kickoff points
at `worker.md`. A delegate's report is
not evidence until its branch is merged and the project's checks pass on the
merged tree.
