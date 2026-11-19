# Perf

**You own the measurement story: baseline, limiter, remedy, proof.**

1. Measure a baseline before reading code for answers: the slow operation on a
   realistic workload, five runs or more, with the median and the spread
   written down. A number nobody measured is a `guess`.
2. Explain the number before trusting it. Name what bounds it (CPU, I/O, a
   lock, a query, the network, a serial loop) from a profile, trace, or
   counters taken during a run, and rule out that the run measured something
   else: errors, cache hits, skipped work, a cold start, noise. When `bug-hunt`
   is installed, work the limiter as its defect.
3. Pick the remedy from the cheapest end and stop at the first that meets the
   target: do not do it at all; do it once and reuse the result; do it less;
   do it later; do it concurrently; do it cheaper.
4. Change one thing per attempt. Measure it with the same harness and workload
   as the baseline, keep it only when the gain clears the spread, and revert
   it otherwise. Run the regression tests either way.
5. Report the final number against the baseline with the run count and the
   spread. A gain inside the spread is `INCONCLUSIVE`.
6. Ship with the shipping playbook. For a long climb against one metric, switch
   to the autonomous-run playbook with the target as its exit condition.

**Reply:** baseline and final numbers with run count and spread, the limiter and how it was found, each kept and reverted change, and the command that reproduces the numbers.
