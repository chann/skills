---
description: Fan a task out to subagents or other coding agents and return one report with verdicts and the call tree.
argument-hint: "<task>"
---

Use the **swarm** skill to fan the task out to subagents or other installed
coding agents.

Task:

- Use `$ARGUMENTS` when it is non-empty.
- Otherwise use the task already under discussion.

Frame first: the done predicate, the single return, and the shape (`partition`,
`race`, or a mix). Declare a race's selection rule before any arm runs.

Probe authenticated CLIs before choosing a route. Record the plan, including
the rationale and the quota transcript, before any child run. Every brief
stands alone and asks for `PASS`, `ISSUES`, or `BLOCKED` with evidence. Pass
file paths instead of pasting sources. Do not poll. Read each `meta.json` and
`result.md` yourself; a gap is never a pass. Finish with one report and the
call tree.

Stay in this session when only one usable route exists and the user did not
name an agent or model. Use `arena` for competing attempts at one artifact,
`long-task` for a multi-milestone project, `research-brief` for a cited brief,
and `interrogate` for a defect report written in this session.
