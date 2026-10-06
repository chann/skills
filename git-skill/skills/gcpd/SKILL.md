---
name: gcpd
description: Use only when the user explicitly invokes "/gcpd" or "$gcpd" as the short alias for "/git-commit-push-deploy" or "$git-commit-push-deploy". Delegates to that canonical skill without restating or weakening it. For a request phrased in natural language, use git-commit-push-deploy directly.
disable-model-invocation: true
---

# GCPD

This skill is only a selector alias for `git-commit-push-deploy`.

Before inspecting or mutating any Git repository or initiating a deployment,
locate the installed `git-commit-push-deploy` skill, read its `SKILL.md`
completely, and follow it exactly, including every required shared workflow and
the repository's documented deployment settings.

If the canonical skill is unavailable, stop before any Git command or deployment
and report that `git-commit-push-deploy` must also be installed. Do not recreate,
summarize, or weaken the canonical workflow in this alias.
