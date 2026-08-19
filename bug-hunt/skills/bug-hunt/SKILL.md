---
name: bug-hunt
description: Use when something is broken, throwing, failing, flaky, or slower than it should be and the cause is not obvious, including "버그 원인 찾아줘", "이거 왜 안 되는지 추적해줘", "테스트가 간헐적으로 깨져", "성능이 갑자기 느려졌어", "diagnose this bug", "find the root cause", "this test is flaky", "/bug-hunt", or "$bug-hunt". Reproduces first, falsifies hypotheses in a written ledger, pins the fix with a check that failed for the defect's reason, and leaves a diagnosis record under `.bug-hunts/`. For defects found by reading a diff use code-review instead.
---

# Bug Hunt

A hunt that leaves a trail. Most debugging loses its own history: three
hypotheses get tried, two are silently abandoned, the fix lands, and the next
person — or the next session — starts from zero and retries the abandoned two.

This workflow keeps the trail. Every hypothesis is written down with the
observation that would kill it and the observation that actually came back.
Falsified hypotheses stay in the record. The fix is pinned by a check that
failed for the defect's reason before it passed.

The artifact is `.bug-hunts/<YYYY-MM-DD>-<slug>.md`. Create it at step 1 and
keep writing to it as you go — a record written at the end is a summary, not a
trail.

## 1. State the defect as an observation

Write, into the record:

- **Symptom** — what was observed, in the reporter's words.
- **Expected** — what should have happened instead.
- **Environment** — versions, platform, configuration, and whether it happens
  elsewhere.
- **First seen** — and, if known, the last version where it did not happen.

Where the project keeps a domain or architecture document, read it now so the
record uses the project's own vocabulary rather than inventing parallel names.

Ambiguity here costs the whole hunt. "It's slow" is not a defect statement; "the
`/search` endpoint takes 4 s at p50, and took 300 ms last week" is. Ask only for
what you cannot observe yourself.

## 2. Reproduce before touching product code

Find a command that fails, and record it verbatim. Nothing else happens until
this exists.

```
Reproduction: pnpm vitest run src/search/rank.test.ts -t "ranks by recency"
Result: fails, 3 of 5 runs
```

If it reproduces intermittently, record the rate. A 3-in-5 failure and a
1-in-500 failure are different bugs with different techniques.

**If it does not reproduce**, that is the finding. Record what you tried, say so
plainly, and stop rather than fixing code speculatively. A fix for a defect you
never saw cannot be verified, and it hides the real one.

Then minimize: remove inputs, config, and code paths until removing anything
more makes the failure disappear. Record the minimal case. Most hunts are won
here — a small enough reproduction usually names its own cause.

## 3. Work the hypothesis ledger

Each round takes one hypothesis and tries to kill it. Write all four columns
before you run anything:

```markdown
| # | Hypothesis | Falsified if | Observed | Verdict |
|---|---|---|---|---|
| 1 | The comparator reads a stale timestamp | Logged timestamps match the fixture | Matched exactly | falsified |
| 2 | Two records share a sort key, so order is unstable | Keys are unique in the fixture | Two records share key `a3f` | survived |
```

Rules that make the ledger worth keeping:

- **Falsification, not confirmation.** Pick the observation that would prove the
  hypothesis wrong, and go get it. Looking for agreement finds it every time.
- **One variable per round.** Two changes at once means the next observation
  explains nothing.
- **Instrument, do not speculate.** A hypothesis you cannot observe is not ready
  — narrow it until it is. See
  [`references/instrumentation-playbook.md`](references/instrumentation-playbook.md).
- **Keep the dead ones.** A falsified hypothesis is the most valuable line in
  the record; it is the one that stops the next session repeating your work.

### The widening rule

After **three** falsified hypotheses inside the same layer, stop generating a
fourth there. The layer is probably the wrong place to look. Move deliberately:

| From | To |
|---|---|
| Application code | The library, runtime, or platform beneath it |
| The failing component | The data flowing into it |
| Logic | Timing, ordering, concurrency, caching |
| Your code | Your assumption about what the code you called guarantees |

Write the widening into the record as its own line, naming the assumption you
are now doubting. Three falsified hypotheses in a row is information, and
silently generating a fourth in the same layer throws it away.

## 4. Pin the fix with a failing check

Before the fix goes in, there must be a check that fails **for the defect's
reason** — not for a missing file, a typo in the test, or a stubbed
dependency. Read the failure output and confirm it names the defect.

Then fix the cause the ledger identified, and confirm the check passes. Record
both the failing and the passing output.

Where the project practices test-first work, this is the same red-green loop
written down; where it does not, the check may be a script or a command, but it
must still fail first.

**Fix the cause, not the symptom.** If the ledger says two records share a sort
key, the fix is a total ordering — not a retry, not a sleep, not a try/except
around the assertion. When a symptom-level patch is genuinely the right call
(an upstream bug, a deadline), record it as a workaround with the real cause and
what would remove it.

## 5. Clean up the instrumentation

Every temporary probe carries the marker `BUGHUNT` so removal is provable:

```bash
grep -rn "BUGHUNT" . --exclude-dir=.git
```

The hunt is not finished while that search returns a hit outside the record.
Run the project's own checks afterwards — instrumentation removal has broken
working code before.

## 6. Close the record

The record ends with:

- **Cause** — one paragraph, in the project's vocabulary.
- **Fix** — what changed, and the check that pins it.
- **Falsified** — the surviving list, so nobody retries it.
- **Blast radius** — other call sites with the same shape, named or explicitly
  searched for and not found.
- **Left open** — anything unexplained. An empty section must say why.

Redact before saving: scrub tokens, keys, passwords, connection strings,
customer identifiers, and personal data out of every captured log line. A
diagnosis record is committed or pasted into an issue more often than anyone
plans for.

## Refusals

- Do not fix a defect you never reproduced. Report the non-reproduction instead.
- Do not apply a fix before a check fails for the defect's reason.
- Do not generate a fourth hypothesis in a layer that produced three falsified
  ones. Widen.
- Do not delete or rewrite a falsified hypothesis to make the record read better.
- Do not leave a `BUGHUNT` probe behind.
- Do not weaken, skip, or retry-wrap a test to make a failure disappear.

## Integration

**Pairs with:** `code-review` when the fix needs review, `git-commit` to land the
fix together with its regression check, and `gen-session-handoff` when the hunt
outlives the session.

**Use instead of:** reading a diff for defects, which is `code-review`. This
skill starts from a broken behavior, not from a change.
