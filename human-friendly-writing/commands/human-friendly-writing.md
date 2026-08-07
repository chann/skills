---
description: Rewrite AI-written Korean text into natural, human-sounding prose without changing its meaning.
argument-hint: "[text-or-file]"
---

Use the **human-friendly-writing** skill to rewrite AI-written Korean text into
natural, human-sounding prose.

Input:
- Use `$ARGUMENTS` when it is non-empty — inline Korean text or the path of a
  UTF-8 text file.
- Otherwise rewrite the Korean text already under discussion.

Keep facts, numbers, proper nouns, code identifiers, and established technical
terms exactly as they are. Never overwrite a source file; when the input was a
file, save the rewrite as a sibling file.
