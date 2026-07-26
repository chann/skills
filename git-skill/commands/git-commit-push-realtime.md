---
description: Commit and push verified outcome checkpoints continuously while working
---

Use the **git-commit-push-realtime** skill for the requested implementation.

Plan meaningful, outcome-based checkpoints before the first commit. Complete and
verify one coherent unit, stage only its explicit paths, create a Conventional
Commit, push it immediately, and prove `HEAD` matches its upstream before
starting the next unit.

Do not create time-based or knowingly broken checkpoint commits. Never use
`git add .`, bypass hooks, auto-reconcile a moved upstream, or force-push. If a
push is rejected, surface the error and stop.
