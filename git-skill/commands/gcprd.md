---
description: Alias for `/git-commit deploy` — push verified checkpoints, then merge into main, verify, push, and deploy using documented repository settings
argument-hint: "[task]"
---

Use the **git-commit** skill in mode `deploy` for the requested work; `$ARGUMENTS` is the task.

Read the installed `git-commit` skill and every reference its `deploy` mode loads
before any Git command. If `git-commit` is not installed, stop and report it.
The fixed mode never changes, and this alias never relaxes a `git-commit` rule.

Push each verified checkpoint to the working branch. After the task finishes,
merge into the default branch (`main` or `master`), verify the merged tree, push
it, then deploy that pushed commit once and confirm the deployment.
