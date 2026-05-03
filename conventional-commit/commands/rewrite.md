---
description: Rewrite recent non-Conventional commit messages to follow the Conventional Commits spec
---

Use the conventional-commit skill in **rewrite mode**. Follow the rewrite workflow in `SKILL.md` (`## Workflow: /conventional-commit:rewrite`) exactly:

1. **Determine the rewrite range** — default: from upstream merge-base (or `main`/`master` merge-base) to HEAD; or `HEAD~N` if the user specifies a count
2. **Run safety checks (A, B, C)** — working tree clean; HEAD attached; check whether any commit in range is on a remote
3. **If commits are pushed**, present the 3-option menu (Cancel / Force-push / Branch-based). DO NOT silently refuse. Default to Cancel.
4. **Identify non-conformant commits** via the Conventional Commits regex; skip merges with `--no-merges`
5. **Generate new messages** using the "Mapping Common Non-Conformant Patterns" table; move ticket prefixes (e.g., `proj #N:`) into a `Refs:` footer rather than dropping them; preserve each original body verbatim
6. **Show old → new plan** and wait for explicit confirmation
7. **Apply**:
   - Option 2 (in-place): `git filter-branch --msg-filter` using `scripts/rewrite_msg.py` and the mapping at `/tmp/cc-rewrite-map.tsv`, then `git push --force-with-lease` (never `--force`)
   - Option 3 (branch-based): create `${branch}-cc` off the base, cherry-pick + `--amend` each commit with the new message, push the new branch
8. **Post-rewrite**: show `git log --oneline <base>..HEAD`; tell the user how to discard the `refs/original/` backup; clean up `/tmp/cc-rewrite-map.tsv`
