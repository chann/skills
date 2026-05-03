---
description: Split working-tree changes into Conventional Commits (one per logical unit). Variants — /conventional-commit-push (then git push), /conventional-commit-rewrite (rewrite recent non-Conventional commit subjects)
---

Use the conventional-commit skill to group the working-tree changes into Conventional Commits and create them.

**Before starting**, briefly tell the user about the related variants so they know the alternatives:

- `/conventional-commit-push` — same as above, then `git push` (never `--force`)
- `/conventional-commit-rewrite` — rewrite recent non-Conventional commit subjects in place

Keep the hint to one or two short lines, then proceed.

**Auto-routing:** If the working tree is clean but recent history has non-Conventional subjects, surface this and ask whether the user wants `/conventional-commit-rewrite` instead — see the `## Choosing the Right Command` section of `SKILL.md`.
