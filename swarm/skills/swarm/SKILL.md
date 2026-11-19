---
name: swarm
description: Use when the user asks to fan work out to subagents or hand it to another coding agent or model, including "서브에이전트로 작업해줘", "서브에이전트 써서 돌려줘", "병렬로 나눠서 돌려줘", "이 작업 코덱스에 시켜줘", "클로드한테 검토받아줘", "다른 모델로 한 번 더 확인해줘", "쿼터 나눠서 병렬로 돌려줘", "use subagents", "spawn subagents", "swarm this", "run this with Codex", "ask Claude to review this", "spread these across quota", "second opinion from another model", "/swarm", or "$swarm". Frames a done predicate, splits the work into disjoint slices or races one brief across routes, reads every PASS, ISSUES, or BLOCKED result, and returns one report with the route rationale and a call tree. For competing attempts at one artifact with a single winner use arena, for a multi-milestone project use long-task, for a cited brief use research-brief, and for this session's defect report use interrogate.
---

# Swarm

Fan one job out to subagents or other installed coding agents, read what comes
back, and return one report that says who did what, why that route, and
whether the job is done.

The record is a run directory under `$XDG_CACHE_HOME/swarm/runs/<run-id>/`
(`~/.cache/swarm/runs/<run-id>/` when `XDG_CACHE_HOME` is unset): `plan.json`,
each task's `result.md` and `meta.json`, and `report.md`. Never store tokens,
session cookies, or raw login dumps there.

A route is `(agent, provider, model)`. Agents are Codex (`codex`), Claude Code
(`claude`), OpenCode (`opencode` 2.0.0 or newer), and Antigravity (`agy`).
Models are whatever those CLIs have authenticated; keep no private allowlist.
Run the helper with `python3 <skill-dir>/scripts/swarm.py <command>`.

Track the four phases in the host's task list before launching anything.

## 1. Frame

Write down, before any probe:

- **Done predicate.** The observable condition that ends the job.
- **Return.** The single artifact or report the swarm hands back.
- **Shape.** `partition` (disjoint slices of the work), `race` (the identical
  brief on different routes), or a mix. For a race, declare the selection rule
  now: `first pass` (the first `PASS` wins), `rank all` (order every arm), or
  `best of` (score every arm, keep one).

Stay in this session, and say which gate fired, when any is true:

- Probe reports `heterogeneous: false` and the user named no agent or model.
- The job is a lookup, a one-file edit, or something this session can finish.
- It is a multi-milestone autonomous project. That is `long-task`, even when
  the project says to use subagents in worktrees.
- It is a cited brief. That is `research-brief`.
- It is this session's defect report. That is `interrogate`.
- It is several competing attempts at one artifact with one winner. That is
  `arena`.

## 2. Fan out

**Probe.** `probe --check-auth --json`. Missing, unauthenticated, or OpenCode
below 2.0.0 is not a candidate; never upgrade a CLI. Read
`references/routes.md` and save the model list and quota transcript before
planning. A quota figure is copied from that transcript or is the literal
`unknown`; never invent a percentage. A discovery command that would flood
this session may run in one lightweight subagent, but the plan is recorded
here.

**Plan.** Read `references/selection.md`, write `plan.json`, and pass it
through `plan --run-id <run-id> --file <plan.json>`. The helper rejects a plan
without a rationale, one that reuses a vendor across independent steps or race
arms, one that escapes an exclude list, and one whose quota figure is not in
the transcript. At most four steps; a larger fan-out is a later run. A
fallback covers only its own step's failure and stays on the same vendor unless
`include_vendors` widens it. Print the one-line rationale (task fit, limiting
quota bucket and reset, vision or speed when set) before running.

**Brief.** Every brief stands alone and goes to a file:

1. The goal, how this slice or arm fits it, and why it is needed.
2. The scope and the exact slice or race arm, with its write set (or
   read-only).
3. The check that proves the work, and the fields the report must carry.
4. The verdict: `PASS`, `ISSUES` (every issue the worker can prove, not only
   the first), or `BLOCKED` (what stopped it), each with evidence such as a
   `file:line` or a command and its output.

Pass paths with `--context-file` and sources with `--reference`
(`--recommend-inspect` when reading it would change the answer); never paste
sources, diffs, or logs. A prompt over 8,000 characters is a warning, not a
success.

**Run.** Read `references/execution.md` before choosing a sandbox, then
`run --run-id … --task-id … --prompt-file … --cwd … --sandbox … --write-set …`.
Parallel steps need disjoint write sets or read-only access. Add `--guard` to a
read-only review that a silent edit would invalidate. When the host's subagent
tool can run that exact model id, use it and log it with `record-native`.

Do not poll. Pass `--timeout` and wait for that process, or start it in the
background and wait for the host's completion notice. A `sleep` loop or a turn
that keeps checking whether a file exists is a failed run.

## 3. Aggregate

Read each `<task-id>/meta.json` and `result.md` yourself, not a summary of
them.

- A result missing a verdict, evidence, or anything else its brief required is
  rerun once. A second miss is recorded as a gap. A gap is never a pass.
- `status: ok` with non-empty `denials_observed` is a completed answer; say
  when a refusal could have changed it.
- `error_class: permission` does not fall back; the headless CLI could not ask.
  Rerun with the missing `--add-dir`, or stop.
- `error_class: mutated` and `error_class: guard_failed` stop the run.
- `quota`, `auth`, and `unavailable` may use the step's own fallbacks. Anything
  else stops.
- `write_set_ok: false` means the tree changed outside the declared paths. That
  task is not clean. Compare `changed_paths` with the write set yourself.
- Partition: every required slice needs a result. Race: apply the rule declared
  in Frame, not one chosen after seeing the arms.

Judge the done predicate as `VERIFIED`, `NOT VERIFIED`, or `INCONCLUSIVE`. Any
gap or dropout on a required slice makes it at best `INCONCLUSIVE`.

## 4. Report

Mark a review that changed nothing with `mark --insignificant` when the user
wants only work that changed an outcome, then run `report --run-id <run-id>`.
Return one consolidated report:

- a result table: task, route, verdict, write set held;
- one line per issue, with its evidence;
- gaps, dropouts, and denials;
- the race rule and the winning arm, when a race ran;
- the done-predicate verdict;
- the call tree from `report.md`, unless the user asked to skip it.

## Refusals

- Do not spawn when this session should do the work, or when only one usable
  route exists and the user named none.
- Do not invent quota, model rankings, or a transcript the helper cannot see.
- Do not fall back outside the plan's vendor filter.
- Do not poll for a result file.
- Do not upgrade the user's CLI.
- Do not read or copy credential files into the cache.
- Do not call a gap, a dropout, or a missing verdict a pass.
- Do not treat a guarded run as clean after `mutated` or `write_set_ok: false`.

## Integration

**Pairs with:** `interrogate` when another model's findings should become this
session's defect report, `bug-hunt` when a delegated task is one experiment in
a diagnosis, and `arena`, which can seat its candidates through this skill.
Each is optional; this skill runs alone.

**Use instead of:** `arena` for competing attempts with one winner,
`long-task` for a multi-milestone project, `research-brief` for a cited brief,
and `interrogate` for a defect report written here.

**Reply:** the result table with each worker's verdict, issue one-liners, gaps and dropouts, the race rule when used, the done-predicate verdict, and the call tree from `report.md`.
