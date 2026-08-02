# work-summary

[한국어](README.ko.md) · [← back to main](../README.md)

A date-ranged Markdown reporter over the session history your coding agents
already keep locally — Claude Code, Codex, opencode, and agy. Ask for today,
this week, this month, or an explicit span and get a summary or a detailed
report of what was asked and what was done.

## Why it is different

`work-summary` reports from evidence, not memory: every project, count, and
quoted request comes from the stores' own records, mined read-only and kept
local. Absent tools are skipped silently, empty ranges are reported honestly,
and nothing is ever staged, committed, or sent to an external service.

## Installation

Global:

```bash
npx skills add -y -g chann/skills --skill work-summary
```

Project-local:

```bash
npx skills add chann/skills --skill work-summary
```

## Usage

| Claude Code | Codex | Action |
|---|---|---|
| `/work-summary [range]` | `$work-summary [range]` | Markdown work report for today, yesterday, this/last week, this/last month, or `YYYY-MM-DD..YYYY-MM-DD` |

Examples:

```text
/work-summary this week
$work-summary detailed report for 2026-07-01..2026-07-31
오늘 뭐 했는지 요약해줘
```

With no argument it reports today at summary depth. Ask for "detailed" (or
"상세") to add a timeline and a per-request log; ask for a file to save the
report under `.work-summaries/`.

## Interaction contract

- Read-only toward every agent history store
- Local-only: history content never leaves the machine
- Buckets in the user's local timezone; weeks start Monday
- Reports only recorded facts — empty ranges say so
- Replies with Markdown; writes a file only on request and never commits it

## Package layout

```text
work-summary/
├── .claude-plugin/plugin.json
├── commands/work-summary.md
├── skills/work-summary/
│   ├── SKILL.md
│   ├── agents/openai.yaml
│   ├── evals/evals.json
│   └── references/agent-history-stores.md
├── README.md
└── README.ko.md
```

## Requirements

- An agent platform that supports skills
- Read access to the local agent history stores being mined
- `jq` / `sqlite3` / Python 3 for ad-hoc queries (standard macOS/Linux tooling)

## License

MIT
