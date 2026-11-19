---
name: git-cleanup
description: Use when the user asks to clean up, prune, or delete local branches and finished worktrees that are already merged, including "clean up local branches", "merged 브랜치 정리", "이미 머지된 브랜치 삭제", "끝난 워크트리 정리해줘", "prune merged branches", "remove finished worktrees", "/git-cleanup", or "$git-cleanup". Removes clean, unlocked linked worktrees and deletes local branches whose tip is reachable from at least one protected branch (`main`, `master`, `dev`, `develop`, `development`, `stg`, `stage`, `staging`, `root`), never the protected list, the current branch, or the main or current worktree, after one confirmed plan. Uses `git worktree remove` without `--force` and `git branch -d` only, never `-D`. To merge a branch first use git-merge.
---

# Git Cleanup

Remove finished linked worktrees and delete local branches that are fully merged
into a protected branch. Local only; nothing remote is touched.

## Protected branches

`main`, `master`, `dev`, `develop`, `development`, `stg`, `stage`, `staging`, `root`

These and the current branch are never deleted, whatever their merge status.

## 1. Inventory

```bash
git fetch --prune 2>/dev/null || true      # informational; fine when offline
current=$(git branch --show-current)
[ -n "$current" ] || { echo "Detached HEAD; check out a branch first." >&2; exit 1; }
protected=(main master dev develop development stg stage staging root)
anchors=()
for p in "${protected[@]}"; do
  git rev-parse --verify -q "refs/heads/$p" >/dev/null && anchors+=("$p")
done
[ "${#anchors[@]}" -gt 0 ] || { echo "No protected branch exists locally; nothing to anchor against." >&2; exit 1; }
```

A tip is merged when `git merge-base --is-ancestor <tip> <anchor>` succeeds for
at least one anchor. Use this rather than `git branch --merged`, which checks only
against `HEAD`. Record which anchor proved each candidate.

## 2. Worktree candidates

Read every worktree from `git worktree list --porcelain`, never from typed paths.
The first entry is the main worktree; the current one is
`git rev-parse --show-toplevel`. A worktree is removable only when **all** hold:

1. it is not the main worktree;
2. it is not the current worktree;
3. it is not locked (no `locked` line);
4. `git -C <path> status --short` prints nothing (ignored files are allowed);
5. it has a branch (not a detached HEAD), that branch is not protected, and the
   branch tip is reachable from an anchor.

Every other worktree is kept with its reason: main, current, locked, uncommitted
or untracked changes, detached HEAD, protected branch, or branch not merged. A
`prunable` entry (its directory is already gone) is reported and left to
`git worktree prune`.

## 3. Branch candidates

A branch is a candidate when it is not protected, not the current branch, not
checked out in a kept worktree, and its tip is reachable from an anchor. A branch
whose worktree is a removal candidate is handled in the worktree pass.

## 4. Show one plan and confirm

```
Plan

Worktrees to remove (then delete their branch):
  ../repo-oauth   feature/oauth-login   (merged into main)
Worktrees kept:
  ../repo-wip     feature/wip           (uncommitted changes)
  ../repo-spike   (detached HEAD)

Branches to delete:
  bugfix/null-response   (merged into main)
  chore/update-deps      (merged into develop)
Kept:
  main, develop          (protected)
  feature/in-progress    (current branch)

Proceed? (y/N)
```

If there is nothing to remove or delete, say so and stop. Wait for explicit
confirmation; the default is no.

## 5. Worktree pass

For each confirmed worktree:

```bash
git worktree remove "$path"      # never --force
git worktree prune
git branch -d "$branch"
```

If Git refuses the removal (for example because of new changes or a submodule),
leave that worktree and its branch in place and report the refusal.

## 6. Branch pass

```bash
for branch in "${branch_candidates[@]}"; do
  git branch -d "$branch" || echo "refused $branch; left intact"
done
```

If `-d` refuses a branch thought to be merged, something is off (for example a
rewritten or cherry-picked history): report and skip it. Never escalate.

## 7. Summarize

Show `git worktree list` and `git branch`, the counts removed and deleted against
the counts planned, and every worktree or branch kept or refused with its reason.

## Never

- `git branch -D` or `git worktree remove --force`.
- Delete a protected branch or the current branch, or remove the main or current
  worktree.
- Remove a locked worktree or one with uncommitted or untracked changes.
- Delete remote branches (`git push origin --delete ...`); this skill is local.
- Treat an unmerged but stale branch or worktree as a candidate.
- Skip the confirmation.

Run only on the user's own request; never as a step of another skill.

**Reply:** each worktree removed and each branch deleted with the anchor that proved it merged, each worktree or branch kept or refused with its reason, and the remaining `git worktree list` and `git branch` output.
