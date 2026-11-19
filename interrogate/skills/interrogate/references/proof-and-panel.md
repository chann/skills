# Proof and panel

Load this before proving a finding at `ran` or running an adversary panel.

## Choosing how far to push

The ladder is `said` < `cited` < `traced` < `ran` < `reproduced`. Stop at the
first level that settles the finding's severity. A LOW naming issue needs
`cited`; a HIGH data-loss claim needs `traced` at least and `ran` when one
script can show it.

| Level | Good proof | Not proof |
|---|---|---|
| `cited` | `src/cache.py:42` where the changed line drops the lock | "the cache looks unsafe" |
| `traced` | 1. `save()` at `api.py:18` calls `write()` without the lock. 2. `write()` at `store.py:51` reads `count`, then sleeps on I/O. 3. A second request reaches `store.py:51` before step 2 stores. 4. Both store `count + 1`; one increment is lost. | "this could race" |
| `ran` | `python3 /tmp/cr-003/repro.py` with its printed `AssertionError` pasted verbatim | a script you wrote but did not run, or output you paraphrased |
| `reproduced` | steps in the running app and the wrong screen or response observed | a log line you expect to appear |

A `traced` walk names every step with a `file:line`. A gap in the walk ("and
then somehow") means the finding is still `cited`.

## Writing a repro script safely

1. Make a temporary directory outside the repository (`mktemp -d`).
2. Write the script there. Import the changed code from the repository path
   (for example `PYTHONPATH=<repo>` or a relative `require` of the built file),
   with bytecode and cache writes turned off where the runtime allows
   (`PYTHONDONTWRITEBYTECODE=1`).
3. Make it fail loudly when the defect is present: an assertion with the
   expected and actual values, and a non-zero exit.
4. Run it once, paste the exact command and the output it printed.
5. Check `git status --porcelain` matches the snapshot taken before the run.

Do not install packages into the repository, start services that write into
it, check out other revisions in place, or call any network endpoint. When a
proof would need any of these, stop at the level already reached and say what
the next level would need.

Running the project's existing tests counts as `ran` when a test fails for the
finding's reason. A test that passes is evidence against the finding: lower its
severity or drop it.

## Panel brief

Hand each adversary the same text, filled in:

> Try to make this change fail. Scope: `<git command>`. Intent: `<one
> sentence>`. A finding counts only with a run behind it: an existing test
> that fails, or a small repro script kept in a temporary directory outside
> the repository. Do not edit the repository, run destructive commands, or
> call the network. For each finding give a title, the `file:line`, the
> command exactly as you ran it, what it printed, and what the intent says it
> should have printed. Whatever you did not run stays out, including style,
> naming, and hazards that only a later change would trigger. Finding nothing
> is an acceptable answer.

## Verifying panel findings

- Rerun every returned command yourself under the safe-proof rules. Output that
  matches is `ran`; a command you cannot rerun safely is unverified.
- Keep a finding only when your rerun reproduces the failure and that failure
  contradicts the stated intent.
- Two findings share a root cause when one correction would fix both. Merge
  them, keep the strongest proof, and list every adversary that found it.
- Record unverified findings per adversary in the header, for example
  `**Dropped:** 4 (below cited: 1; panel model-a: 2 unverified, model-b: 1 unverified)`.
