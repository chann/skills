---
description: Run competing attempts at one artifact, cross-judge them, pick a base, and graft the best parts.
argument-hint: "<task>"
---

Use the **arena** skill to run several competing attempts at one artifact.

Task:

- Use `$ARGUMENTS` when it is non-empty.
- Otherwise use the task already under discussion.

Frame first: name the artifact, derive a hidden rubric of three to six
gradeable criteria, and give every candidate the same prompt. Each candidate
writes to its own worktree or temporary directory. Route the seats through
`swarm` when it is installed; otherwise say the candidates share one vendor.
The judge is read-only, sees neutral labels only, and comes from another
vendor when one is available. Read every candidate yourself before picking a
base, graft by hand, and verify the result.

Refuse and do the task once when its shape is already settled. Use `swarm` for
different slices of one job and `review-me` for an interview about a plan's
decisions.
