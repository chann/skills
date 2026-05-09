---
name: git-merge-to-main
description: Use when the user asks to merge the current branch into `main` and delete the merged source branch. Trigger on phrases like "merge to main", "main에 머지", "main 브랜치에 합쳐줘", "merge this branch into main and delete it", "/git-merge-to-main". Switches to `main`, merges the source branch, then runs `git branch -d` on the source. Refuses to force-delete or to operate on a dirty working tree. For `dev` use `git-merge-to-dev`; to bulk-clean already-merged branches use `git-branch-cleanup`.
---

# Git Merge to Main

## Overview

Merge the **current branch** into `main`, then delete the source branch locally because it's now fully merged. Safe by design — never `--force`, never `-D` (only `-d`), never auto-resolves conflicts, never auto-pushes.

**Announce at start:** "I'm using the git-merge-to-main skill to merge `<source-branch>` into main and delete it."

## Preconditions

Run these checks before touching anything. Fail closed on any violation — report and stop.

| # | Check | Command | On fail |
|---|---|---|---|
| 1 | In a git repo | `git rev-parse --is-inside-work-tree` | Abort: "Not a git repository." |
| 2 | HEAD attached (not detached) | `git symbolic-ref -q HEAD` | Abort: "Detached HEAD; checkout a branch first." |
| 3 | Current branch is not `main` | `[ "$(git branch --show-current)" != "main" ]` | Abort: "Already on main; nothing to merge." |
| 4 | Working tree clean | `[ -z "$(git status --porcelain)" ]` | Abort: "Working tree has uncommitted changes; commit/stash first." |
| 5 | `main` branch exists locally | `git rev-parse --verify main` | Abort: "main branch not found locally; create it or use git-merge-to-dev." |

## Workflow

### Step 1: Capture state

```bash
src=$(git branch --show-current)
echo "Source branch: $src"
git log --oneline "main..$src" | head -20      # what will be merged
```

If `main..$src` is empty → tell the user "`$src` has no new commits beyond main; nothing to merge" and stop.

### Step 2: Show the plan and confirm

```
Plan:
  1. git checkout main
  2. git merge $src
  3. git branch -d $src     (safe delete; refuses if not fully merged)
  4. (you stay on main; push manually when ready)

N commits will be merged. Proceed? (y/N)
```

Wait for explicit confirmation. Default is **no**.

### Step 3: Optional — fetch and check divergence (informational only)

```bash
git fetch origin main 2>/dev/null || true
behind=$(git rev-list --count HEAD..origin/main 2>/dev/null || echo 0)
if [ "$behind" -gt 0 ]; then
  echo "Heads up: local main is $behind commits behind origin/main."
  echo "After merge, you'll want to: git pull --rebase (or reconcile manually) before pushing."
fi
```

Don't auto-pull. The user controls when to sync.

### Step 4: Switch to main and merge

```bash
git checkout main
git merge "$src"
```

Use plain `git merge` — fast-forward if possible, otherwise create a merge commit. Do **not** use `--no-ff` unless the user asks. Do **not** use `--ff-only` (it would error on diverged history; let merge handle it).

If merge produces conflicts:

1. **Stop.** Don't try to auto-resolve.
2. Report the conflicting paths.
3. Tell the user to resolve and either `git commit` (to finish the merge) or `git merge --abort` (to roll back).
4. Do **not** delete the source branch.

### Step 5: Delete the source branch

After the merge succeeds and the working tree is clean:

```bash
git branch -d "$src"
```

Use `-d` (lowercase). Git will refuse if the branch isn't fully merged — that's the safety net. **Never** use `-D` (force) here. If `-d` refuses:

- Most likely cause: the merge didn't actually include all of `$src`'s commits (e.g. the user picked `--ff-only` and it became a no-op, or a hook rewrote the merge). Report and stop; do not escalate to `-D`.

### Step 6: Summary

```bash
git log --oneline -5
git branch --show-current
echo "Merged $src into main and deleted $src locally. Push when ready: git push"
```

If a remote-tracking branch `origin/$src` exists, mention it but do **not** auto-delete:

```
Note: origin/$src still exists. Delete the remote branch with:
  git push origin --delete $src
```

## Worked Example

```
User: 이 브랜치를 main에 머지해줘

Step 1:
  src = feature/oauth-login
  git log --oneline main..feature/oauth-login →
    a1b2c3d feat(auth): add OAuth login flow
    e4f5g6h test(auth): add OAuth login tests

Step 2 (plan):
  → checkout main, merge feature/oauth-login, delete feature/oauth-login
  User confirms.

Step 3 (divergence): origin/main is 0 commits ahead. ✓

Step 4: git checkout main && git merge feature/oauth-login → fast-forward.

Step 5: git branch -d feature/oauth-login → "Deleted branch feature/oauth-login (was a1b2c3d)."

Step 6: Show git log -5; remind user to push.
```

## Red Flags

**Never:**
- `git branch -D` (force delete) — use `-d` and respect the safety check
- Auto-resolve merge conflicts — stop and let the user resolve
- Auto-push after the merge — the user pushes when ready
- Run `git pull` / `git pull --rebase` without explicit user consent
- Delete the remote branch (`git push origin --delete`) without explicit user consent
- Use `--force` anywhere
- Operate when the working tree is dirty

**Always:**
- Show the plan and wait for confirmation before merging
- Report conflicts and stop without auto-fixing
- Use `git branch -d` (safe) for source-branch deletion
- Run `git status --short` after the merge to verify the tree

## Common Mistakes

**Force-deleting when `-d` refuses**
- **Problem:** "branch was not fully merged" → reaching for `-D`
- **Fix:** Investigate why the merge was incomplete; never escalate to `-D` automatically

**Auto-pushing after merge**
- **Problem:** Surprises the user; may break collaborator workflows if main was behind
- **Fix:** Stop after the merge; tell the user to push manually

**Pulling main without permission**
- **Problem:** `git pull` may rebase or merge unexpected commits
- **Fix:** Only `git fetch origin main` (informational); leave reconciliation to the user

## Integration

**Pairs with:**
- `git-commit` / `git-commit-push` — commit working-tree changes first, then merge
- `git-branch-cleanup` — bulk-delete other branches that are already merged into main
- `git-merge-to-dev` — same pattern, target = `dev` (or `develop`)

**Called by:** Manual user invocation only. Never auto-run during another skill's workflow.
