---
name: gcprm
description: Use only when the user explicitly invokes "/gcprm" or "$gcprm", the short alias for "/git-commit push realtime merge-main" and "$git-commit push realtime merge-main". Pushes verified checkpoints to the same-named remote feature branch, then merges into main, verifies the merged tree, and pushes main after the task finishes. Keeps the feature branch. For natural-language requests such as "commit and push as you work, then merge into main" or "중간중간 커밋 푸시하고 끝나면 main에 머지해줘", use git-commit directly.
disable-model-invocation: true
---

# GCPRM

A selector alias for `git-commit` with the mode fixed to `push realtime merge-main`.

1. Before any Git command, locate the installed `git-commit` skill and read
   its `SKILL.md` completely, along with every reference its
   `push realtime merge-main` mode loads.
2. Run `git-commit` in mode `push realtime merge-main`. Pass the rest of
   the user's text through as the task description. Keep the mode fixed
   regardless of any mode words in that text.
3. Follow every verification and safety rule in the canonical workflow.

If `git-commit` is not installed, stop before any Git command and report that
`git-commit` must also be installed. If the installed skill lacks
`push realtime merge-main`, stop and report that it needs to be updated.
Do not rebuild its workflow from memory or fall back to another alias.

**Reply:** what the `git-commit` reply contract requires for mode `push realtime merge-main`, or the dependency report.
