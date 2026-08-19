---
description: Hand this session to a fresh agent, separating proven state from unproven.
argument-hint: "[note about what the next session is for]"
---

Use the **gen-session-handoff** skill to compact this session into a resumable
document.

Focus:
- Use `$ARGUMENTS` as a note about what the next session is for when it is
  non-empty.
- Otherwise cover the work currently under way.

Name the command behind every proven claim, and put everything else under
unproven — "I implemented it" is not proof. Reference plans, specs, reviews, and
diffs by path instead of copying them in. Record the decisions with their reasons
and the approaches ruled out, give every next action a done-check, and end with a
copyable resume prompt. Redact secrets from quoted commands and logs. Do not
commit or push.
