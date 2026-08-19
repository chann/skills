---
name: research-brief
description: Use when a technical question must be answered from primary sources and the answer needs to survive being quoted later, including "이거 공식 문서에서 확인해줘", "어떤 방식이 맞는지 근거까지 찾아줘", "라이브러리 동작 조사해줘", "research how this API behaves", "find out whether X supports Y", "check the spec on this", "/research-brief", or "$research-brief". Produces a cited brief under `.research/` with a bottom-line answer, a claim table naming each source's tier and verified version, a contradiction ledger, and mandatory open questions. For summarizing a document you already have use plan-summary instead.
---

# Research Brief

Answer a technical question from the sources that own the answer, and leave a
brief someone can check six months from now.

Two failures make research worthless. The first is confident prose with no
source behind it. The second is a source that was right when it was read and is
wrong now, with nothing in the document to reveal that. Both come from the same
missing habit: not writing down where a claim came from and what it was true of.

Every claim in the brief carries its source, that source's tier, and the version
or date it was verified against. A claim that cannot carry those does not go in
the brief — it goes in **Open questions**.

The artifact is `.research/<YYYY-MM-DD>-<slug>.md`.

## 1. Sharpen the question

Restate the question as one sentence that a source could answer or refuse. Then
write, into the brief:

- **The question** — the sharpened version.
- **Why it is being asked** — the decision it feeds, so scope stays honest.
- **What would settle it** — the observation, spec line, or source file that
  would end the argument.

"Should we use X?" is not answerable by a source; "Does X support Y in version
Z, and what does it do when the input is empty?" is. Split a question that hides
two questions, and answer them separately.

If the question is really about a document the user already has, say so and route
it to `plan-summary`. Research is for material that is not yet in hand.

## 2. Delegate the reading when you can

When the platform can run a background agent, dispatch one to do the reading so
the user keeps working. Seed it with the sharpened question, the source tiers,
the claim-table format, and the output path — not with a topic. A background
agent given a topic returns an essay; given a question and a format it returns
evidence.

When no background agent is available, do the reading inline and say so. Never
skip the reading because delegation was unavailable.

## 3. Read the source that owns the answer

Follow every claim back to the source that owns it, not to a write-up about that
source. Tier each source as you use it:

| Tier | What it is | How it may be written |
|---|---|---|
| **T1** | The specification, the official reference, the first-party source code, the API's own response | As fact, with the source |
| **T2** | First-party secondary material — changelog, release note, maintainer's post, official blog | As fact, marked T2, with its date |
| **T3** | Community material — Stack Overflow, third-party blog, forum, another model's answer | Only as **unverified**, never as fact |

Rules that keep the tiers meaningful:

- **A T3 claim is a lead, not an answer.** Use it to find the T1 source, then
  cite the T1 source. If the T1 source cannot be found, the claim stays labeled
  unverified in the brief and appears in Open questions.
- **Read the source, not the search result.** A search snippet is not the source;
  open it. Snippets are frequently stale or truncated mid-qualifier.
- **Prefer the source code when the docs are ambiguous.** Behavior lives in the
  implementation; the docs are a description of it that can drift.
- **Record what you could not reach.** A paywalled spec or a private repository is
  a limitation of the brief, not a gap to fill with a guess.

## 4. Pin every claim to a version

Software claims expire. Each claim records what it was verified against:

- A library or framework claim records the **version** — `4.2.1`, not "latest".
- A service or API claim records the **date** it was verified, because the
  provider can change it without a version.
- A spec claim records the **spec revision or section**.

This is what lets a reader tell a stale brief from a wrong one, which are
different problems with different fixes.

## 5. Record contradictions instead of resolving them silently

When two sources disagree, both go in the brief with the resolution and its
reason:

```markdown
| Claim | Source A | Source B | Resolution |
|---|---|---|---|
| Default timeout is 30 s | Docs (T1, v4.2) say 30 s | Source code (T1, v4.2) sets 10 s | Code wins; the docs were not updated with the 4.1 change. Filed as an open question. |
```

Picking one and deleting the other destroys the most useful thing you found. A
disagreement between two T1 sources is a finding in its own right, and it is
usually where the bug the user is chasing lives.

## 6. Write the brief

```markdown
# <question>

## Bottom line
<the direct answer, two or three sentences>
**Confidence:** high | medium | low — <what would raise it>

## Claims
| # | Claim | Source | Tier | Verified against | Confidence |
|---|---|---|---|---|---|

## Detail
<the reasoning, one section per part of the question>

## Contradictions
<disagreeing sources, both cited, with the resolution and its reason>

## Open questions
<what is unresolved, what would resolve it, and why it was not resolved here>

## Sources
<full list with URLs and access dates>
```

**Bottom line first.** The reader wants the answer, then the evidence. A brief
that makes them read to the end to learn the answer will not be read.

**Confidence is about the evidence, not the writing.** High confidence means a T1
source states it directly for the version in question. Fluent prose over T3
sources is low confidence, however certain it sounds.

**Open questions is mandatory.** If it is genuinely empty, say why in one line —
"every claim is T1 against v4.2.1 and no source disagreed." An empty section with
no explanation reads as an unasked question.

## Refusals

- Do not state a T3 claim as fact. Find the T1 source or label it unverified.
- Do not cite a search snippet as a source. Open the source.
- Do not write a claim without the version or date it was verified against.
- Do not resolve a contradiction by deleting one side.
- Do not fill a gap with a plausible answer. Gaps go in Open questions.
- Do not present the brief as complete while a question in scope is unanswered;
  say which part is unanswered.

## Integration

**Pairs with:** `review-me` when the research feeds a decision that needs closing,
`bug-hunt` when the question came out of a diagnosis, and `gen-docs` when the
findings belong in project documentation.

**Use instead of:** `plan-summary`, which summarizes a document the user already
has. This skill goes and finds the material.
