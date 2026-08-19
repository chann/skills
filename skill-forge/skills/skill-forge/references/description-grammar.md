# Description grammar

A skill's `description` is the only text the model reads before deciding whether
to load the skill. Everything else — the workflow, the references, the scripts —
is invisible until that decision is already made. A skill that is never selected
is a skill that does not exist, and a skill selected on the wrong request is
worse than one that is never selected.

Write the description for the selection decision, not as a summary.

## The four parts

Every description carries the same four parts, in this order.

**1. The opening clause.** `Use when` or `Use only when`. This is a contract with
the frontmatter, not a stylistic choice — see C3 in the contract.

**2. The triggers.** The phrasings a user actually types, in every language the
skill serves. Take them from real requests, not from how you would name the
feature. A user who wants a change explained types "이 변경 뭐 바뀐 거야" long
before they type "diff summary". Include the literal `/<name>` and `$<name>`
selectors so an explicit invocation always matches.

**3. The output.** What the run leaves behind — a file, a report, a commit, a
decision record. This is what separates two skills that share a subject.
"Reviews code" describes four skills; "produces severity-tagged findings as
Markdown plus a self-contained HTML report under `.reviews/`" describes one.

**4. The disambiguation.** When a sibling skill is a near neighbour, name it and
the condition that selects it instead. Without this the model picks by coin
flip, and the user gets HTML when they asked for Markdown.

## Trigger vocabulary

Collect triggers from three sources and keep all three:

- **Task words** — what the user is trying to do: "review", "요약", "커밋",
  "clean up merged branches".
- **Artifact words** — what they expect back: "리포트", "quiz", "handoff",
  "markdown file".
- **Selectors** — `/<name>` and `$<name>`.

Prefer verbatim phrases over categories. `"main..dev 코드를 요약해줘"` selects
correctly; `"summarization requests"` does not.

## Boundaries

State what the skill is not, when the negative space is where mistakes happen:

- `Korean text only; not a spell-checker, not a translator, never changes content.`
- `for one Git change use diff-summary instead`

A boundary clause costs one sentence and prevents a whole class of wrong runs.

## Failure modes

| Symptom | Cause | Fix |
|---|---|---|
| Skill never fires | Description names the feature, not the request | Add verbatim user phrasings |
| Skill fires on unrelated work | Trigger words are generic ("code", "file") | Add the artifact and the boundary |
| Two siblings fire at random | Neither names the other | Add the disambiguation clause to both |
| Explicit invocation is ignored | `/name` or `$name` missing | Add both selector tokens |
| Skill starts on its own | `Use when` on a workflow that should be selector-only | Switch to `Use only when` and set `disable-model-invocation: true` |

## Length

Aim for two to four sentences. Long is fine when the triggers earn it — a skill
serving four languages needs the room. Long is not fine when it comes from
restating the workflow: the workflow belongs in the body, which loads only after
the skill is selected.

## Worked example

Too thin — no triggers, no output, no neighbour:

```
description: Summarizes a git diff.
```

Contract-conformant:

```
description: Use when the user wants an explanatory code, diff, branch, commit,
  or PR change summary, including "코드를 요약해줘", "변경사항을 요약해줘",
  "summarize this diff", "what changed between branches", "/diff-summary", or
  "$diff-summary". Produces evidence-based purpose, behavior, architecture,
  contracts, tests, and operations in Markdown and interactive HTML. Use
  diff-summary-md for a Markdown-only artifact, diff-summary-quiz for a
  comprehension quiz, and code-review for defects and risks.
```
