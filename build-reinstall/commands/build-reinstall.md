---
description: Build the project, reinstall the new local result, and verify the installed copy.
argument-hint: "[project-root]"
---

Use the **build-reinstall** skill to build the project, reinstall the newly
built local result, and verify the installed copy.

Input:
- Use `$ARGUMENTS` as the project root when it is non-empty.
- Otherwise use the current project.

Follow the skill's discovery, displayed-plan, safety, and installed-artifact
verification requirements. Do not infer success from the build alone.
