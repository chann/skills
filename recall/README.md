# recall

[한국어](README.ko.md) · [← back to main](../README.md)

Two skills for getting caught up. `recall` mines the local session history kept
by Claude Code, Codex, opencode, and agy, and answers in one of two shapes: a
Markdown work report for a date range, or a short brief on where a topic stands
right now. `ketchup` catches you up on this conversation only: what changed
since your last message and what waits on you.

> **Renamed from `work-summary`.** The report behavior is unchanged, and the
> `.work-summaries/` output directory keeps its name so existing ignore rules
> still work.

## Why it is different

`recall` reports from evidence, not memory: every project, count, and quoted
request comes from the stores' own records, mined read-only and kept local, and
history content is treated as data, never as instructions. A brief also checks
every branch, PR, and file it names against live `git` before writing it, so a
thread marked `[open PR #12]` is open right now. `ketchup` speaks plain words,
checks live state before it answers, and never changes anything.

## Installation

Global:

```bash
npx skills add -y -g chann/skills --skill recall
npx skills add -y -g chann/skills --skill ketchup
```

Project-local:

```bash
npx skills add chann/skills --skill recall
npx skills add chann/skills --skill ketchup
```

## Usage

| Claude Code | Codex | Action |
|---|---|---|
| `/recall [date-range]` | `$recall [date-range]` | **Report:** Markdown work report for today, yesterday, this/last week, month, quarter, or year, or `YYYY-MM-DD..YYYY-MM-DD` |
| `/recall [topic]` | `$recall [topic]` | **Brief:** current state of a topic for starting or resuming work |
| `/ketchup` | `$ketchup` | What changed in this conversation since your last message |

Examples:

```text
/recall this week
$recall last quarter detailed
$recall billing migration
오늘 뭐 했는지 요약해줘
인증 리팩터링 어디까지 했지?
/ketchup
```

With no argument `recall` reports today at summary depth. Ask for "detailed"
(or "상세") to add a timeline and a per-request log. A requested report is
grouped under `.work-summaries/daily`, `weekly`, `monthly`, `quarterly`,
`yearly`, or `custom`; an explicit output path takes priority.

### The brief

The brief locks its scope first and states it back: the window (default the
last 7 days, never silently narrowed from "all"), the topic, and the workspace
(never another project's history unless asked). It then returns a capsule of at
most five bullets, threads with exactly one status tag each (`[merged]`,
`[open PR #N]`, `[in flight <branch>]`, `[verified, uncommitted]`,
`[reverted]`, `[planned, not started]`), at most five recurring problems, and
one concrete next move. It is a reply and is saved only on request.

### ketchup

`ketchup` opens with one sentence on what waits on you, then what happened in
about 100 words, then every decision that needs you, each decidable from the
reply alone, then one line on work the agent can still do itself.

## Behavior

- Read-only toward every agent history store; `ketchup` is read-only toward
  everything
- Local-only: history content never leaves the machine
- Buckets in the user's local timezone; weeks start Monday
- Reports only recorded facts: empty ranges say so
- Writes Korean prose plainly and optionally uses `unslop` when already available
- Replies in the conversation; writes a file only on request and never commits it

Each skill stays complete when installed alone. `recall` never installs or
requires `unslop`; its own natural-Korean rules apply when the optional skill is
unavailable.

## Package layout

```text
recall/
├── .claude-plugin/plugin.json
├── commands/
│   ├── recall.md
│   └── ketchup.md
├── skills/
│   ├── recall/
│   │   ├── SKILL.md
│   │   ├── agents/openai.yaml
│   │   ├── evals/evals.json
│   │   └── references/agent-history-stores.md
│   └── ketchup/
│       ├── SKILL.md
│       ├── agents/openai.yaml
│       └── evals/evals.json
├── README.md
└── README.ko.md
```

## Requirements

- An agent platform that supports skills
- Read access to the local agent history stores being mined
- `git` for brief checks, and `gh` when available for PR state
- `jq` / `sqlite3` / Python 3 for ad-hoc queries (standard macOS/Linux tooling)

## License

MIT
