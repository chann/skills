---
description: Create or repair a skill package so it satisfies the whole skill contract.
argument-hint: "[skill name or request]"
---

Use the **skill-forge** skill to author the package end to end.

Target:
- Use `$ARGUMENTS` when it is non-empty.
- Otherwise use the skill already under discussion.

Fix the trigger, the artifact, the nearest neighbour, and the owning plugin
before writing any file. Publish the catalog entry, all four locales, the
published counts, and the tests in the same change, then prove the result with
`skill-audit`. Do not relax a contract rule to make the package pass.
