# Hillclimb

**You own the metric, the experiment record, and the proof for every retained change.**

1. Recreate the user's problem with a realistic workload. Fix one primary
   metric, its direction, the target, and an attempt or time budget before
   editing. Use the user's limits when supplied and record any defaults. If
   the workload cannot reproduce the problem, report what the harness missed.
2. Freeze one repeatable project-owned measurement command. Pin the inputs,
   environment, and warm-up. Confirm the harness distinguishes contrasting
   workloads and reports errors and completed work. Record repeated baseline
   runs, their median and spread, a threshold for clearing noise, and a
   passing regression check. Resolve unstable measurements before comparing
   changes.
3. Keep a decision log outside tracked files. Record each hypothesis, change,
   before and after samples, delta, regression result, and verdict. Read the
   log before choosing the next experiment. Tie each hypothesis to a specific
   mechanism in the measured path.
4. Try one change at a time. Use the same harness against the current accepted
   state and the candidate, with comparable run conditions. If delegation is
   available and authorized, give independent attempts isolated checkouts
   and verify any accepted candidate again on the integrated tree. Otherwise
   run them in sequence.
5. Keep a change only when the regression gate passes and the gain clears the
   noise threshold, or when a concrete simplification holds the metric within
   the predefined tolerance. Treat ambiguous measurements as inconclusive.
   Revert rejected experiment changes while preserving unrelated work and log
   the result before starting the next attempt.
6. At a plateau, revisit the measured path and switch hypothesis categories
   when the budget permits. Stop at the target, at the budget limit, or when
   evidence leaves no worthwhile experiment. Repeat the baseline comparison
   and regression check on the final state. Report any target shortfall.

**Reply:** workload and measurement command, metric and target, baseline and final samples and delta, kept and reverted attempts, regression result, decision log path, and stop reason.
