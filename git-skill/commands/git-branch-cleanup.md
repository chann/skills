---
description: Delete local branches already merged into a protected branch (main/master/dev/develop/stage/staging/stg). Uses git branch -d only — never -D.
---

Use the **git-branch-cleanup** skill to delete local branches whose tip is reachable from at least one protected branch.

Protected (never deleted): `main`, `master`, `dev`, `develop`, `stage`, `staging`, `stg`. The current branch is also kept.

Follow the workflow in `git-skill/skills/git-branch-cleanup/SKILL.md` exactly:

1. **Inventory** local branches and find which protected names exist locally (anchors).
2. **Identify candidates** — every non-protected, non-current branch that is `git merge-base --is-ancestor` of at least one anchor. Record which anchor proved each candidate.
3. **Show the plan** with the proving anchor per candidate, plus what's being kept and why. Wait for explicit confirmation; default is "no".
4. **Delete** each candidate with `git branch -d` (safe). If git refuses, skip + report — never escalate to `-D`.
5. **Summary**: list remaining branches and how many were deleted vs skipped.

Never use `-D`, never delete protected branches, never delete the current branch, never delete remote branches (`git push origin --delete ...` is out of scope).
