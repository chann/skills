---
description: Merge the current branch into main, then safely delete the source branch unless it is protected. Never -D, never auto-push.
---

Use the **git-merge-to-main** skill to merge the current branch into `main` and delete the source branch unless it is protected.

Protected source branches: `main`, `master`, `dev`, `develop`, `development`, `stg`, `stage`, `staging`, `root`. If `$src` is a protected source branch, still merge after confirmation but skip the local delete. Do not run `git branch -d "$src"` or suggest remote deletion for protected source branches.

Follow the workflow in `git-skill/skills/git-merge-to-main/SKILL.md` exactly:

1. **Preconditions** — git repo, attached HEAD, current branch ≠ `main`, working tree clean, `main` exists locally. Fail closed.
2. **Show the plan** (`main..$src` log + delete step, or "skip the local delete" for a protected source branch) and wait for explicit confirmation.
3. **(Optional) fetch + warn** if local `main` is behind `origin/main`. Don't auto-pull.
4. **Checkout `main` and `git merge "$src"`** — fast-forward when possible, regular merge otherwise. On conflict: stop and surface paths; do NOT auto-resolve.
5. **Delete or keep source** — for a non-protected source branch run `git branch -d "$src"` (safe; never `-D`). For a protected source branch, skip the local delete.
6. **Summary**: `git log --oneline -5`. Mention the user must `git push` manually; do NOT auto-push.

Never `--force`, never `-D`, never auto-resolve conflicts, never auto-push, never auto-delete the remote branch, never delete a protected source branch.
