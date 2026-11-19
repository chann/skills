# understand

[한국어](README.ko.md) · [← back to main](../README.md)

Two read-only questions about a codebase, kept apart on purpose: `how` explains
how it works from the code, and `why` explains why it is that way from the
record.

## Why it is different

An agent asked "why is it built this way" usually answers from the shape of the
code and sounds sure. That is a guess dressed as history. These two skills split
the question by its source of truth:

- **`how` reads code.** Every claim carries a `file:line`; anything not read is
  labelled `inferred`; the answer always names what was not read.
- **`why` reads the record.** Commits, blame, pull-request and issue threads, and
  design notes. It quotes the authors, marks its own reading, and says plainly
  what the record does not answer.

Both are read-only and neither requires the other.

## Installation

Global:

```bash
npx skills add -y -g chann/skills --skill how --skill why
```

Project-local:

```bash
npx skills add chann/skills --skill how --skill why
```

## Usage

| Claude Code | Codex | Action |
|---|---|---|
| `/how <question>` | `$how <question>` | Explain how part of the codebase works, with `file:line` citations |
| `/why <question>` | `$why <question>` | Explain why it is built this way, as a quoted decision timeline |

Examples:

```text
/how does the job scheduler pick the next task
$how where should a new retry helper live
/why did we pick Postgres advisory locks over Redis
$why 이 플래그 왜 아직 꺼져 있어?
```

## What each answer contains

| Skill | Shape |
|---|---|
| `how` | Overview · Key concepts · Runtime flow · Code map · Gotchas |
| `why` | Short answer with confidence · decision timeline (commit or PR, date, quote) · inferences · what the record does not answer |

## What it refuses

- Editing files, committing, or posting comments
- Describing code from names alone, or explaining motivation from code shape
- Stating a reason that no commit, pull request, issue, or note gives

## Which skill to use

| You want | Use |
|---|---|
| How it works today | `how` |
| Why it is that way | `why` |
| An external library or spec | `research-brief` |
| What one change did | `diff-summary` |
| Something is broken | `bug-hunt` |
| Your own earlier sessions | `recall` |

## Package layout

```text
understand/
├── .claude-plugin/plugin.json
├── commands/how.md
├── commands/why.md
├── skills/how/
│   ├── SKILL.md
│   ├── agents/openai.yaml
│   └── evals/evals.json
├── skills/why/
│   ├── SKILL.md
│   ├── agents/openai.yaml
│   └── evals/evals.json
├── README.md
└── README.ko.md
```

## Requirements

- An agent platform that supports skills
- `git`; `gh` is optional and widens what `why` can read

## License

MIT
