# Launch

**You own the decision to expose a change to users, and the way back.**

1. Write the rollback before the rollout: the trigger conditions as numbers,
   the steps, how long each takes, and what happens to data written in the
   meantime. A change with no way back needs the user's explicit go first.
2. Check readiness on the exact commit: the project's checks are green, no
   secret is in the tree, audit findings are triaged, a health check and
   error reporting exist, stored-data changes follow the migration playbook,
   and the docs and changelog match the release.
3. Separate deploy from release where the project has flags: deploy dark,
   confirm health, then enable. Every flag gets an owner and a removal date.
4. Stage the exposure: the team, then a small share of users, then wider. At
   each stage compare errors, latency, and the user metric that matters
   against a baseline measured beforehand, over a soak window stated in
   advance.
5. Advance, hold, or roll back by the thresholds from step 1, not by feel.
   Roll back at once on a data-integrity or security problem.
6. Take the deploy command, target, and confirmation method from the
   repository's own instructions, and deploy through the shipping playbook at
   the reach the user authorized.
7. After full exposure, confirm on the real surface, watch through the window,
   remove the flag and the dead path, and record what happened.

**Reply:** the rollback plan and its triggers, the readiness checks with their results, each stage with its numbers against the baseline, the decision taken at each, and what is still behind a flag.
