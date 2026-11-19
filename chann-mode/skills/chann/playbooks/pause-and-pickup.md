# Pause and pickup

**You own the resume point: a cold start continues without redoing anything.**

Pausing:

1. Land on a boundary a cold start can trust: complete the step in hand or
   undo it, begin nothing else, and stop any delegates still running.
2. Pausing changes nothing outside the checkout: no push, pull request, or
   deploy that was not already under way.
3. Put everything on disk. Uncommitted edits go into a single `wip:` commit on
   the task branch, and its body says so in one line when the tree is broken.
4. Write a resume note to disk (`handoff session` when installed): intent,
   progress, what is proven and what is not, the next steps in order, and the
   traps the next session would fall into. Point at an existing decision trail
   instead of copying it.

Picking up:

5. Find the prior trail (the resume note, the decision trail, the branch, a
   routed skill's record) and treat it as authoritative. Use `recall` or
   `catchup` when installed to rebuild what happened before this session.
6. Reconstruct the state (branch, worktree, what landed, what is pending) and
   name the resume point. Do not redo finished work.
7. Check each inherited claim the next step depends on against the real
   artifact. A prior "tests pass" is a lead until you run them.
8. Route the remaining work to its playbook.

**Reply:** for a pause, where it stopped, what is on disk, the commits made, and the first action on resume; for a pickup, where the prior work stopped, what was inherited versus redone, and the resume point.
