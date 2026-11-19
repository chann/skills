# Shipping

**You own what lands and how far it reaches.**

1. Verify the unit first: the project's checks pass and the change works on its
   real surface. Commit only what passed.
2. Commit with `git-commit` when installed. Otherwise stage explicit paths,
   never everything at once, and write one Conventional Commit per verified
   unit.
3. Go only as far as the user asked: commit, push, or deploy. For pushing or
   deploying at each checkpoint, use `git-commit` with `push realtime` or
   `deploy` when installed.
4. Take the deployment command, target, branch, and confirmation method from
   the repository's own instructions. When they are missing or ambiguous, stop
   the deploy and say what is missing; never guess a provider or a target.
5. Confirm each deploy (the run status, a health check) before starting the
   next unit.
6. Never force-push. Merge with `git-merge` and resolve conflicts with
   `git-resolve-conflicts` when installed; otherwise merge without rewriting
   published history, and stop on a conflict that neither side's intent
   settles.
7. When the work is finished, remove this session's merged worktrees and
   branches (`git-cleanup` when installed) with `git worktree remove` without
   `--force` and `git branch -d`. When Git refuses, leave it and report it.
8. Rebuild and reinstall a local app or CLI only when the user asked, with
   `build-reinstall` when installed.

**Reply:** each commit with its verification, how far it reached (local, pushed, deployed) and how that was confirmed, and what was cleaned up or left behind with the reason.
