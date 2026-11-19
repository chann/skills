---
description: Remove finished worktrees and delete local branches already merged into a protected branch (main/master/dev/develop/development/stg/stage/staging/root). Never --force, never -D.
---

Use the **git-cleanup** skill to remove finished linked worktrees and delete local branches whose tip is reachable from at least one protected branch.

Protected (never deleted): `main`, `master`, `dev`, `develop`, `development`, `stg`, `stage`, `staging`, `root`. The current branch, the main worktree, and the current worktree are also kept.

1. **Inventory** — stop on a detached HEAD; find which protected branches exist locally (anchors).
2. **Worktrees** — from `git worktree list --porcelain`, a worktree is removable only when it is not the main or current worktree, not locked, `git status --short` is empty, and its non-protected branch tip is reachable from an anchor. Keep every other worktree and record why.
3. **Branches** — every non-protected, non-current branch not checked out in a kept worktree whose tip is `git merge-base --is-ancestor` of an anchor.
4. **Plan** — one plan for worktrees and branches, with the proving anchor and every kept item's reason. Wait for explicit confirmation; default is "no".
5. **Execute** — `git worktree remove <path>`, `git worktree prune`, `git branch -d <branch>`; then the branch pass with `git branch -d`. On any refusal: leave it and report.

Never use `--force` or `-D`, never delete protected or current branches, never remove the main or current worktree, never delete remote branches.
