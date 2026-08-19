# Instrumentation playbook

A hypothesis you cannot observe is not ready to test. This file is how to get
the observation — cheaply, without changing the behavior you are measuring, and
without leaving anything behind.

Every temporary probe carries the marker `BUGHUNT` so `grep -rn "BUGHUNT" .`
proves removal.

## Pick the cheapest probe that answers the question

Work down this list and stop at the first one that can answer it.

| Probe | Answers | Cost |
|---|---|---|
| Read the code path | What is supposed to happen | free |
| Existing logs and error output | What already got recorded | free |
| A print or log line at the boundary | What value crossed it, and when | seconds |
| An assertion inside the suspect function | Whether an invariant holds | seconds |
| A debugger breakpoint | Full state at one moment | minutes |
| A bisect over commits or inputs | Which change or input introduced it | minutes |
| A tracer or profiler | Where time or allocation goes | minutes |

Reaching for a profiler before reading the failing line is the common mistake.
Reading for an hour instead of printing one value is the other one.

## Log the value, the identity, and the time

A probe that prints `"here"` wastes the round. Print what distinguishes this
call from the next one:

```
BUGHUNT rank/compare id=a3f ts=1723... left=a3f right=a3f equal=true
```

- **The value** the hypothesis is about, not a summary of it.
- **An identity** — request id, row id, iteration index — so lines from
  different calls can be told apart.
- **A monotonic timestamp** when ordering or duration is in question.

Print raw, not formatted. A formatter is another place a value can change on the
way to your eyes.

## Probe at the boundary, not in the middle

Put probes where data crosses a seam: function entry and exit, the network call,
the query, the cache read, the queue handoff. A value that is correct entering a
component and wrong leaving it localizes the defect to that component in one
round. Probes sprinkled through the middle produce a wall of output that
localizes nothing.

For a suspected wrong value, probe both sides of the seam in the same round —
that is one variable, not two.

## Per-ecosystem probes

**Python** — `print(f"BUGHUNT ...", file=sys.stderr, flush=True)`. Unflushed
stdout reorders against stderr and will lie to you about sequence. For import or
startup problems, `python -X importtime`. For allocation,
`tracemalloc.take_snapshot()`.

**JavaScript and TypeScript** — `console.error("BUGHUNT ...")` so the line
survives stdout redirection. For async ordering, log
`performance.now()` rather than `Date.now()`. For a value that changes
identity, log the object under `structuredClone` or a stable key — logging a
live object shows its state at expand time, not at log time, which has cost more
hours than any other single mistake in this list.

**Shell** — `set -x` for the whole script, `PS4='+BUGHUNT ${LINENO}: '` to mark
the lines. `set -o pipefail` before concluding anything about an exit code.

**Go** — `log.Printf("BUGHUNT ...")`. For concurrency hypotheses, run the
reproduction under `-race` before writing another hypothesis; the race detector
often answers the question outright.

**Rust** — `eprintln!("BUGHUNT ...")` or `dbg!`. Remember that `dbg!` moves its
argument unless you pass a reference.

## Intermittent failures

A 1-in-N failure needs a loop, not a rerun:

```bash
for i in $(seq 1 200); do <reproduction> || echo "BUGHUNT failed on run $i"; done
```

Record the observed rate before and after the fix. "It passed once" is not
evidence about a bug that fails one time in fifty.

Common causes, roughly in order of frequency: shared mutable state between
tests, real time or timezone dependence, unordered collection iteration,
unawaited async work, test execution order, and network or filesystem timing.
Each is a hypothesis with a cheap probe — pin the clock, seed the randomness,
sort the collection, await the promise, shuffle the test order.

## Bisection

Bisect when a hypothesis is "something changed" rather than "this is wrong":

- **Over commits** — `git bisect start <bad> <good>` with `git bisect run <cmd>`
  when the reproduction is scriptable. Record the first bad commit in the ledger
  as an observation, not as the cause; the commit tells you where, not why.
- **Over inputs** — halve the input until the failure disappears. This is
  minimization from the other direction and often faster on large fixtures.
- **Over configuration** — disable half the flags, plugins, or middleware.
  Especially effective when the defect appears only in one environment.

## Performance hypotheses

Measure before hypothesizing. A profiler on the reproduction tells you which
layer owns the time; only then is a hypothesis about that layer worth writing.

- Record a baseline number and the measurement command, so "faster" is checkable.
- Measure the same scope both times. A 40% improvement on a function that is 2%
  of the request is not a fix.
- Distinguish latency from throughput, and p50 from p99 — a p99 regression with a
  flat p50 is usually contention or a cache miss, not the algorithm.

## Removal

Before the hunt closes:

```bash
grep -rn "BUGHUNT" . --exclude-dir=.git
```

Then run the project's own checks. Removing instrumentation has broken working
code often enough that the check is not optional.
