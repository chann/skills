# long-task

[한국어](README.ko.md) · [← back to main](../README.md)

Autonomous orchestrator for **long-running, multi-milestone projects** that run for hours or days without human intervention. Inspired by [jthack/claude-goal](https://github.com/jthack/claude-goal)'s `/goal` lifecycle, layered on top of a worktree-based parallel-subagent orchestrator.

## What it does

- Runs a **Phase 1 (setup) → Phase 2 (orchestration loop) → Phase 3 (completion)** workflow that takes a project from scratch to delivered
- Dispatches parallel **subagents in isolated git worktrees** (cap: 5 parallel) and merges them after verification
- Enforces an **architectural review cycle** at every milestone (review → fix subagents → re-review, max 3 iterations)
- Uses persistent `.agent/` state files as working memory so progress survives context compaction or session restarts
- Installs a **Stop hook** that auto-continues work across many turns while a long-task is active — no manual nudging needed
- Codex-style **lifecycle commands**: `/long-task status | pause | resume | clear | complete`
- **Completion audit** gate: `/long-task complete` writes a template that maps acceptance criteria to concrete evidence
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

The skill triggers automatically on phrases like *"build this whole project end-to-end"*, *"do this autonomously"*, *"run a long task"*, or you can invoke it explicitly:

| Command                      | Action                                                                              |
| ---------------------------- | ----------------------------------------------------------------------------------- |
| `/long-task <objective>`     | Phase 1 setup with this objective, then enter autonomous orchestration loop         |
| `/long-task`                 | Status if active, otherwise Phase 1 interactive setup                               |
| `/long-task status`          | Current state, phase, elapsed time, runaway counter, and `.agent/progress.md` tail |
| `/long-task pause`           | Disarm Stop hook auto-continuation until resumed                                    |
| `/long-task resume`          | Resume auto-continuation; runaway counter resets                                    |
| `/long-task clear`           | Delete `.agent/state.md`; preserves the rest of `.agent/*.md` for reference         |
| `/long-task complete`        | Write `.agent/audit.md` template, mark complete, disarm Stop hook                   |

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
2. **Phase 2 (Orchestration loop):** Per milestone — re-read state, dispatch parallel implementer subagents in worktrees, verify (tests/lint/types), merge, dispatch architectural reviewer, run fix cycle, update `progress.md`. Repeat until all milestones complete. Stop-hook auto-continues across turns.
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

## Credits

The lifecycle / Stop-hook design is a direct nod to [github.com/jthack/claude-goal](https://github.com/jthack/claude-goal), which clones codex's `/goal` into Claude Code. This plugin combines that mechanism with multi-milestone orchestration.

## License

MIT
