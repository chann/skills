# Decision trail

The record a long or unattended run leaves for someone who was not watching.
A reviewer reads it top to bottom, follows the evidence pointers, and decides
whether to trust the result without replaying the session.

## The file

One append-only, tab-separated file with a header row. Every cell stays on one
line.

| Column | Holds |
|---|---|
| `ts` | ISO 8601 UTC timestamp |
| `phase` | the playbook step or workstream |
| `decision` | what was chosen or done, in one line |
| `why` | the reason in plain words; name a principle when one drove it |
| `evidence` | a pointer: a commit, a `file:line`, an artifact or log path, a command. Never a paragraph |
| `result` | `VERIFIED`, `NOT VERIFIED`, `INCONCLUSIVE`, `reverted`, `blocked`, or `open` |

```text
ts	phase	decision	why	evidence	result
2026-11-19T01:02:00Z	frame	exit when the suite is green and p95 < 200 ms over 20 runs	a predicate a command can check	scripts/bench.sh	open
2026-11-19T01:40:00Z	round 1	cached the tenant lookup per request	profile showed 61% of time in that query	commit 3f2a9c1, .perf/r1.txt	VERIFIED
2026-11-19T02:15:00Z	round 2	tried batching the audit writes and reverted it	the 3 ms gain sat inside the 9 ms spread	.perf/r2.txt	reverted
2026-11-19T02:40:00Z	round 3	supersedes 2026-11-19T01:40:00Z: the bench reused one tenant, so every lookup hit the cache	reran with 500 tenants	.perf/r1-multitenant.txt	INCONCLUSIVE
2026-11-19T03:05:00Z	ship	skipped the production deploy	irreversible, nobody awake to confirm	AGENTS.md:12	blocked
```

## What gets a row

- A fork: the option taken and the one rejected.
- A completed unit with its verification result.
- A pivot or revert, with what triggered it.
- A blocker, including an irreversible action skipped during an autonomous run.
- In a loop, one row per round, kept or discarded.

Skip the self-evident: opening a file, listing a directory, rerunning a command
whose result did not change a decision.

## Rules

- **Append-only.** A call that turned out wrong is corrected by
  adding a row whose `decision` starts with `supersedes <ts>:`, naming the row
  it replaces. Existing rows are not edited or deleted.
- **Plain cells.** Replace tabs and newlines inside a cell with spaces. Prefix a
  cell that starts with `=`, `+`, `-`, or `@` with `'` so a spreadsheet does
  not evaluate it.
- **Local by default.** Write it to `.decisions/<YYYY-MM-DD>-<slug>.tsv` at the
  repository root and keep it out of Git; when the project does not ignore that
  path, add it to `.git/info/exclude`. Commit the file only when the person
  reviewing the work could not judge the result without it.

Appending a row from a shell:

```bash
trail=.decisions/2026-11-19-checkout-latency.tsv
[ -s "$trail" ] || printf 'ts\tphase\tdecision\twhy\tevidence\tresult\n' > "$trail"
printf '%s\t%s\t%s\t%s\t%s\t%s\n' "$(date -u +%Y-%m-%dT%H:%M:%SZ)" \
  "round 3" "moved the PDF render off the request path" \
  "it blocks the response and nothing reads it inline" "commit 9b1e0d4" "VERIFIED" >> "$trail"
```

## Before handing back

Walk the rows against what actually happened in the session:

1. Each row corresponds to something that was really decided or done.
2. Every evidence pointer resolves and shows what its row claims.
3. Nothing that steered the result is missing: each branch point, change of
   direction, and dropped approach has a row.

Add the missing rows and supersede the wrong ones. The reply names the trail's
path.
