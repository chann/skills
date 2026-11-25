# CI

**You own the gates every change passes before it lands.**

1. Read what runs today: the workflow files, the scripts they call, and the
   checks the protected branch requires. Reproduce the pipeline's commands
   locally before changing them.
2. Order the gates cheapest first so a failure shows early: format and lint,
   types, unit tests, build, integration, end-to-end, then security and
   dependency audits. Each gate is one command a developer runs locally
   unchanged.
3. Pin what the pipeline runs: third-party actions by commit hash, tool
   versions from the repository's own version files, installs from the
   lockfile. Give the token the least permission the job needs, and never
   expose secrets to code from a fork.
4. Never weaken a gate to get green. Allowing a step to fail, skipping a job,
   or lowering a threshold is the user's decision.
5. Make a failure actionable: the log shows the failing command and its
   output. Quarantine a flaky test with an owner and an issue instead of
   retrying it into silence.
6. Keep it fast: cache dependencies on the lockfile hash, run independent jobs
   in parallel, cancel superseded runs. Measure the duration before and after.
7. Prove it on a real run: push a branch and watch the run for that commit,
   including one deliberately failing change the gate must stop. A workflow
   that never ran is `INCONCLUSIVE`.
8. Ship with the shipping playbook.

**Reply:** the gates in order with their commands, what was pinned and which permissions were narrowed, the run that passed and the run that was correctly blocked, and the duration before and after.
