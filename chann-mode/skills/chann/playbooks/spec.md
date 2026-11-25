# Spec

**You own the statement of what gets built and how anyone will know it is done.**

1. Write your current read of the ask in one sentence, and list what it leaves
   open: who it is for, why now, what success looks like. Read the repository
   first; never ask what the code already answers.
2. Close the gaps one question at a time, each with your guess and the
   reasoning behind it attached, so the user corrects a guess instead of
   composing an answer. Use `review-me` when installed. Stop when you can
   predict the answers to the next three questions you would ask. When several
   rounds do not get there, say which foundational piece is missing.
3. When the ask is still a raw idea, widen before narrowing: name three to
   five distinct directions, one of them nobody asked for, then pick one
   against the user's stated goal and record why each other lost.
4. When one request bundles capabilities that could ship and be verified
   separately, split it before specifying: a table of modules with each one's
   responsibility and what it depends on, no cycles, and a build order. Each
   module gets its own spec.
5. Write the spec to a file: the objective, who uses it, success criteria as
   checks someone can run, boundaries (always, ask first, never), what is out
   of scope and why, and the open questions. A criterion nobody can check is
   rewritten or cut.
6. A change to shipped behavior gets a delta spec: the current behavior, the
   new behavior, and the check that tells them apart.
7. Return the spec's path and end the turn there. The plan playbook turns an
   approved spec into units; nothing is built until the user says go.

**Reply:** the spec path, the confirmed intent in the user's own words, the directions rejected and why, the decisions still open, and what stays unverified.
