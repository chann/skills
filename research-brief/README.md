# research-brief

[한국어](README.ko.md) · [← back to main](../README.md)

Answer a technical question from the sources that own the answer, and leave a
brief someone can still check six months from now.

## Why it is different

Two failures make research worthless. The first is confident prose with no source
behind it. The second is a source that was right when it was read and is wrong
now, with nothing in the document to reveal that.

`research-brief` fixes both by making every claim carry its own provenance:

- **Source tiers.** T1 is the spec, the official reference, the first-party source
  code. T2 is first-party secondary material — changelog, maintainer post. T3 is
  community material, which may only be written as *unverified*. A T3 claim is a
  lead to the T1 source, not an answer.
- **Version pinning.** Every claim records the version or date it was verified
  against — `4.2.1`, not "latest". This is what lets a reader tell a stale brief
  from a wrong one, which are different problems.
- **A contradiction ledger.** When two sources disagree, both stay in the brief
  with the resolution and its reason. Picking one and deleting the other destroys
  the most useful thing the research found — and a disagreement between two T1
  sources is often exactly where the bug lives.
- **Mandatory open questions.** An empty section must say why it is empty. A
  brief with nothing unresolved and no explanation is a brief that stopped asking.

Answer first, evidence second: the bottom line and its confidence sit at the top,
because a brief that hides the answer at the end does not get read.

## Installation

Global:

```bash
npx skills add -y -g chann/skills --skill research-brief
```

Project-local:

```bash
npx skills add chann/skills --skill research-brief
```

## Usage

| Claude Code | Codex | Action |
|---|---|---|
| `/research-brief [question]` | `$research-brief [question]` | Answer the question from primary sources and write a cited brief under `.research/` |

Examples:

```text
/research-brief does our HTTP client retry idempotent requests by default?
$research-brief what does this API return when the page cursor is expired?
/research-brief 이 라이브러리 기본 타임아웃 몇 초인지 공식 문서로 확인해줘
```

Where the platform can run a background agent, the reading is delegated so you
keep working; the agent is seeded with the question, the tiers, and the output
format rather than a topic.

## The brief

```markdown
# <question>
## Bottom line          ← the answer plus confidence
## Claims               ← claim | source | tier | verified against | confidence
## Detail
## Contradictions
## Open questions        ← mandatory
## Sources
```

## What it refuses

- Stating a T3 community claim as fact
- Citing a search snippet instead of opening the source
- A claim with no version or date behind it
- Resolving a contradiction by deleting one side
- Filling a gap with a plausible answer
- Calling the brief complete while a question in scope is unanswered

## Package layout

```text
research-brief/
├── .claude-plugin/plugin.json
├── commands/research-brief.md
├── skills/research-brief/
│   ├── SKILL.md
│   ├── agents/openai.yaml
│   └── evals/evals.json
├── README.md
└── README.ko.md
```

## Requirements

- An agent platform that supports skills
- Access to the sources being researched (web or repository reads)

## License

MIT
