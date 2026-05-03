---
name: conventional-commit-push
description: Use when the user asks to commit working-tree changes AND push to the remote. Trigger on phrases like "commit and push", "커밋하고 푸시해줘", "/conventional-commit-push", "push my commits". Runs the conventional-commit workflow, then `git push` (never `--force`). For commit-only use `conventional-commit`; for history rewrite use `conventional-commit-rewrite`.
---

# Conventional Commit + Push

## Overview

Variant of the `conventional-commit` skill that runs the standard commit workflow, then pushes the resulting commits to the remote. Never uses `--force` or `--force-with-lease`.

**Announce at start:** "I'm using the conventional-commit-push skill to commit and push these changes."

## Workflow

**Before starting, Read the main `conventional-commit` SKILL.md** at `<plugin-root>/skills/conventional-commit/SKILL.md` — the full default workflow (steps 1–5), the secrets check, the commit-plan template, and the Red Flags list all live there. The variant relies on those sections.

Then follow `## Workflow: /conventional-commit` in the main SKILL.md exactly — steps 1–5 (inspect, group, plan, commit, summary). After every commit succeeds, push:

```bash
git push
```

If the current branch has no upstream:

```bash
git push -u origin "$(git branch --show-current)"
```

If the push is rejected (non-fast-forward), **stop and surface the error** — do not retry, do not auto-resolve, do not use `--force` or `--force-with-lease`. Tell the user to `git pull --rebase` (or equivalent) and re-push manually.

See the "Worked Example" under `## Workflow: /conventional-commit-push` in the main SKILL.md.

## Red Flags

Same Never/Always lists as the main `<plugin-root>/skills/conventional-commit/SKILL.md`. In particular:

- **Never** `git add .` or `git add -A` — always explicit paths.
- **Never** bypass hooks with `--no-verify`.
- **Never** `--force` push, and only `--force-with-lease` after explicit user consent.
- **Never** commit suspected secret files (`.env*`, `*_rsa`, `*.pem`, `*.key`, `*.p12`, `credentials.*`) without explicit override.

## Integration

**Pairs with:** `code-review` (or `code-review-md` / `code-review-html`) — run a review before committing.
**Called by:** Manual user invocation only. Never auto-run during another skill's workflow.
