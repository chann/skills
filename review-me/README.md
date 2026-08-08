# review-me

[한국어](README.ko.md) · [← back to main](../README.md)

A read-only review that follows every relevant decision in a plan, design, or
important choice. It asks one question at a time, recommends a concrete answer,
continues through any choices uncovered by that answer, and finishes only after
every decision is recorded and confirmed.

## Why it is different

`review-me` distinguishes “we discussed the topic” from “the decision is
complete.” A decision is complete only when its exact choice, boundaries,
alternatives, broader consequences, and observable proof are explicit. Before
claiming completion, the skill checks that every relevant point of view has
been covered.

This skill is inspired by Matt Pocock's
[`grill-me`](https://github.com/mattpocock/skills/tree/main/skills/productivity/grill-me)
and
[`grilling`](https://github.com/mattpocock/skills/tree/main/skills/productivity/grilling)
skills. It builds the interview loop into the skill, follows newly uncovered
decisions, checks each one for missing details, and asks the user to confirm the
final record.

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
| `/review-me [topic]` | `$review-me [topic]` | Review one decision at a time until every relevant choice is resolved |

Examples:

```text
/review-me our team invitation plan
$review-me review the caching design we just discussed
```

The skill uses the command argument when supplied and otherwise reviews the
current conversation. It inspects available evidence for facts, but leaves
consequential choices to the user.

## How the conversation works

- One active question per turn
- A specific recommendation and decisive tradeoff for every question
- Review dependencies first; revisit affected choices when an earlier decision changes
- Check every decision for its choice, boundary, alternatives, consequences, and proof
- Finish by accounting for items that were resolved, did not apply, or were deliberately deferred
- Keep the review read-only until the final decision record is confirmed

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
