---
description: Merge the current branch into main, dev (fallback develop), another local branch, or the default branch, then safely delete the source unless it is protected. Never -D, never auto-push.
argument-hint: "[main | dev | <branch>]"
---

Use the **git-merge** skill to merge the current branch into the target named by
`$ARGUMENTS` and delete the source branch unless it is protected.

Resolve the target first: the argument wins; `dev` falls back to `develop`; with
no argument use the default branch from `origin/HEAD`, otherwise `main`. The
target must exist locally; never create or substitute one. State the resolved
target in the plan.

Protected source branches: `main`, `master`, `dev`, `develop`, `development`, `stg`, `stage`, `staging`, `root`. If `$src` is a protected source branch, still merge after confirmation but skip the local delete. Do not run `git branch -d "$src"` or suggest remote deletion for protected source branches.

Refuse a dirty working tree or detached HEAD. Show the plan and wait for explicit
confirmation (default no). Use a plain `git merge`; on conflicts stop and report
the paths. Delete a non-protected source only with `git branch -d`, never `-D`.
Never `--force`, never auto-resolve, never auto-pull, never auto-push, and never
delete a remote branch without explicit consent.
