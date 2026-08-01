# review-me

[한국어](README.ko.md) · [← back to main](../README.md)

A read-only decision-tree review that follows a plan, design, or consequential
choice down to every applicable leaf. It asks one question at a time, recommends
a concrete answer, expands each answer into downstream decisions, and finishes
with a confirmed closure record.

## Why it is different

`review-me` treats “we discussed the topic” and “the decision is complete” as
different states. A leaf closes only when its exact choice, boundaries, variants,
cross-cutting consequences, and observable proof are all explicit. An audit then
accounts for every applicable lens before the skill claims completion.

This skill is inspired by Matt Pocock's
[`grill-me`](https://github.com/mattpocock/skills/tree/main/skills/productivity/grill-me)
and
[`grilling`](https://github.com/mattpocock/skills/tree/main/skills/productivity/grilling)
skills. It internalizes the interview loop and extends it with a recursive
decision frontier, leaf-closure tests, lens accounting, and a final confirmation
record.

## Installation

Global:

```bash
npx skills add -y -g chann/skills --skill review-me
```

Project-local:

```bash
npx skills add chann/skills --skill review-me
```

## Usage

| Claude Code | Codex | Action |
|---|---|---|
| `/review-me [topic]` | `$review-me [topic]` | Review one decision at a time until every applicable leaf is closed |

Examples:

```text
/review-me our team invitation plan
$review-me review the caching design we just discussed
```

The skill uses the command argument when supplied and otherwise reviews the
current conversation. It inspects available evidence for facts, but leaves
consequential choices to the user.

## Interaction contract

- One active question per turn
- A specific recommendation and decisive tradeoff for every question
- Dependency-first traversal with descendants reopened when an ancestor changes
- Five closure tests for every leaf: choice, boundary, variants, consequences,
  and proof
- A final audit of resolved, not-applicable, and deliberately deferred lenses
- Read-only review until the closure record is confirmed

This is for reviewing plans, designs, product behavior, architecture, and other
decisions. Use `/code-review` or `$code-review` to inspect a Git diff for defects.

## Package layout

```text
review-me/
├── .claude-plugin/plugin.json
├── commands/review-me.md
├── skills/review-me/
│   ├── SKILL.md
│   ├── agents/openai.yaml
│   ├── evals/evals.json
│   └── references/review-lenses.md
├── README.md
└── README.ko.md
```

## Requirements

- An agent platform that supports skills
- Read access to any evidence placed in review scope

## License

MIT
