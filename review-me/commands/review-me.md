---
description: Review a plan, design, or decision one question at a time until every consequential leaf is resolved.
argument-hint: "[topic]"
---

Use the **review-me** skill for a leaf-complete decision-tree review.

Review target:
- Use `$ARGUMENTS` when it is non-empty.
- Otherwise use the plan, design, or decision already under discussion.

Keep the review read-only until the skill's closure audit is confirmed. Ask one
decision question at a time, give a recommended answer, and wait for the user's
answer before traversing the next node.
