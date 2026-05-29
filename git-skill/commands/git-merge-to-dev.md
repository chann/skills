---
description: Merge the current branch into dev (or develop), then safely delete the source branch unless it is protected. Never -D, never auto-push.
---

Use the **git-merge-to-dev** skill to merge the current branch into the dev branch and delete the source branch unless it is protected.

Protected source branches: `main`, `master`, `dev`, `develop`, `development`, `stg`, `stage`, `staging`, `root`. If `$src` is a protected source branch, still merge after confirmation but skip the local delete. Do not run `git branch -d "$src"` or suggest remote deletion for protected source branches.

Resolve the target first:

1. If `dev` exists locally → target = `dev`
2. Else if `develop` exists locally → target = `develop`
3. Else → abort with a clear message.

State the resolved target out loud, then follow the workflow in `git-skill/skills/git-merge-to-main/SKILL.md` exactly, substituting `$target` for `main` in every step (preconditions, checkout, merge, divergence check). Safety rules are identical: use `git branch -d` only for non-protected source branches (never `-D`), skip the local delete for a protected source branch, no auto-resolve on conflicts, no auto-push, no auto-pull.
