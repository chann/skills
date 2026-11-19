# Feature

**You own the design and the behavior a user sees.**

1. Trace the subsystem the feature touches and name the data shape before any
   logic: the types, the state, the source of truth. A wrong shape is the
   expensive mistake; logic follows it.
2. Decide what fans out, one line each, writing `n/a` with a reason rather than
   dropping a line:
   - blocking first steps: what must land before anything runs in parallel;
   - independent workstreams: disjoint files or layers that can run at once;
   - shared mutable state: what two workers would both write, split before it
     is serialized;
   - smallest safe decomposition: one owner or several, and why.
3. With two or more workstreams, run the fan-out playbook (`swarm` when
   installed). Otherwise build it in the session.
4. Build it as a series of small units, each closed by its own check and
   committed once that check is green.
   Reuse what the codebase, the standard library, or an installed dependency
   already has. Finish every caller, test, fixture, and doc the change touches.
5. Verify on the real surface by driving the feature the way a user would, not
   only through its tests. The wrong surface or `INCONCLUSIVE` is not a pass.
6. When the design is contested, run the review playbook on the diff
   (`interrogate` when installed) before shipping.
7. Ship with the shipping playbook.

**Reply:** what the user can now do, the data shape and the choices that mattered with their alternatives, the fan-out decision, how it was verified on the real surface, and the open decisions.
