---
description: Variant of /conventional-commit — split working-tree changes into Conventional Commits, then git push (never --force)
---

Use the conventional-commit skill to group the working-tree changes into Conventional Commits and create them.

After every commit succeeds, run `git push` (or `git push -u origin "$(git branch --show-current)"` if no upstream is configured). Do NOT use `--force` or `--force-with-lease`. If the push is rejected, surface the error and stop without retrying.
