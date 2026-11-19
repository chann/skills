# Plan

**You own the plan, not the code. The plan is the deliverable.**

1. For a one- or two-file change with an obvious approach, skip the plan: say
   so and switch to the playbook that does the work.
2. Settle every open question an experiment can settle by running it, under
   the prototype playbook. Bring the user only product or preference calls;
   when `review-me` is installed, use it for those, one decision at a time.
3. Write the plan to a file. Open with the goal, the done check, and the units
   in landing order with their dependency graph: which units start from the
   default branch and which wait for which.
4. Give each unit its own section: what it depends on, the files it may touch,
   the one change it makes, the result a user sees, and its verification (the
   command, the surface, the pass condition). A unit without verification is
   not ready.
5. Name what stays unproven, and order the unit with the riskiest unknown
   first.
6. When `plan-summary` is installed, use it to explain the plan file to the
   people who will review it.
7. Hand back the path and stop. Execution starts on the user's go.

**Reply:** the plan path, the units in order with their dependencies, what was settled by experiment, the decisions left for the user, and what stays unproven.
