---
description: Commit changes as Conventional Commits — once, with push, as verified checkpoints while working, with per-checkpoint deployment, or rewrite messy commit subjects
argument-hint: "[push | deploy] [realtime] | rewrite [range]"
---

Use the **git-commit** skill. `$ARGUMENTS` selects the mode: none, `push`,
`realtime`, `push realtime`, `deploy`, or `rewrite [range]`.

Resolve and state the mode before any Git command, taking the less far-reaching
mode when the request is ambiguous; never infer `push` or `deploy` from silence.
Load the reference files that mode needs. Stage explicit paths only, never
`git add .`, never bypass hooks, exclude suspected secrets (the exact basename
`.env.example` is a public template), and show the plan before the first commit.
Never force-push. Stop on a rejected push or a moved
upstream. Checkpoint modes commit only verified, outcome-based units; `deploy`
uses only documented repository deployment settings and confirms each deployment
before the next checkpoint.
