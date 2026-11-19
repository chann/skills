---
description: Alias for `/git-commit push realtime` — commit and push verified outcome checkpoints continuously while working
argument-hint: "[task]"
---

Use the **git-commit** skill in mode `push realtime` for the requested work; `$ARGUMENTS` is the task.

Read the installed `git-commit` skill and every reference its `push realtime` mode loads
before any Git command. If `git-commit` is not installed, stop and report it.
The fixed mode never moves to a farther-reaching one, and this alias never
relaxes a `git-commit` rule.
