---
description: Diagnose a broken behavior with a written hypothesis ledger and a pinned regression check.
argument-hint: "[symptom or failing command]"
---

Use the **bug-hunt** skill to diagnose the defect.

Target:
- Use `$ARGUMENTS` as the symptom or failing command when it is non-empty.
- Otherwise use the failure already under discussion.

Reproduce before touching product code, and record the reproduction verbatim. Do
not fix a defect that never reproduced — report the non-reproduction instead.
Write every hypothesis with the observation that would falsify it, keep the
falsified ones, and widen the search after three failures in the same layer. Land
the fix only after a check fails for the defect's reason, then prove the
`BUGHUNT` probes are gone.
