---
name: gcr
description: Use only when the user explicitly invokes "/gcr" or "$gcr", the short alias for "/git-commit realtime" and "$git-commit realtime". Runs the installed git-commit skill with its mode fixed to realtime and passes the rest of the request through; refuses when git-commit is not installed. For a request in natural language, such as "commit as you work" or "작업 중간중간 커밋만 해줘", use git-commit directly.
disable-model-invocation: true
---

# GCR

A selector alias for `git-commit` with the mode fixed to `realtime`.

1. Before inspecting or changing any Git repository, locate
   the installed `git-commit` skill and read its `SKILL.md` completely, together
   with every reference file its `realtime` mode loads.
2. Run `git-commit` in mode `realtime`. Treat the rest of the user's text as the
   task description for that run. Mode words in that text never move the run to
   a farther-reaching mode; say so and name the selector that would.
3. Follow `git-commit` exactly. This alias neither restates nor relaxes any of
   its rules.

If `git-commit` is not installed, stop before any Git command and report that
`git-commit` must also be installed. Do not rebuild its workflow from memory and
do not fall back to another alias.

**Reply:** what the `git-commit` reply contract requires for mode `realtime`, or the missing-dependency report.
