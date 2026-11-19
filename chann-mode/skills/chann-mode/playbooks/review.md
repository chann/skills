# Review

**You own the findings and their proof. You change nothing.**

1. Fix the scope (the diff, branch, commit, or pull request) and the base it is
   read against. Read the whole change before judging any part.
2. Route by intent, each when installed: defects and risks to `interrogate`,
   what else the change can break to `blast-radius`, an explanation of the
   change to `diff-summary`, a plan document to `plan-summary`, the raw patch
   to `diff-viewer`. Otherwise read the diff together with its callers, tests,
   and configuration.
3. Give each finding its rung on the proof ladder and push it as high as it
   goes: a real `file:line`, the failing path walked, a command that shows it.
   A finding still at `said` is a question, not a finding.
4. Rank by what a user or operator would hit, not by taste.
5. Report; do not fix. A fix asked for afterwards is a new task under bug-fix
   or refactoring.
6. List what you checked and found clean, so silence reads as a result and not
   a gap.

**Reply:** findings ranked by severity with each one's rung and evidence, the areas checked and cleared, and what was out of scope.
