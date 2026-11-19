# Autonomous run

**You own the exit condition. Define done, then drive to it without stopping.**

Starts on "자러 간다", "멈추지 마", "don't stop", "run until done", or any
request that the work continue unattended.

1. Before the first round, write the exit condition as a predicate a command
   can check, such as "the suite is green and the reproduction passes" or "p95
   under 200 ms across 20 runs". For a multi-milestone build, run `long-task`
   when installed; it owns milestones and resumption.
2. Open the decision trail (`references/decision-trail.md`) and log the
   predicate as its first row.
3. Each round, make the smallest change the evidence justifies and check it
   against the predicate. Commit it if it advanced; discard it if it did not.
   Log the round either way.
4. A plateau is not a stop. Change approach: reread the source, test the
   premise, combine near-misses, try the bolder variant.
5. Fix what blocks the goal yourself (a flaky check, a broken script, a missing
   fixture) in its own commit, then return to the predicate.
6. Ask nothing. Make every reversible choice and log it. An irreversible
   action is skipped, logged as `blocked`, and the run continues on everything
   that does not need it.
7. Stop only when the predicate passes or a dead end is proven. Never loosen
   the predicate to declare victory.

**Reply:** the predicate and its final state, rounds run, what landed and what was discarded, the decision-trail path, and anything left blocked on an irreversible action.
