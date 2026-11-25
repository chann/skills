---
name: gcprd
description: Use only when the user explicitly invokes "/gcprd" or "$gcprd", the short alias for "/git-commit deploy" and "$git-commit deploy". Pushes verified checkpoints to the working branch while the work continues, then merges into main or master, verifies the merged tree, pushes it, and deploys and confirms that pushed commit through the repository's documented settings. Refuses when git-commit is not installed. For a request in natural language, such as "commit and push as you work, then merge to main and deploy" or "중간중간 커밋 푸시하고 끝나면 main에 머지해서 배포해줘", use git-commit directly.
disable-model-invocation: true
---

# GCPRD

A selector alias for `git-commit` with the mode fixed to `deploy`.

1. Before inspecting or changing any Git repository or starting a deployment,
   locate the installed `git-commit` skill and read its `SKILL.md` completely,
   together with every reference file its `deploy` mode loads.
   If the installed `deploy` mode still deploys each checkpoint instead of
   loading `references/merge-main.md`, stop and report that `git-commit`
   needs updating.
2. Run `git-commit` in mode `deploy`. Treat the rest of the user's text as the
   task description for that run. Mode words in that text never change the
   fixed mode or its default-branch target; say so when they try.
3. Follow `git-commit` exactly. This alias neither restates nor relaxes any of
   its rules.

If `git-commit` is not installed, stop before any Git command and report that
`git-commit` must also be installed. Do not rebuild its workflow from memory and
do not fall back to another alias.

**Reply:** what the `git-commit` reply contract requires for mode `deploy`, or the missing-dependency report.
