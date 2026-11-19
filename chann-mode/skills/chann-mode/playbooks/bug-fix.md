# Bug fix

**You own the root cause and the proof that it is gone.**

Every shipped line traces to runtime evidence. A change that "might help" is a
hypothesis, not a fix, and it does not ship.

1. Reproduce it yourself on the surface where it was reported: the page, the
   command, the API call, the failing test. If it will not fire, narrow the
   conditions, synthesize the trigger, or instrument until it does. Ask the
   user only after naming what you cannot reach and why. When `bug-hunt` is
   installed, run it from here; it owns the reproduction record, the
   hypothesis ledger, and the diagnosis file.
2. List the candidate causes and rule them out with runtime evidence: a log
   line, a probe, a bisect, a debugger. Each round, take the test that
   eliminates the most. When evidence refutes a hypothesis, revert every edit
   it motivated.
3. After two fixes on one premise fail, write the premise down and test it
   directly before a third.
4. Fix the first place the system went wrong, not where the symptom surfaced.
   A guard is a fix only when the state it handles is legitimate.
5. Write the check before the fix and watch it fail for the defect's reason.
   It lands before the fix in history. Skip the automated check only when it
   would cost more than the bug, and say so.
6. Verify on the surface from step 1: the original reproduction now passes. A
   unit test alone reaches `ran`, not `reproduced`.
7. Ship with the shipping playbook, at the reach the user asked for.

**Reply:** what was broken, the root cause with `file:line`, the fix, the failing-then-passing output pasted verbatim, and the hypotheses ruled out.
