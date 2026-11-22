---
description: Alias for `/git-commit push realtime merge-main` — push verified checkpoints, then merge into main, verify, and push main
argument-hint: "[task]"
---

Use the **git-commit** skill in mode `push realtime merge-main` for the requested work. Treat `$ARGUMENTS` as the task.

Read the installed `git-commit` skill and every reference this mode loads
before any Git command. If the skill is missing or lacks the mode, stop and
report the required installation or update. Keep the mode fixed and follow
every Git and verification rule in the canonical workflow.

Push each verified checkpoint to the same-named remote feature branch.
After the task finishes, merge into `main`, verify the merged tree, and push
`main`. Retain the feature branch.
