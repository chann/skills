# swarm

[한국어](README.ko.md) · [← back to main](../README.md)

Two ways to put more than one agent on a job:

- **`swarm`** fans one job out to subagents or other installed coding agents,
  records why each route was chosen, reads every result, and returns one
  report with a call tree.
- **`arena`** runs the same task on several competing candidates, has a judge
  from another vendor score them, and grafts the best parts onto one base.

> `all-subagents` was renamed `swarm` in 1.0.0.

## What `swarm` does

- **Frame:** states the done predicate and the single return, and picks a
  shape: `partition` (disjoint slices), `race` (one brief on different
  routes, with a selection rule declared up front), or a mix
- **Fan out:** probes Codex, Claude Code, OpenCode 2.x, and Antigravity,
  records a route plan with a rationale and a quota transcript, and rejects a
  plan that invents a number or reuses one vendor for independent steps
- **Aggregate:** reads each `PASS`, `ISSUES`, or `BLOCKED` result itself,
  reruns an incomplete one once, and records a gap instead of a pass
- **Report:** one result table with verdicts, issues, gaps, and the call tree
  from `report.md`

The run directory lives under `$XDG_CACHE_HOME/swarm/runs/<run-id>/`, or
`~/.cache/swarm/runs/<run-id>/` when `XDG_CACHE_HOME` is unset.

## What `arena` does

- Names the artifact, writes a hidden rubric of three to six criteria, and
  gives every candidate the same prompt and its own output location
- Seats candidates through `swarm` when it is installed, so they land on
  different vendors
- Runs one read-only judge on neutral labels, then reads every candidate
  before picking a base
- Grafts one or two things from each loser by hand and verifies the result

## Installation

**Global:**

```bash
npx skills add -y -g chann/skills --skill swarm
npx skills add -y -g chann/skills --skill arena
```

**Project-local:**

```bash
npx skills add chann/skills --skill swarm
npx skills add chann/skills --skill arena
```

Use the actual skill name with `--skill`. This plugin packages the `swarm` and
`arena` skills.

**Manual:**

```bash
git clone https://github.com/chann/skills.git
ln -s "$(pwd)/skills/swarm/skills/swarm" ~/.claude/skills/swarm
ln -s "$(pwd)/skills/swarm/skills/arena" ~/.claude/skills/arena
```

## Usage

| Claude Code | Codex | Action |
| --- | --- | --- |
| `/swarm <task>` | `$swarm <task>` | Fan the task out to subagents or other coding agents and report with the call tree |
| `/arena <task>` | `$arena <task>` | Run competing attempts at one artifact, cross-judge them, and graft the best |

Examples:

```text
/swarm use subagents to review the auth diff
$swarm 병렬로 나눠서 돌려줘
/swarm ask Codex to review the auth diff
/arena give me three attempts at the config loader API and pick the best
$arena 여러 안 만들어서 비교해줘
```

A multi-milestone project stays with `/long-task`. A cited brief stays with
`/research-brief`. A defect report written in this session stays with
`/interrogate`. An interview about a plan's decisions is `/review-me`.

When only one usable route exists and the user did not name an agent or model,
`swarm` keeps the work in the current session. `arena` refuses a mechanical
task whose shape is already settled.

## Package layout

```text
swarm/
├── .claude-plugin/plugin.json
├── commands/
│   ├── swarm.md
│   └── arena.md
└── skills/
    ├── swarm/
    │   ├── SKILL.md
    │   ├── agents/openai.yaml
    │   ├── evals/evals.json
    │   ├── assets/prompts/common.md
    │   ├── references/
    │   └── scripts/swarm.py
    └── arena/
        ├── SKILL.md
        ├── agents/openai.yaml
        └── evals/evals.json
```

## Requirements

- An agent platform that supports skills
- Python 3.10+ for `swarm`
- At least one of `codex`, `claude`, `opencode` 2.0.0 or newer, or `agy` when a
  task should actually leave this session

## License

MIT
