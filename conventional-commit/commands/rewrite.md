---
description: Rewrite recent non-Conventional commit messages to follow the Conventional Commits spec
---

Use the conventional-commit skill in **rewrite mode**. Follow the rewrite workflow in `SKILL.md` exactly:

1. Determine the rewrite range — default: from upstream merge-base (or `main`/`master` merge-base) to HEAD
2. Run safety checks — refuse if the working tree is dirty, HEAD is detached, or any commit in the range already exists on a remote
3. Identify commits whose subject does not match the Conventional Commits regex; skip merges
4. Show the user an old → new mapping. Preserve each original body verbatim — rewrite only the subject line
5. After explicit confirmation, apply with `git filter-branch --msg-filter` using `scripts/rewrite_msg.py` and the mapping at `/tmp/cc-rewrite-map.tsv`
6. Show `git log --oneline <base>..HEAD` and tell the user how to discard the `refs/original/` backup once they're satisfied
