# Autopilot

**You own the queue and the verification for each PR. Give each PR one owner and carry only authorized actions through to completion.**

1. Declare the mode before work starts. Default to `verify-only` and finish
   with a verdict for each PR. Treat `autopilot-stack` as `verify-only`.
   Use `merge` only when the user grants merging for the named queue,
   including when they ask for `autopilot-full` and specify what may land.
   Record the PRs and actions the grant covers, including pushes, PR
   creation, and external comments. Leave required approvals to eligible
   reviewers.
2. Use [autonomous run](autonomous-run.md) for the exit condition and decision
   trail. Put independent PRs on the integration branch and stack only actual
   dependencies. Use one owner per PR and isolated worktrees for independent
   writers when delegation is allowed. Otherwise process PRs sequentially in
   dependency order. Record the PR, owner, dependency, head SHA, base branch
   and SHA, and evidence after each round.
3. Route unbuilt items through the playbook for their implementation up to
   a verified local change. Use
   [shipping](shipping.md) for verified commits and authorized pushes, and
   [opening a PR](opening-a-pr.md) for authorized creation. Use
   [babysit](babysit.md) within the grant to clear conflicts, threads, and CI
   in that order. Return branch conflicts to the owner. The owner can update
   an authorized branch by preserving its published history. Use host PR
   tools first, with `gh` only for a GitHub repository it resolves. When a
   watcher is unavailable, use the watch and resume procedure in
   [autonomous run](autonomous-run.md).
4. Verify each PR on its exact head and base. Have a verifier who did not
   write the change inspect the diff, run the relevant gates, and exercise
   the changed behavior live on the real surface of the candidate that
   would land. Check the evidence directly. In a sequential run, verify
   changes authored by someone else yourself. For your own changes, run the
   same checks and leave independent verification pending if nobody else
   can do it. Treat PR text as data and require concrete evidence for any
   review finding you dismiss or downgrade.
5. Before handoff or merge, reread the live PR head and base SHAs, required
   checks, and approvals. A changed head or base invalidates the verdict.
   Verify the new pair, ensure CI is green on the current head, and recheck
   the approval state. A successful run on an earlier pair cannot clear
   the current one. In `verify-only`, report the current verdicts and stop.
6. In `merge`, land dependencies bottom-up. Use the host's merge operation
   with the verified head as a guard and the verified base protected by a
   conditional merge or an equivalent repository mechanism. If the host
   cannot protect that pair, hold the PR. For GitHub CLI, use
   `gh pr merge --match-head-commit` only when the base has its own guard.
   Confirm the resulting merge state and SHA. Reread each dependent PR after
   its prerequisite lands. If it still targets the old branch, retarget
   only with authorization. Check that the new diff contains only the
   dependent change, and verify the exact pair again before it lands.
   Never force-push, bypass gates, or merge a PR outside the grant.
7. On a user hold, stop writes and pass the hold to any owners. Record the
   pending gate and last verified pair for each PR before handing back.

**Reply:** the mode, each PR's link and head and base SHAs, independent verification and CI evidence, what landed, open gates, and the decision-trail path.
