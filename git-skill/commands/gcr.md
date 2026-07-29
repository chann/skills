---
description: Alias for `/git-commit-realtime` — commit verified outcome checkpoints continuously while working, without pushing
---

Use the **git-commit-realtime** skill for the requested implementation.

Plan meaningful, outcome-based checkpoints before the first commit. Complete and
verify one coherent unit, stage only its explicit paths, create a Conventional
Commit, record its hash, and continue to the next unit while keeping every
checkpoint local.

Do not create time-based or knowingly broken checkpoint commits. Never use
`git add .`, bypass hooks, or push from this workflow; publication stays a
separate, explicit request such as `/git-commit-push` or `/gcpr`.
