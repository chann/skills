# bug-hunt

[한국어](README.ko.md) · [← back to main](../README.md)

Diagnose a broken behavior with a trail behind it: a reproduction you recorded, a
ledger of hypotheses you tried to kill, and a fix pinned by a check that failed
first.

## Why it is different

Most debugging loses its own history. Three hypotheses get tried, two are
silently abandoned, the fix lands — and the next session starts from zero and
retries the abandoned two.

`bug-hunt` keeps the trail in `.bug-hunts/<date>-<slug>.md`, written as the hunt
runs rather than summarized at the end. Four things make it more than a log:

- **Falsification, not confirmation.** Every hypothesis is written with the
  observation that would prove it wrong, before that observation is collected.
  Looking for agreement finds it every time.
- **The widening rule.** After three falsified hypotheses in the same layer, the
  search must move to a different layer or assumption, and the record says which.
  Three failures in a row is information; generating a fourth in the same place
  throws it away.
- **Falsified hypotheses stay.** The dead lines are the most valuable part of the
  record — they stop the next session repeating your work.
- **Provable cleanup.** Temporary probes carry a `BUGHUNT` marker, so removal is
  a search rather than a promise.

## Installation

Global:

```bash
npx skills add -y -g chann/skills --skill bug-hunt
```

Project-local:

```bash
npx skills add chann/skills --skill bug-hunt
```

## Usage

| Claude Code | Codex | Action |
|---|---|---|
| `/bug-hunt [symptom or failing command]` | `$bug-hunt [symptom or failing command]` | Reproduce, falsify hypotheses in a ledger, pin the fix, and leave a diagnosis record |

Examples:

```text
/bug-hunt the /search endpoint takes 4s at p50 and took 300ms last week
$bug-hunt src/rank.test.ts fails about one run in fifty
/bug-hunt 로그인 후 세션이 가끔 사라져
```

## The loop

1. **State the defect** — symptom, expected, environment, first seen.
2. **Reproduce** — a command that fails, recorded verbatim, then minimized. No
   reproduction means the non-reproduction is the finding.
3. **Work the ledger** — one falsifiable hypothesis per round, one variable at a
   time, instrumented rather than guessed.
4. **Pin the fix** — a check that fails for the defect's reason, then passes.
5. **Clean up** — prove every `BUGHUNT` probe is gone and re-run the project's checks.
6. **Close the record** — cause, fix, falsified list, blast radius, left open.

## What it refuses

- Fixing a defect that never reproduced
- Applying a fix before a check fails for the defect's reason
- A fourth hypothesis in a layer that produced three falsified ones
- Deleting a falsified hypothesis to make the record read better
- Weakening, skipping, or retry-wrapping a test to make a failure disappear
- Leaving a `BUGHUNT` probe behind

## Package layout

```text
bug-hunt/
├── .claude-plugin/plugin.json
├── commands/bug-hunt.md
├── skills/bug-hunt/
│   ├── SKILL.md
│   ├── agents/openai.yaml
│   ├── evals/evals.json
│   └── references/instrumentation-playbook.md
├── README.md
└── README.ko.md
```

## Requirements

- An agent platform that supports skills
- Permission to run the project's own tests and checks

## License

MIT
