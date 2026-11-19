---
description: Alias for `/git-commit deploy` — commit, push, deploy, and confirm verified outcome checkpoints using documented repository settings
argument-hint: "[task]"
---

Use the **git-commit** skill in mode `deploy` for the requested work; `$ARGUMENTS` is the task.

Read the installed `git-commit` skill and every reference its `deploy` mode loads
before any Git command. If `git-commit` is not installed, stop and report it.
The fixed mode never moves to a farther-reaching one, and this alias never
relaxes a `git-commit` rule.
