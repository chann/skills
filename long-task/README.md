# long-task

[한국어](README.ko.md) · [← back to main](../README.md)

Autonomous orchestrator for **long-running, multi-milestone projects** that run for hours or days without human intervention.

## What it does

- Runs a Phase 1 (setup) → Phase 2 (orchestration loop) → Phase 3 (completion) workflow that takes a project from scratch to delivered
- Dispatches parallel **subagents in isolated git worktrees** (cap: 5 parallel) and merges them after verification
- Enforces an **architectural review cycle** at every milestone (review → fix subagents → re-review, max 3 iterations)
- Uses persistent `.agent/` state files as working memory so progress survives context compaction or session restarts
- Resolves ambiguity autonomously during execution — you only interact with the user during Phase 1 setup
- Includes ready-to-customize templates for `goal.md`, `plans.md`, `standards.md`, `implement.md`, `progress.md`

## Installation

**Recommended (global, one shot):**

```bash
npx skills add -y -g chann/skills@long-task
```

**Project-local:**

```bash
npx skills add chann/skills@long-task
```

**Manual:**

```bash
git clone https://github.com/chann/skills.git
ln -s "$(pwd)/skills/long-task/skills/long-task" ~/.claude/skills/long-task
```

## Usage

The skill triggers automatically on phrases like *"build this whole project end-to-end"*, *"do this autonomously"*, *"run a long task"*, or you can invoke it explicitly:

| Command       | Action                                                                  |
| ------------- | ----------------------------------------------------------------------- |
| `/long-task`  | Start Phase 1 setup interview, then run autonomous orchestration loop   |

**Examples:**

```
> /long-task build a TypeScript Express API with auth, posts, and comments
> implement this end-to-end and don't stop to ask questions
> run a long task to build the whole CLI from scratch
```

## How it works

1. **Phase 1 (Setup, only user interaction):** Interview the user, write `.agent/goal.md`, design milestones in `.agent/plans.md`, define `.agent/standards.md` and `.agent/implement.md`. Get final sign-off.
2. **Phase 2 (Orchestration loop):** Per milestone — re-read state, dispatch parallel implementer subagents in worktrees, verify (tests/lint/types), merge, dispatch architectural reviewer, run fix cycle, update `progress.md`. Repeat until all milestones complete.
3. **Phase 3 (Completion):** Final cross-cutting review on entire codebase, address critical issues, write final `progress.md` summary, report to user.

## State files (`.agent/`)

| File             | Purpose                                              | Updated when                              |
| ---------------- | ---------------------------------------------------- | ----------------------------------------- |
| `goal.md`        | Problem, outcome, acceptance criteria, non-goals     | Once, at setup                            |
| `plans.md`       | Architecture, milestones, tasks                      | At setup; appended on scope discovery     |
| `standards.md`   | Code quality bar (read by every subagent)            | Once                                      |
| `implement.md`   | Subagent workflow (read by every subagent)           | Once                                      |
| `progress.md`    | Current state, decisions, architecture summary       | After every action                        |

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
        └── references/
            └── project-templates.md       # Customizable .agent/ file templates
```

## Requirements

- An agent platform that supports skills ([Claude Code](https://code.claude.com), Codex, opencode, Copilot CLI, etc. — see [main README](../README.md#use-on-other-agent-platforms))
- Git repository (worktree subagents need this)

## License

MIT
