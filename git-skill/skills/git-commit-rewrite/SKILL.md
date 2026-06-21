---
name: git-commit-rewrite
description: Use when the user asks to rewrite recent non-Conventional commit subjects, fix existing commit messages, or clean up commit history. Trigger on phrases like "rewrite commit history", "fix these commit messages", "커밋 메시지 다시 써줘", "/git-commit-rewrite", or whenever the user shows a non-Conventional `git log` and asks for help. For new commits use `git-commit`; for commit + push use `git-commit-push`.
---

# Git Commit Rewrite

## Overview

Rewrites non-Conformant commit subjects in recent history into Conventional Commits format. **Destructive** — changes commit SHAs. Refuses to silently rewrite already-pushed commits; instead presents a 3-option menu (Cancel / Force-push / Branch-based).

**Force mode:** if the invocation contains the token `force` or `--force`, that menu and every other interactive gate are skipped and the rewrite is force-pushed — see "Force mode" in the main `git-commit/SKILL.md`.

**Announce at start:** "I'm using the git-commit-rewrite skill to rewrite these commit messages."

## Workflow

**Before starting, Read the main `git-commit` SKILL.md** at `<plugin-root>/skills/git-commit/SKILL.md` — the safety check details, regex, "Mapping Common Non-Conformant Patterns" table, in-place / branch-based rewrite scripts, and post-rewrite cleanup commands all live there. The variant relies on those sections.

Then follow `## Workflow: /git-commit-rewrite` in the main SKILL.md exactly. Steps:

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

**Force mode (`force` keyword):** if the invocation contains the standalone token `force` or `--force` (case-insensitive), the user has pre-consented — skip the safety checks in step 2, skip the step 3 menu (auto in-place rewrite even if pushed), and in step 6 show the plan but do **not** wait. After applying, if any rewritten commit was already on the remote, finish with `git push --force` (bare — the only place it's allowed). Git's own `filter-branch` constraints still apply. Full rules: `## Workflow: /git-commit-rewrite` → "Force mode" in the main `git-commit/SKILL.md`.

The script lives at `<plugin-root>/skills/git-commit/scripts/rewrite_msg.py` (in the main skill — variants share it).

## Red Flags

Same Never/Always lists as the main `<plugin-root>/skills/git-commit/SKILL.md`. In particular:

- **Never** `--force` push — **except** in force mode (the `force` keyword), where bare `--force` is the user's opted-in choice; otherwise only `--force-with-lease` after explicit user consent.
- **Never** rewrite pushed commits without showing the 3-option menu first — **except** in force mode, where the keyword is the pre-consent.
- **Never** use `git filter-branch --root`.
- **Never** drop ticket references — move them to a `Refs:` footer.
- **Never** rewrite merge commits — use `--no-merges`.
- **Always** preserve the original commit body verbatim.

## Integration

**Pairs with:** `git-commit` — first commit working-tree changes, then rewrite stale history separately.
**Called by:** Manual user invocation only. Never auto-run during another skill's workflow.
