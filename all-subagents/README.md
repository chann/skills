# all-subagents

[한국어](README.ko.md) · [← back to main](../README.md)

Routes work asked for through subagents to another installed coding agent,
records why that route was chosen, and leaves the result with a call tree.

## What it does

- Probes Codex, Claude Code, OpenCode 2.x, and Antigravity, and skips anything
  that is missing or not authenticated
- Records a route plan with a rationale and a quota transcript, and rejects a
  plan that invents a number or reuses one vendor for independent checks
- Runs the selected CLI with a prompt file, a sandbox posture, and an optional
  Git guard
- Writes `report.md` naming each agent, model, outcome, and whether the write
  set held

The run directory lives under `$XDG_CACHE_HOME/all-subagents/runs/<run-id>/`,
or `~/.cache/all-subagents/runs/<run-id>/` when `XDG_CACHE_HOME` is unset.

## Installation

**Global:**

```bash
npx skills add -y -g chann/skills --skill all-subagents
```

**Project-local:**

```bash
npx skills add chann/skills --skill all-subagents
```

Use the actual skill name with `--skill`. This plugin packages the
`all-subagents` skill.

**Manual:**

```bash
git clone https://github.com/chann/skills.git
ln -s "$(pwd)/skills/all-subagents/skills/all-subagents" ~/.claude/skills/all-subagents
```

## Usage

| Claude Code | Codex | Action |
| --- | --- | --- |
| `/all-subagents [task]` | `$all-subagents [task]` | Hand the task to another coding agent and write the call-tree report |

Examples:

```text
/all-subagents use subagents to review the auth diff
$all-subagents 서브에이전트로 이 리뷰 돌려줘
/all-subagents ask Codex to review the auth diff
```

A multi-milestone project stays with `/long-task`. A cited brief stays with
`/research-brief`. A defect report written in this session stays with
`/code-review`.

When only one usable route exists and the user did not name an agent or model,
the work stays in the current session.

## Package layout

```text
all-subagents/
├── .claude-plugin/plugin.json
├── commands/all-subagents.md
└── skills/all-subagents/
    ├── SKILL.md
    ├── agents/openai.yaml
    ├── evals/evals.json
    ├── assets/prompts/common.md
    ├── references/
    └── scripts/all_subagents.py
```

## Requirements

- An agent platform that supports skills
- Python 3.10+
- At least one of `codex`, `claude`, `opencode` 2.0.0 or newer, or `agy` when a
  task should actually leave this session

## License

MIT
