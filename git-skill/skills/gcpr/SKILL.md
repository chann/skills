---
name: gcpr
description: Use only when the user explicitly invokes "/gcpr" or "$gcpr", the short alias for "/git-commit push realtime" and "$git-commit push realtime". Runs the installed git-commit skill with its mode fixed to push realtime and passes the rest of the request through; refuses when git-commit is not installed. For a request in natural language, such as "commit and push as you work" or "작업 중간중간 커밋 푸시해줘", use git-commit directly.
disable-model-invocation: true
---

# GCPR

A selector alias for `git-commit` with the mode fixed to `push realtime`.

1. Before inspecting or changing any Git repository, locate
   the installed `git-commit` skill and read its `SKILL.md` completely, together
   with every reference file its `push realtime` mode loads.
   Check that the installed version ships `scripts/push-checkpoint.sh`. If it
   does not, report that `git-commit` needs updating before you start.
2. Run `git-commit` in mode `push realtime`. Treat the rest of the user's text as the
   task description for that run. Mode words in that text never move the run to
   a farther-reaching mode; say so and name the selector that would.
3. Follow `git-commit` exactly. This alias neither restates nor relaxes any of
   its rules.

If `git-commit` is not installed, stop before any Git command and report that
`git-commit` must also be installed. Do not rebuild its workflow from memory and
do not fall back to another alias.

**Reply:** what the `git-commit` reply contract requires for mode `push realtime`, or the missing-dependency report.
