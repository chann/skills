---
name: conventional-commit-rewrite
description: Use when the user asks to rewrite recent non-Conventional commit subjects, fix existing commit messages, or clean up commit history. Trigger on phrases like "rewrite commit history", "fix these commit messages", "커밋 메시지 다시 써줘", "/conventional-commit-rewrite", or whenever the user shows a non-Conventional `git log` and asks for help. For new commits use `conventional-commit`; for commit + push use `conventional-commit-push`.
---

# Conventional Commit Rewrite

## Overview

Rewrites non-Conformant commit subjects in recent history into Conventional Commits format. **Destructive** — changes commit SHAs. Refuses to silently rewrite already-pushed commits; instead presents a 3-option menu (Cancel / Force-push / Branch-based).

**Announce at start:** "I'm using the conventional-commit-rewrite skill to rewrite these commit messages."

## Workflow

Follow `## Workflow: /conventional-commit-rewrite` in the main `conventional-commit` skill SKILL.md (`conventional-commit/skills/conventional-commit/SKILL.md`) exactly. Steps:

1. **Determine the rewrite range** — default base is the upstream merge-base (or `main` / `master` merge-base); or `HEAD~N` if the user specifies a count. Never use `--root`.
2. **Run safety checks A, B, C** — working tree clean; HEAD attached; check whether any commit in range is on a remote.
3. **If commits are pushed**, present the 3-option menu (Cancel / Force-push / Branch-based). Do NOT silently refuse. Default to Cancel.
4. **Identify non-conformant commits** via the Conventional Commits regex; skip merges with `--no-merges`.
5. **Generate new messages** using the "Mapping Common Non-Conformant Patterns" table; move ticket prefixes (e.g. `proj #N:`) to a `Refs:` footer; preserve each original body verbatim.
6. **Show old → new plan** and wait for explicit confirmation.
7. **Apply the rewrite**:
   - Option 2 (in-place): `git filter-branch --msg-filter` with `scripts/rewrite_msg.py` and the mapping at `/tmp/cc-rewrite-map.tsv`, then `git push --force-with-lease` (never `--force`).
   - Option 3 (branch-based): create `${branch}-cc` off the base, cherry-pick + `--amend` each commit with the new message, push the new branch.
8. **Post-rewrite**: show `git log --oneline <base>..HEAD`; tell the user how to drop the `refs/original/` backup; clean `/tmp/cc-rewrite-map.tsv`.

The script lives at `<plugin-root>/skills/conventional-commit/scripts/rewrite_msg.py` (in the main skill — variants share it).

## Red Flags

Same Never/Always lists as the main `conventional-commit/SKILL.md`. In particular:

- **Never** `--force` push (only `--force-with-lease` after explicit user consent).
- **Never** rewrite pushed commits without showing the 3-option menu first.
- **Never** use `git filter-branch --root`.
- **Never** drop ticket references — move them to a `Refs:` footer.
- **Never** rewrite merge commits — use `--no-merges`.
- **Always** preserve the original commit body verbatim.

## Integration

**Pairs with:** `conventional-commit` — first commit working-tree changes, then rewrite stale history separately.
**Called by:** Manual user invocation only. Never auto-run during another skill's workflow.
