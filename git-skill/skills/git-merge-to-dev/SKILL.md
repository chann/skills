---
name: git-merge-to-dev
description: Use when the user asks to merge the current branch into the dev branch (`dev`, falling back to `develop`) and delete the merged source branch unless the source is protected. Trigger on phrases like "merge to dev", "dev에 머지", "develop에 합쳐줘", "merge this into dev and delete it", "/git-merge-to-dev". For `main` use `git-merge-to-main`; to bulk-clean already-merged branches use `git-branch-cleanup`.
---

# Git Merge to Dev

## Overview

Variant of `git-merge-to-main` with target = `dev` (preferred) or `develop` (fallback). Merges the **current branch** into the dev branch, then safely deletes the source branch unless the source is protected.

**Announce at start:** "I'm using the git-merge-to-dev skill to merge `<source-branch>` into `<target>` and delete it unless it is protected."

## Target Branch Resolution

Resolve which branch to merge into, in order:

1. If `dev` exists locally → target = `dev`
2. Else if `develop` exists locally → target = `develop`
3. Else → abort: "No `dev` or `develop` branch found locally. Create one or use `git-merge-to-main`."

```bash
if git rev-parse --verify dev >/dev/null 2>&1; then
  target=dev
elif git rev-parse --verify develop >/dev/null 2>&1; then
  target=develop
else
  echo "No dev or develop branch found locally; aborting." >&2
  exit 1
fi
```

State the resolved target out loud before proceeding so the user can correct you.

## Workflow

**Before starting, Read the main `git-merge-to-main` SKILL.md** at `<plugin-root>/skills/git-merge-to-main/SKILL.md`. Follow that workflow exactly, **substituting the resolved `$target`** wherever it says `main`. The preconditions, plan/confirm step, protected source branch handling, conflict handling, safe-delete rule (`git branch -d`, never `-D`), and post-merge summary all apply identically.

Protected source branches are: `main`, `master`, `dev`, `develop`, `development`, `stg`, `stage`, `staging`, `root`. If `src` is a protected source branch, merge after confirmation but skip the local delete instead of running `git branch -d "$src"`.

Key substitutions:

| In `git-merge-to-main` | In this skill |
|---|---|
| Precondition 3: current branch ≠ `main` | current branch ≠ `$target` |
| Precondition 5: `main` exists locally | `$target` (`dev` or `develop`) exists locally |
| `git checkout main` | `git checkout "$target"` |
| `git merge "$src"` (into main) | `git merge "$src"` (into `$target`) |
| `git fetch origin main` (divergence check) | `git fetch origin "$target"` (divergence check) |

The merge-conflict rule, `-d`-not-`-D` rule, no-auto-push rule, and Red Flags list are identical.

When showing the plan, include the delete step only for non-protected source branches. For a protected source branch, show:

```
  3. skip the local delete for protected source branch $src
```

## Worked Example

```
User: dev에 머지해줘

Resolution: dev exists → target = dev
Source: feature/payments

Plan:
  1. git checkout dev
  2. git merge feature/payments
  3. git branch -d feature/payments

User confirms.
→ checkout dev, merge succeeds (fast-forward), delete branch.
→ Remind user to push dev when ready.
```

Protected source branch example:

```
User: staging을 dev에 머지해줘

Resolution: dev exists → target = dev
Source: staging (protected)

Plan:
  1. git checkout dev
  2. git merge staging
  3. skip the local delete for protected source branch staging

User confirms.
→ checkout dev, merge succeeds, keep staging locally.
→ Remind user to push dev when ready.
```

## Red Flags

Same Never/Always lists as `git-merge-to-main`. In particular:

- **Never** `-D` (force delete) — only `-d` (safe delete)
- **Never** delete a protected source branch (`main`, `master`, `dev`, `develop`, `development`, `stg`, `stage`, `staging`, `root`)
- **Never** auto-resolve merge conflicts
- **Never** auto-push or auto-pull the target branch
- **Always** state which target was resolved (`dev` vs `develop`) before merging
- **Always** show the plan and wait for confirmation
- **Always** identify protected source branches and skip the local delete

## Integration

**Pairs with:**
- `git-commit` / `git-commit-push` — commit working-tree changes first
- `git-merge-to-main` — same pattern, target = `main`
- `git-branch-cleanup` — bulk-delete other branches already merged into the dev branch

**Called by:** Manual user invocation only. Never auto-run during another skill's workflow.
