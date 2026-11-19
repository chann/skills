---
name: blast-radius
description: Use when the user wants to know what a change could break outside its own diff before it ships, including "이거 바꾸면 뭐가 깨져?", "영향 범위 확인해줘", "이 변경 영향도 봐줘", "blast radius of this change", "what could this break", "is this small diff safe to merge", "/blast-radius", or "$blast-radius". Finds the one or two facts the change is safe because of, proves them as far as running real code in a temporary directory, and replies with the safety fact and its proof level, risks with `file:line`, what was cleared, and the cheapest check before merging. Read-only on the repository. Use interrogate for defects inside the diff itself.
---

# Blast radius

Find what a change breaks somewhere else, before it ships. Listing callers is
not the job; a symbol search does that in a second. The job is the breakage a
symbol search never shows.

A convincing writeup proves nothing: it reads the same whether or not it is
true. So the answer rests on one or two facts, and those facts are proven by
running code, not by argument.

## Proof ladder

Grade each safety fact, weakest first, and say where it stopped:

| Level | Means |
|---|---|
| `said` | Asserted. Worth nothing alone |
| `cited` | A real `file:line`, or the line in the pinned library's source |
| `traced` | The failure path walked step by step, and it does not reach |
| `ran` | A script or test that calls the shipped code and fails loudly if the fact is false |
| `reproduced` | Seen in the running product |

`ran` is usually one small script, in a temporary directory outside the
repository, that imports the same code the product ships and calls the exact
function in question.

## 1. Read the change

Resolve the scope the user named; otherwise the current branch against its
merge base with the default branch, plus uncommitted changes. Read the diff,
the commit messages, and the PR text. List the symbols it adds, changes, and
deletes. Then write down what it now does differently that the diff does not
spell out: a changed default, a reordered side effect, a new exception, a
different return shape, a removed guard.

## 2. Find the safety fact

Most changes that look risky are safe because of a single fact, such as "this
call only evicts entries that already expired" or "every writer of this column
goes through the function that changed". Name the one or two facts that, if
true, clear most of the risk at once. Spend the time there, not on a long list
of maybes.

## 3. Look where a symbol search stops

- **Pinned dependencies.** Read the library's own source at the version the
  lockfile pins, plus any local patch or vendored copy.
- **Timing and teardown.** When things run: event-loop ordering, callbacks,
  unmount and cleanup, shutdown hooks, retries, migrations before code.
- **Serialized shapes.** API payloads, database columns, cache entries, queue
  messages, files on disk, and another language or service reading the same
  bytes.
- **Switches.** Feature flags, environment config, and build-time defines that
  route around or into the change.
- **Distance.** Code several hops downstream that consumes the changed value
  without naming the changed symbol.

"Searched, found nothing" is a valid result; say what was searched. Never
invent a caller, a consumer, or an API.

## 4. Prove the facts

Push each safety fact as far down the ladder as is cheap, then stop and record
the level. For `ran`:

1. Make a temporary directory outside the repository.
2. Write a script there that imports the shipped code from the repository path
   and asserts the safety fact, failing with expected and actual values.
3. Run it, paste the exact command and its output.

The repository stays read-only: no edits, no checkout, no install into it, no
destructive command, no repository content sent to the network. Compare
`git status --porcelain` before and after; if it changed, report it. A fact
that needs any of those to prove stays at the level it reached and is called
`unproven` when that level is below `traced`.

## 5. Weigh the risks

For each risk give how it breaks, the `file:line`, a real likelihood, a real
cost, and how to check it. Keep confirmed risks; move what was checked and is
fine to the cleared list with the reason.

## Refusals

- Do not fix anything. Report; the user decides.
- Do not present a risk without a `file:line` or a named search that found it.
- Do not call a fact proven when its script was written but not run.

**Reply:** what the change does (including the non-obvious part); the safety fact with its proof level and pasted proof, or "unproven"; risks with how, `file:line`, likelihood, cost, and how to check; what was checked and cleared; and the cheapest check to run before merging.
