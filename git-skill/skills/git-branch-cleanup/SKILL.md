---
name: git-branch-cleanup
description: Use when the user asks to clean up, prune, or delete local branches that have already been merged. Trigger on phrases like "clean up local branches", "merged 브랜치 정리", "이미 머지된 브랜치 삭제", "prune merged branches", "/git-branch-cleanup". Deletes local branches whose tip is reachable from at least one protected branch (`main`, `master`, `dev`, `develop`, `development`, `stg`, `stage`, `staging`, `root`), excluding the protected list and the current branch. Uses `git branch -d` (safe delete) only — never `-D`.
---

# Git Branch Cleanup

## Overview

Find and delete local branches that have been fully merged into one of the protected branches, then are safe to remove. Protected names — `main`, `master`, `dev`, `develop`, `development`, `stg`, `stage`, `staging`, `root` — and the current branch are always kept.

**Announce at start:** "I'm using the git-branch-cleanup skill to delete local branches already merged into a protected branch."

## Protected Branches

The following branch names are **never** deleted, regardless of merge status:

`main`, `master`, `dev`, `develop`, `development`, `stg`, `stage`, `staging`, `root`

The **current branch** is also never deleted.

## Workflow

### Step 1: Inventory

```bash
git fetch --prune 2>/dev/null || true   # informational; keeps refs honest, don't error if offline

current=$(git branch --show-current)
[ -n "$current" ] || { echo "Detached HEAD; checkout a branch first." >&2; exit 1; }

protected=(main master dev develop development stg stage staging root)

# All local branch names
all=$(git for-each-ref --format='%(refname:short)' refs/heads/)
```

### Step 2: Find which protected branches actually exist locally

Only protected branches that exist locally can serve as merge anchors:

```bash
anchors=()
for p in "${protected[@]}"; do
  git rev-parse --verify "$p" >/dev/null 2>&1 && anchors+=("$p")
done

if [ "${#anchors[@]}" -eq 0 ]; then
  echo "No protected branches (main/master/dev/develop/development/stg/stage/staging/root) found locally; nothing to anchor against." >&2
  exit 1
fi
```

### Step 3: Identify candidates

A branch is a candidate when **all** of:

1. It is **not** in the protected list
2. It is **not** the current branch
3. Its tip is reachable from at least one anchor (i.e. fully merged into it)

```bash
candidates=()
for b in $all; do
  # skip protected
  case " ${protected[*]} " in *" $b "*) continue ;; esac
  # skip current
  [ "$b" = "$current" ] && continue
  # merged into any anchor?
  for a in "${anchors[@]}"; do
    if git merge-base --is-ancestor "$b" "$a"; then
      candidates+=("$b|$a")   # remember which anchor proved it
      break
    fi
  done
done
```

Each entry stores `branch|anchor` so the plan can show **why** each candidate is being deleted.

### Step 4: Show the plan and confirm

```
Plan: delete N merged local branches

  feature/oauth-login        (merged into main)
  bugfix/null-response       (merged into main)
  chore/update-deps          (merged into develop)

Kept (protected or current):
  main, develop, stage  ← protected
  feature/in-progress  ← current branch

Proceed? (y/N)
```

If `candidates` is empty → tell the user "Nothing to clean up; no merged non-protected branches found." and stop.

Wait for explicit confirmation. Default is **no**.

### Step 5: Delete with `-d` (safe)

```bash
for entry in "${candidates[@]}"; do
  branch="${entry%%|*}"
  if git branch -d "$branch"; then
    echo "✓ deleted $branch"
  else
    echo "✗ refused $branch — left intact (run \`git branch -d $branch\` manually if you're sure)"
  fi
done
```

**Never** use `-D` (force). If `-d` refuses for a candidate that we *thought* was merged, something is off — report and skip; don't escalate.

### Step 6: Summary

```bash
git branch                # show what remains
echo "Done. Deleted M of N candidates."
```

If any candidates were skipped, list them and explain that `-d` refused (likely the branch has commits not actually reachable from the anchor — e.g. a `--no-commit` cherry-pick or rewritten history).

## Worked Example

```
User: 머지된 브랜치 다 정리해줘

current = main
anchors found locally: main, develop

Local branches:
  main                       ← protected, kept
  develop                    ← protected, kept
  feature/oauth-login        → ancestor of main? yes → candidate
  bugfix/null-response       → ancestor of main? yes → candidate
  feature/wip-experiment     → ancestor of any anchor? no → kept (not yet merged)
  hotfix/typo                → ancestor of develop? yes → candidate

Plan: delete 3 (feature/oauth-login, bugfix/null-response, hotfix/typo)
User confirms.
→ git branch -d feature/oauth-login    ✓
→ git branch -d bugfix/null-response   ✓
→ git branch -d hotfix/typo            ✓
→ Show remaining branches: main, develop, feature/wip-experiment.
```

## Red Flags

**Never:**
- Use `git branch -D` (force delete) — only `-d` (safe delete) is allowed here
- Delete any branch in the protected list (`main`, `master`, `dev`, `develop`, `development`, `stg`, `stage`, `staging`, `root`)
- Delete the current branch
- Delete remote branches (`git push origin --delete ...`) — this skill is local-only
- Skip the confirmation prompt
- Treat unmerged-but-stale branches as candidates — only fully-merged branches qualify

**Always:**
- Show the plan with the proving anchor for each candidate (so the user can spot-check)
- Show what was kept and why
- Use `git merge-base --is-ancestor` to verify merge status (not `git branch --merged`, which only checks against HEAD)
- Default the confirmation to "no"

## Common Mistakes

**Using `git branch --merged` instead of `--is-ancestor`**
- **Problem:** `--merged` checks against the *current* branch only, not all protected anchors
- **Fix:** Loop through anchors with `git merge-base --is-ancestor` so a branch merged into `develop` (but not `main`) is still detected

**Force-deleting when `-d` refuses**
- **Problem:** Reaching for `-D` when the safety check correctly flags risk
- **Fix:** Skip the branch and report; let the user decide

**Including the current branch as a candidate**
- **Problem:** You can't delete the branch you're standing on; git will refuse anyway
- **Fix:** Filter the current branch out before building the candidate list

## Integration

**Pairs with:**
- `git-merge-to-main` / `git-merge-to-dev` — those skills delete a single source branch right after merging; this skill cleans up everything that's already merged

**Called by:** Manual user invocation only. Never auto-run during another skill's workflow.
