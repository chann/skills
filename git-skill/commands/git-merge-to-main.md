---
description: Merge the current branch into main, then safely delete the source branch (git branch -d). Never -D, never auto-push.
---

Use the **git-merge-to-main** skill to merge the current branch into `main` and delete the source branch.

Follow the workflow in `git-skill/skills/git-merge-to-main/SKILL.md` exactly:

1. **Preconditions** — git repo, attached HEAD, current branch ≠ `main`, working tree clean, `main` exists locally. Fail closed.
2. **Show the plan** (`main..$src` log + delete step) and wait for explicit confirmation.
3. **(Optional) fetch + warn** if local `main` is behind `origin/main`. Don't auto-pull.
4. **Checkout `main` and `git merge "$src"`** — fast-forward when possible, regular merge otherwise. On conflict: stop and surface paths; do NOT auto-resolve.
5. **`git branch -d "$src"`** (safe; never `-D`). If git refuses, stop and report — do not escalate.
6. **Summary**: `git log --oneline -5`. Mention the user must `git push` manually; do NOT auto-push.

Never `--force`, never `-D`, never auto-resolve conflicts, never auto-push, never auto-delete the remote branch.
