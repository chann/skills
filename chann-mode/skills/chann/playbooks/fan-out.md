# Fan-out

**You own the done check and the merged result.**

1. Write done as a check that can fail before splitting anything: the command,
   the surface, the pass condition.
2. Split into slices whose write sets do not overlap. Two slices that must
   write one file are one slice, or the file goes to one of them and the other
   waits for it.
3. Run `swarm` when installed. Otherwise dispatch through the host's subagent
   tool under section 5 of `SKILL.md`: a worktree and branch per writer, a
   model tier per role.
4. Make each brief stand alone. Its first line points at `worker.md`, then the
   goal, the slice, its owned files, the bar, how to verify, and the report
   shape. Assume the delegate knows nothing else.
5. Collect each slice's verdict with its evidence. A missing report, a skipped
   check, or `INCONCLUSIVE` is a gap, not a pass: give that slice to a fresh
   delegate or do it yourself.
6. Merge every branch into yours, read the merged diff, and run the project's
   checks on the merged tree.
7. Remove each merged worktree and branch with the safe commands
   (`git-cleanup` when installed).

**Reply:** one report with the done check and its final state, each slice's verdict and evidence, the merged-tree check output, what was cleaned up, and any gap still open.
