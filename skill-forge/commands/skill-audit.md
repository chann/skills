---
description: Report every packaged skill that violates the skill contract.
argument-hint: "[skill name or repository path]"
---

Use the **skill-audit** skill to run the contract over the packaged skills.

Scope:
- Use `$ARGUMENTS` as a skill name or a repository root when it is non-empty.
- Otherwise audit the current repository.

Run `skill-forge/skills/skill-audit/scripts/audit_skills.py`, group the
violations by cause, and report the rule, skill, and file for each one. Keep the
run read-only unless the user asks for the repairs.
