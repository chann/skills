---
description: Generate or update README.md, README.ko.md, ARCHITECTURE.md, and USAGE.md for a software project.
argument-hint: "[project-root]"
---

Use the **gen-docs** skill to generate or update the project documentation set.

Target root:
- If `$ARGUMENTS` is non-empty, use it as the project root.
- Otherwise use the current working directory.

The documentation set is:
- `README.md`
- `README.ko.md`
- `ARCHITECTURE.md`
- `USAGE.md`

Before writing, the skill must show per-file diffs and get confirmation. It must never write outside those four target files.
