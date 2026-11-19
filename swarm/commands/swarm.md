---
description: Hand a task to another coding agent and record the route, result, and call tree.
argument-hint: "[task]"
---

Use the **all-subagents** skill to hand the task to another installed coding
agent.

Task:

- Use `$ARGUMENTS` when it is non-empty.
- Otherwise use the task already under discussion.

Probe authenticated CLIs before choosing a route. Record the plan, including
the rationale and the quota transcript, before any child run. Pass file paths
instead of pasting sources. Do not poll. Read `meta.json` and show the call
tree when the run finishes.

Stay in this session when only one usable route exists and the user did not
name an agent or model. Use `long-task` for a multi-milestone project,
`research-brief` for a cited brief, and `code-review` for a defect report
written in this session.
