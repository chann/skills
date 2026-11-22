# Opening a PR

**You own the patch, its target branch, and the reviewer's first read.**

1. Confirm the user asked to open a PR. Confirm the repository, head, and
   base. Use the repository's integration
   branch for standalone work and the prerequisite PR's branch for a stack.
   Use an isolated worktree for new edits when needed. Inspect the diff
   against that base and keep unrelated work out of the PR.
2. Use steps 1 and 2 of [shipping](shipping.md) to verify and commit. Check
   the final diff and run the repository's checks on the committed head
   before pushing the task branch. Confirm that the remote head matches the
   verified commit before opening the PR. Honor any narrower publishing
   limits in the request. Preserve published history and stop if Git
   rejects a normal push.
3. Write the title as `type(scope): subject` and keep the body under 40 lines.
   Use the second-level headings Why, What changed, Scope, Tradeoffs,
   Blast Radius, and Verification in that order, omitting any that do not
   apply. Include the commands and results and link the prerequisite PR
   for a stack.
4. Use the host's PR tool first, or `gh` if the repository is on GitHub and
   the CLI resolves it. Check for an open PR for the same head and base and
   return its link if it exists. With authorization to open a PR, use the
   confirmed head and base and open it ready for review unless the user asked
   for a draft. If no available tool can open it, keep the title and body in
   the reply.
5. Read the created PR back to confirm its URL, head, base, and draft status.
   Link it through the host when supported. Monitoring, external comments,
   approval actions, and merging each need authorization for that action.

**Reply:** the PR URL and head and base, what was verified, and any publishing step that remains pending.
