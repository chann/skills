---
name: all-subagents
description: Use when the user asks to work through subagents or hand work to another coding agent or model, including "서브에이전트로 작업해줘", "서브에이전트 써서 돌려줘", "이 작업 코덱스에 시켜줘", "클로드한테 검토받아줘", "다른 모델로 한 번 더 확인해줘", "쿼터 나눠서 병렬로 돌려줘", "use subagents", "spawn subagents", "run this with Codex", "ask Claude to review this", "second opinion from another model", "spread these across quota", "/all-subagents", or "$all-subagents". Produces a run directory with the route rationale, each task's result, and a call-tree report. For a multi-milestone project in this session use long-task, for a cited brief use research-brief, and for this session's defect report use code-review.
---

# All Subagents

Use this when the user wants the work done through subagents, or handed to
another installed coding agent, and leave a record of why that route was
chosen and what came back.

The artifact is a run directory under `$XDG_CACHE_HOME/all-subagents/runs/<run-id>/`
(or `~/.cache/all-subagents/runs/<run-id>/` when `XDG_CACHE_HOME` is unset).
It holds `plan.json`, each task's `result.md` and `meta.json`, and `report.md`.
Do not store tokens, session cookies, or raw login dumps there.

A route is `(agent, provider, model)`. The agents are Codex (`codex`), Claude
Code (`claude`), OpenCode (`opencode` 2.0.0 or newer), and Antigravity (`agy`).
Models are whatever those CLIs have authenticated. Do not keep a private
allowlist of model families.

Run the helper with `python3` from this skill:

```bash
python3 <skill-dir>/scripts/all_subagents.py probe --check-auth --json
```

## 1. Decide this skill applies

Use it when the user asks to work through subagents, spawn subagents, name
another agent or model, get an independent check from a different model
vendor, or spread parallel work across quota pools. "서브에이전트로 작업해줘",
"use subagents", and "spawn subagents" select this skill.

Stay in this session, and say which gate fired, when any of these is true:

- Probe reports `heterogeneous: false` and the user did not name an agent or model.
- The job is a lookup, a one-file edit, or something this session can finish.
- The user wants a multi-milestone autonomous project. That is `long-task`,
  even when that project says to use subagents in worktrees.
- The user wants a cited brief. That is `research-brief`.
- The user wants this session's defect report. That is `code-review`.

Do not upgrade an installed CLI. If OpenCode is older than 2.0.0, leave it
unusable and pick another agent, or ask the user to upgrade.

## 2. Probe before choosing

```bash
python3 <skill-dir>/scripts/all_subagents.py probe --check-auth --json
```

An agent that is missing, unauthenticated, or below the OpenCode version floor
is not a candidate. Read `references/routes.md` and collect the live model list
and quota transcript before writing the plan. If a quota command fails or its
shape is unfamiliar, the quota note is the literal `unknown`. Never invent a
percentage.

A discovery command that would dump a long catalog into this session may run
inside one lightweight subagent. The plan still has to be recorded here.

## 3. Select the route and record the plan

Read `references/selection.md`. Write a plan file and pass it through the
helper. The helper rejects a plan that skips the rationale, reuses a vendor
across independent steps, escapes an exclude list, or claims a quota figure
that is not in the transcript file.

```bash
python3 <skill-dir>/scripts/all_subagents.py plan \
  --run-id <run-id> \
  --file <plan.json>
```

A plan has at most four steps. Each step needs its own route. Independent
checks use different vendors unless the user forced one vendor. A fallback is
only for that step's own failure, and it stays inside the same vendor unless
`include_vendors` names a wider set.

Print the one-line rationale before running: task fit, the limiting quota
bucket and when it resets, and vision or speed when those constraints were set.
`plan.json` keeps the same rationale.

When the host's native subagent tool can run that exact model id, use it and
record the result with `record-native`. Use the CLI when the route is a
different agent, a different vendor, or needs a session the host tool cannot
resume.

## 4. Write the prompt to a file, then run

Read `references/execution.md` before choosing a sandbox. Three rules apply to
every prompt:

1. State the larger goal, how this task fits it, and why it is needed.
2. Pass paths with `--context-file`. Do not paste source files, diffs, or logs.
   A prompt over 8,000 characters is a warning, not a success.
3. When the task depends on an issue, a pull request, or a page, pass
   `--reference`. Add `--recommend-inspect` when reading that source would
   change the answer.

```bash
python3 <skill-dir>/scripts/all_subagents.py run \
  --run-id <run-id> \
  --task-id <task-id> \
  --prompt-file <task.md> \
  --cwd <repo> \
  --sandbox read-only \
  --write-set <path>
```

Name the write set in the prompt and in `--write-set`. Parallel steps are
allowed only when every write set is disjoint or every step is read-only. The
cap is the four steps already in the plan.

Do not poll. Pass `--timeout` and wait for that process, or start it in the
background and wait for the host's completion notice. A `sleep` loop or a turn
that repeatedly asks whether the file exists is a failed run.

For a later turn with the same child, pass `--keep-session` on the first call
and `--resume-task <task-id>` on the next. Start a fresh session when the model
family changes.

For a read-only review where a silent edit would invalidate the verdict, add
`--guard`. The helper hashes the Git state before and after. A changed file or
a moved `HEAD` fails the attempt with `error_class: mutated` and does not fall
back onto another model. The guard is a change detector, not a sandbox.

## 5. Read the result before trusting it

Read `<task-id>/meta.json` and, when it exists, `<task-id>/result.md`.

- `status: ok` with a non-empty `denials_observed` is still a completed answer.
  Tell the user when a refusal could have changed the result.
- `error_class: permission` does not fall back. The headless CLI could not ask
  for approval. Re-run with the missing `--add-dir`, or stop.
- `error_class: mutated` and `error_class: guard_failed` stop the run.
- `quota`, `auth`, and `unavailable` may try the step's own fallback list.
  Anything else stops.
- `write_set_ok: false` means the tree changed outside the declared paths. Do
  not call that task clean.

Compare `changed_paths` with the write set yourself before reporting success.

## 6. Report the call tree

Mark a review that found nothing actionable before the report, when the user
wants only work that changed an outcome:

```bash
python3 <skill-dir>/scripts/all_subagents.py mark \
  --run-id <run-id> \
  --task-id <task-id> \
  --insignificant \
  --outcome-summary "Reviewed the diff and reported no actionable issues."

python3 <skill-dir>/scripts/all_subagents.py report --run-id <run-id>
```

Show `report.md` to the user unless they asked to skip the summary. It names
every participating agent and official model id, the rationale, the outcome,
and whether the write set held. `--only-significant` hides reviews that were
marked insignificant.

A native host subagent is part of the same tree:

```bash
python3 <skill-dir>/scripts/all_subagents.py record-native \
  --run-id <run-id> \
  --task-id <task-id> \
  --agent "Claude Code" \
  --model <model-id> \
  --summary "Why this model ran natively." \
  --outcome-summary "What it produced."
```

## Refusals

- Do not spawn a CLI when this session should do the work.
- Do not spawn a CLI when only one usable route exists unless the user named it.
- Do not invent quota, model rankings, or a transcript the helper cannot see.
- Do not fall back outside the plan's vendor filter.
- Do not poll for a result file.
- Do not upgrade the user's CLI.
- Do not read or copy credential files into the cache.
- Do not treat a guarded read-only run as clean after `mutated` or `write_set_ok: false`.

## Integration

**Pairs with:** `code-review` when another model's findings should become this
session's defect report, and `bug-hunt` when the delegated task is one
experiment inside a diagnosis.

**Use instead of:** `long-task` for a multi-milestone project in this session,
`research-brief` for a cited brief, and `code-review` for a defect report
written here.
