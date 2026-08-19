---
description: Finish a conflicted merge, rebase, cherry-pick, or revert without aborting it.
argument-hint: "[path or note]"
---

Use the **git-resolve-conflicts** skill to finish the operation in progress.

Focus:
- Use `$ARGUMENTS` to narrow attention to a path or to carry a note about intent
  when it is non-empty.
- Otherwise resolve every conflicted path.

Identify which operation stopped and its stated goal before editing anything, and
remember that a rebase swaps the ours/theirs labels. Classify every conflicted
path first: regenerate lockfiles and generated files rather than hand-merging
them, and check a submodule's own log before choosing its commit. Recover both
sides' intent from history before touching a hunk, keep both where they are
compatible, and record what was dropped where they were not. Never run `--abort`
or `--skip`, never invent behavior, and never push.
