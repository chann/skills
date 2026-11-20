---
description: Strip narration comments and encode a real constraint in a type, test, or lint.
argument-hint: "[files or diff]"
---

Use the **no-comments** skill.

Scope:
- Use `$ARGUMENTS` when it is non-empty.
- Otherwise use the current diff against the default branch, including the working tree.

Run the reviewer prompt in `references/comment-review.md` through a general
subagent. On Claude Code that is a general-purpose subagent. On Codex that is
`spawn_agent`. When the host has no subagent tool, run the prompt inline. Do
not require a named specialist subagent type.

The reviewer does not edit application code. A rejected review does not abort
accepted findings. A comment about an outside rule that cannot be checked is
kept and marked for review.
