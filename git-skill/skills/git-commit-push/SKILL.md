---
name: git-commit-push
description: Use when the user asks to commit working-tree changes AND push to the remote. Trigger on phrases like "commit and push", "커밋하고 푸시해줘", "/git-commit-push", "push my commits". Runs the git-commit workflow, then `git push` (never `--force`). For commit-only use `git-commit`; for history rewrite use `git-commit-rewrite`.
---

# Git Commit + Push

## Overview

Variant of the `git-commit` skill that runs the standard commit workflow, then pushes the resulting commits to the remote. Never uses `--force` or `--force-with-lease`.

**Announce at start:** "I'm using the git-commit-push skill to commit and push these changes."

## Workflow

**Before starting, Read the main `git-commit` SKILL.md** at `<plugin-root>/skills/git-commit/SKILL.md` — the full default workflow (steps 1–5), the secrets check, the commit-plan template, and the Red Flags list all live there. The variant relies on those sections.

Then follow `## Workflow: /git-commit` in the main SKILL.md exactly — steps 1–5 (inspect, group, plan, commit, summary). After every commit succeeds, push:

```bash
git push
```

If the current branch has no upstream:

```bash
git push -u origin "$(git branch --show-current)"
```

If the push is rejected (non-fast-forward), **stop and surface the error** — do not retry, do not auto-resolve, do not use `--force` or `--force-with-lease`. Tell the user to `git pull --rebase` (or equivalent) and re-push manually.

See the "Worked Example" under `## Workflow: /git-commit-push` in the main SKILL.md.

## Red Flags

Same Never/Always lists as the main `<plugin-root>/skills/git-commit/SKILL.md`. In particular:

- **Never** `git add .` or `git add -A` — always explicit paths.
- **Never** bypass hooks with `--no-verify`.
- **Never** `--force` push, and only `--force-with-lease` after explicit user consent.
- **Never** commit suspected secret files (`.env*`, `*_rsa`, `*.pem`, `*.key`, `*.p12`, `credentials.*`) without explicit override.

## Integration

**Pairs with:** `code-review` (or `code-review-md` / `code-review-html`) — run a review before committing.
**Called by:** Manual user invocation only. Never auto-run during another skill's workflow.
