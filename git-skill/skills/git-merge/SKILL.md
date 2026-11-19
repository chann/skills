---
name: git-merge
description: Use when the user asks to merge the current branch into main, dev, or another local branch and delete the merged source branch unless it is protected, including "merge to main", "main에 머지해줘", "merge this into dev", "dev에 머지해줘", "develop에 합쳐줘", "merge this branch into release and delete it", "/git-merge", or "$git-merge". Takes an optional target (main, dev, or a local branch name; dev falls back to develop; no argument means the repository default branch), shows a plan, waits for confirmation, merges without pushing, and deletes the source with git branch -d only. Refuses a dirty working tree and never force-deletes. To bulk-clean branches and worktrees that are already merged use git-cleanup; for a merge that stopped on conflicts use git-resolve-conflicts.
---

# Git Merge

Merge the current branch into a target branch, then delete the source branch
locally with `git branch -d` unless it is protected. Never `--force`, never
`git branch -D`, never auto-resolve conflicts, never push.

## Protected source branches

`main`, `master`, `dev`, `develop`, `development`, `stg`, `stage`, `staging`, `root`

A protected source branch is still merged after confirmation, but the local
delete is skipped: never run `git branch -d "$src"` for it and never suggest
deleting its remote branch.

## 1. Resolve the target

The argument wins:

| Argument | Target |
|---|---|
| `main` | `main` |
| `dev` | `dev` if it exists locally, otherwise `develop` |
| any other name | that local branch |
| none | the repository default branch from `origin/HEAD`, otherwise `main` |

```bash
case "$arg" in
  dev)
    if git rev-parse --verify -q refs/heads/dev >/dev/null; then target=dev
    elif git rev-parse --verify -q refs/heads/develop >/dev/null; then target=develop
    else echo "No dev or develop branch found locally." >&2; exit 1; fi ;;
  "")
    target=$(git symbolic-ref --quiet --short refs/remotes/origin/HEAD 2>/dev/null)
    target=${target#origin/}; target=${target:-main} ;;
  *) target=$arg ;;
esac
```

The resolved target must exist as a local branch. If it does not, name what was
looked for (both `dev` and `develop` for `dev`) and stop. Never create a branch to
satisfy the request and never substitute another target such as `main`. Say
which target was resolved, and from what, in the plan.

## 2. Preconditions

Fail closed: report and stop on any violation.

| Check | Command | On failure |
|---|---|---|
| Inside a Git repository | `git rev-parse --is-inside-work-tree` | "Not a git repository." |
| HEAD attached | `git symbolic-ref -q HEAD` | "Detached HEAD; check out a branch first." |
| Current branch is not the target | `[ "$(git branch --show-current)" != "$target" ]` | "Already on `$target`; nothing to merge." |
| Working tree clean | `[ -z "$(git status --porcelain)" ]` | Name the uncommitted paths and ask the user to commit or stash them; do neither on their behalf |
| Target exists locally | `git rev-parse --verify -q "refs/heads/$target"` | See step 1 |

## 3. Capture the state and show the plan

```bash
src=$(git branch --show-current)
git log --oneline "$target..$src" | head -20
protected=(main master dev develop development stg stage staging root)
delete_src=1
case " ${protected[*]} " in *" $src "*) delete_src=0 ;; esac
```

If `$target..$src` is empty, report that `$src` has no new commits beyond
`$target` and stop.

```
Target: dev (argument "dev"; dev exists locally)
Plan:
  1. git checkout dev
  2. git merge feature/payments
  3. git branch -d feature/payments   (safe delete; refuses if not fully merged)
  4. you stay on dev; push manually when ready

3 commits will be merged. Proceed? (y/N)
```

For a protected source branch, step 3 reads
`skip the local delete for protected source branch <src>`. Wait for explicit
confirmation; the default is no.

## 4. Merge

```bash
git fetch origin "$target" 2>/dev/null || true
git rev-list --count "$target..origin/$target" 2>/dev/null   # informational only
git checkout "$target"
git merge "$src"
```

If the local target is behind `origin/$target`, warn that it should be
reconciled before pushing, but never pull or rebase without explicit consent.
Use a plain `git merge`: fast-forward when possible, a merge commit otherwise; no
`--no-ff` unless asked and no `--ff-only`.

When the merge stops on conflicts, stop. Report the conflicted paths, tell the
user to resolve them and `git commit`, or run `git merge --abort` themselves, and
do not delete the source branch. When `git-resolve-conflicts` is installed, name
it as the next request for finishing the merge.

## 5. Delete or keep the source

After a successful merge and a clean `git status --short`:

```bash
if [ "$delete_src" -eq 0 ]; then
  echo "Kept protected source branch $src."
else
  git branch -d "$src"
fi
```

If `git branch -d` refuses, the merge did not include all of `$src`: report it and
stop. Never escalate to `git branch -D`.

## 6. Summarize

Show `git log --oneline -5` and the current branch, and remind the user to push
the target when ready. If `origin/$src` exists and the source is not protected,
mention `git push origin --delete "$src"` as an option, but never run it without
explicit consent.

## Never

- `git branch -D`, `--force`, or a merge on a dirty working tree.
- Auto-resolve conflicts, auto-push, or run `git pull` / `git pull --rebase`
  without explicit consent.
- Delete a protected source branch, or delete any remote branch without explicit
  consent.
- Merge a branch into itself or into a target the user did not ask for.

Run only on the user's own request; never as a step of another skill.

**Reply:** the resolved target and how it was resolved, the source branch and the commits merged, whether the source was deleted or kept (and why), the merge result or the conflicted paths, and the reminder that nothing was pushed.
