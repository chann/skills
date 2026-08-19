# long-task

[한국어](README.ko.md) · [← back to main](../README.md)

Runs **long, multi-milestone projects** autonomously for hours or days without human intervention. It combines a pausable run lifecycle with parallel subagents in Git worktrees.

## What it does

- Runs a **Phase 1 (setup) → Phase 2 (execution loop) → Phase 3 (completion)** workflow that takes a project from scratch to delivery
- Dispatches parallel **subagents in isolated git worktrees** (cap: 5 parallel) and merges them after verification
- Reviews the architecture at every milestone, assigns fixes to subagents, and reviews again for up to 3 iterations
- Uses persistent `.agent/` state files as working memory so progress survives context compaction or session restarts
- Installs a **Stop hook** that auto-continues work across many turns while a long-task is active — no manual nudging needed
- Codex-style **lifecycle commands**: `/long-task status | pause | resume | clear | complete`
- **Completion check**: `/long-task complete` writes a template that maps acceptance criteria to concrete evidence
- Resolves ambiguity autonomously during execution — you only interact with the user during Phase 1 setup
- Includes ready-to-customize templates for `goal.md`, `plans.md`, `standards.md`, `implement.md`, `progress.md`, `state.md`, `audit.md`

## Installation

**Recommended (global, one shot):**

```bash
npx skills add -y -g chann/skills --skill long-task
```

**Project-local:**

```bash
npx skills add chann/skills --skill long-task
```

Use the actual skill name with `--skill`; this plugin packages the `long-task` skill.

**Manual:**

```bash
git clone https://github.com/chann/skills.git
ln -s "$(pwd)/skills/long-task/skills/long-task" ~/.claude/skills/long-task
```

### Stop hook setup

No separate setup script is required. The helper is packaged inside the installable skill folder and installs or updates the Stop hook on the first `/long-task` run.

The helper safely patches `~/.claude/settings.json` and is idempotent. The hook only fires when the current working directory contains `.agent/state.md` with `status: active`, so unrelated Claude Code sessions are unaffected. To disable continuation for a project, run `/long-task pause`, `/long-task clear`, or `/long-task complete`.

## Usage

The skill triggers automatically on phrases like *"build this whole project
end-to-end"*, *"do this autonomously"*, or *"run a long task"*. Explicit
selectors are:

| Claude Code                  | Codex                     | Action                                                                             |
| ---------------------------- | ------------------------- | ---------------------------------------------------------------------------------- |
| `/long-task <objective>`     | `$long-task <objective>`  | Set the objective in Phase 1, then begin the autonomous execution loop             |
| `/long-task`                 | `$long-task`              | Status if active, otherwise Phase 1 interactive setup                              |
| `/long-task status`          | `$long-task status`       | Current state, phase, elapsed time, runaway counter, and `.agent/progress.md` tail |
| `/long-task pause`           | `$long-task pause`        | Disarm Stop hook auto-continuation until resumed                                   |
| `/long-task resume`          | `$long-task resume`       | Resume auto-continuation; runaway counter resets                                   |
| `/long-task clear`           | `$long-task clear`        | Delete `.agent/state.md`; preserve the rest of `.agent/*.md` for reference         |
| `/long-task complete`        | `$long-task complete`     | Write `.agent/audit.md` template, mark complete, disarm Stop hook                  |

**Examples:**

```
> /long-task build a TypeScript Express API with auth, posts, and comments
> implement this end-to-end and don't stop to ask questions
> run a long task to build the whole CLI from scratch
> /long-task status
> /long-task pause
> /long-task complete
```

### Runaway guard

The Stop hook auto-continues up to **500 stops** by default. Override before launching Claude Code:

```bash
export LONG_TASK_MAX_STOP_CONTINUES=1000
```

## How it works

1. **Phase 1 (Setup, only user interaction):** Interview the user, write `.agent/goal.md`, design milestones in `.agent/plans.md`, define `.agent/standards.md` and `.agent/implement.md`. Get final sign-off. State file `.agent/state.md` is created with `status: active`.
2. **Phase 2 (Execution loop):** For each milestone, re-read state, dispatch parallel implementer subagents in worktrees, verify with tests, lint, and type checks, merge, dispatch an architectural reviewer, fix any issues, and update `progress.md`. Repeat until all milestones are complete. The Stop hook continues the work across turns.
3. **Phase 3 (Completion):** Final cross-cutting review on entire codebase, address critical issues, run `/long-task complete` to write `.agent/audit.md` (the evidence map), and report to user.

## State files (`.agent/`)

| File             | Purpose                                              | Updated when                               |
| ---------------- | ---------------------------------------------------- | ------------------------------------------ |
| `state.md`       | Lifecycle status, phase, runaway counter             | Every slash command + Stop-hook tick       |
| `goal.md`        | Problem, outcome, acceptance criteria, non-goals     | Once, at setup                             |
| `plans.md`       | Architecture, milestones, tasks                      | At setup; appended on scope discovery      |
| `standards.md`   | Code quality bar (read by every subagent)            | Once                                       |
| `implement.md`   | Subagent workflow (read by every subagent)           | Once                                       |
| `progress.md`    | Current state, decisions, architecture summary       | After every action                         |
| `audit.md`       | Completion audit: acceptance criteria → evidence map | Once, when `/long-task complete` runs      |

## Project structure

```
long-task/
├── .claude-plugin/
│   └── plugin.json                        # Plugin metadata
├── commands/
│   └── long-task.md                       # /long-task slash command
└── skills/
    └── long-task/
        ├── SKILL.md                       # Skill definition and workflow
        ├── scripts/
        │   └── long_task.py               # Lifecycle helper + Stop hook
        └── references/
            ├── project-templates.md       # .agent/ file templates
            └── completion-audit.md        # Completion-audit guide
```

## Requirements

- An agent platform that supports skills ([Claude Code](https://code.claude.com), Codex, opencode, Copilot CLI, etc. — see [main README](../README.md#use-on-other-agent-platforms))
- `python3` for the helper script and Stop hook
- Git repository (worktree subagents need this)

## License

MIT
