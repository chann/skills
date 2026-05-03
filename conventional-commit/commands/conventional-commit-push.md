---
description: Split working-tree changes into Conventional Commits, then git push (never --force)
---

Use the **conventional-commit-push** skill to group the working-tree changes into Conventional Commits, create them, and push to the remote.

After every commit succeeds, run `git push` (or `git push -u origin "$(git branch --show-current)"` if no upstream is configured). Do NOT use `--force` or `--force-with-lease`. If the push is rejected, surface the error and stop without retrying.
