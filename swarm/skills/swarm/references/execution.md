# How a run is executed

`scripts/swarm.py run` builds the CLI command. Do not hand-assemble
one. This note is the posture contract the command implements.

## Sandbox

| Posture | When | What the helper asks for |
|---|---|---|
| `read-only` | Reviews and other non-mutating reads | Claude Code denies edit tools. Codex uses `sandbox_mode=read-only`. OpenCode uses the `plan` agent and denies edit and shell. Antigravity uses `--mode plan --sandbox`. |
| `workspace-write` | The task is allowed to edit the write set | Claude Code `acceptEdits`. Codex `workspace-write`. OpenCode `--auto`. Antigravity `--mode accept-edits --sandbox`. |
| `bypass` | The user accepted an unrestricted local run, or an older Antigravity build has no `--sandbox` | The CLI's unrestricted flag. Do not switch to this after a read-only flag is rejected. `error_class: no_option` stops the run. |

`--no-tools` forces `read-only`. Claude Code and OpenCode can actually deny
tools, so `tools_enforced` is true. Codex and Antigravity cannot turn tools
off. Their `tools_enforced` is false, and the prompt has to carry the limit.
When "no tool call happened" must be guaranteed, pick Claude Code or OpenCode.

`--allow-shell` keeps edits denied and permits a shell, for a review that needs
`git` or a focused test. Antigravity still mounts a read-only filesystem in
`read-only` mode. Codex's read-only sandbox also blocks child processes, so a
Codex task that must run a command needs `workspace-write` or another agent.

`--isolate` asks the CLI not to load project hooks, rules, or skills where the
CLI has that switch. Codex gets `--ignore-rules`. Claude Code gets safe mode
and a strict MCP config. OpenCode turns sharing, update, and snapshots off.

## Context outside the working directory

Pass `--add-dir` for a checkout or snapshot outside `--cwd`. Directories that
contain `--context-file` paths are added automatically. Antigravity headless
mode auto-denies a read outside the workspace and can still exit successfully
with an empty answer. The helper classifies the `jetski:` auto-deny note as
`permission` and does not fall back, because the next model would hit the same
wall.

## Sessions

One-shot runs suppress or delete the child session where the CLI allows it:
Codex `--ephemeral`, Claude Code `--no-session-persistence`, OpenCode
`session delete` for the session this run created. Antigravity keeps its
transcript. `session_cleaned_up: false` is that fact, not a failure.

`--keep-session` leaves the session in `sessions.json`. Resume it with
`--resume-task`. Do not resume a session onto a different model family. Start
a new task instead.

## After the process exits

The helper writes `meta.json`, publishes `result.md` only for a successful
attempt, and refreshes `report.md`. A failed attempt keeps its own
`attempts/attempt-N/result.md` when the CLI produced text. Read that file
instead of mining the raw log.

Failure classes that may use the step's fallback list are `quota`, `auth`,
and `unavailable`. `permission`, `mutated`, `guard_failed`, `no_option`,
`timeout`, `format`, and `failed` stop. Quota classification looks at stderr,
not at the model's answer, so a test log that mentions `429` cannot mark the
account exhausted.

`--guard` records file hashes, symlink targets, and `HEAD` before and after.
It does not watch a process that detaches into a new session, and it does not
cover another repository's Git directory. Pair it with `read-only`. A clean
guard means the snapshotted state matched, which is not a promise that no
transient write occurred.

The helper never polls. The timeout is the wait.

## Command lines

Probe, record the plan, then run one task per step:

```bash
python3 <skill-dir>/scripts/swarm.py probe --check-auth --json
python3 <skill-dir>/scripts/swarm.py plan --run-id <run-id> --file <plan.json>
python3 <skill-dir>/scripts/swarm.py run \
  --run-id <run-id> \
  --task-id <task-id> \
  --prompt-file <task.md> \
  --cwd <repo> \
  --sandbox read-only \
  --write-set <path> \
  --timeout 600
```

For a later turn with the same child, pass `--keep-session` on the first call
and `--resume-task <task-id>` on the next.

A review that found nothing actionable can be marked before the report, and
`--only-significant` then hides it:

```bash
python3 <skill-dir>/scripts/swarm.py mark \
  --run-id <run-id> \
  --task-id <task-id> \
  --insignificant \
  --outcome-summary "Reviewed the diff and reported no actionable issues."

python3 <skill-dir>/scripts/swarm.py report --run-id <run-id> [--only-significant]
```

`report.md` names every participating agent and official model id, the
rationale, the outcome, and whether the write set held.

A step that ran on the host's own subagent tool joins the same tree:

```bash
python3 <skill-dir>/scripts/swarm.py record-native \
  --run-id <run-id> \
  --task-id <task-id> \
  --agent "Claude Code" \
  --model <model-id> \
  --summary "Why this model ran natively." \
  --outcome-summary "What it produced."
```

Use the host's subagent tool when it can run that exact model id. Use the CLI
when the route is a different agent, a different vendor, or needs a session
the host tool cannot resume.
