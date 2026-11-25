# Finish on the default branch

`push realtime merge-main` and `deploy` add this final step. At entry, record
the source branch and remote as in checkpoints.md, then resolve the default
branch on that remote: the branch `refs/remotes/<remote>/HEAD` points to when
it is `main` or `master`, otherwise whichever one of `refs/heads/main` and
`refs/heads/master` exists there. Stop before editing when neither exists, or when
both exist and the remote HEAD does not pick one. Every later `main` in this file means that resolved branch.
The invocation authorizes the source pushes, one final integration into it,
and publication of the tested commit.

When the source is the default branch itself, the checkpoint pushes already
publish it: skip steps 2, 3, and 5, run step 4's checks on the final pushed
tip, and report that no merge was needed.

1. Complete the task and its checks on the source. Publish each checkpoint
   as in checkpoints.md. Before touching main, confirm the remote source tip
   still equals the final reviewed source SHA. A clean, already published
   source may proceed directly to integration.
2. Find main's checkout with `git worktree list --porcelain`. Use it if clean.
   Otherwise, if main has no checkout, create a separate worktree for the local
   main branch. If only remote main exists, create local main at its fetched
   tip in that worktree. Stop for an existing dirty main checkout or unfinished
   Git operation. Keep the source checkout and branch intact.
3. In the main checkout fetch the intended remote main. Fast-forward a behind
   local main to that exact tip. Stop if local main contains unrelated unpublished
   commits. Inspect the incoming source range. Merge the **verified source SHA**
   with `git merge --ff --no-edit "$source_commit"`. On conflict preserve the
   merge state, report its paths, and stop before publishing main.
4. Record the resulting main SHA. Run the repository's required checks **on
   the merged tree**, even for a fast-forward. Require a clean main checkout,
   unchanged tested HEAD, and `git merge-base --is-ancestor "$source_commit" HEAD`.
   On failure report the already published source and local main state. Keep
   remote main unchanged. On a retry, reuse a previously recorded local merge
   only after checking its exact SHA, parents and remote base, then rerun checks.
5. From the main checkout run the same push helper with the original remote,
   branch `main`, and the tested main SHA. Report both remote refs and their
   verified SHAs. An already integrated source needs no empty commit. If the
   push is rejected by branch protection or a concurrent update, preserve the
   published source and report the rejection. Never force, disable protection,
   delete the source branch, or count a source-only push as a completed merge.
6. In `deploy`, continue with `references/deploy.md` steps 4–5 for the pushed
   default-branch SHA.
