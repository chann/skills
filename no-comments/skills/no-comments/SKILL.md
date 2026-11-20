---
name: no-comments
description: Use when the user wants comments that only narrate the code removed, including "주석 정리해줘", "의미 없는 주석 지워줘", "strip the comments", "delete narration comments", "clean up the comments in this diff", "/no-comments", or "$no-comments". Deletes narration, commented-out code, and workaround essays, keeps a comment about an outside rule that cannot be checked and marks it for review, and encodes a real constraint in a type, test, or lint when the user agrees. The review stays a report. For a read-only defect review use interrogate, and for prose outside the code use unslop.
---

# No Comments

Remove comments that only narrate the code. A comment that states a real
constraint is replaced by a type, a test, or a lint, and then deleted. The
reviewer reports. This skill applies the accepted part of that report.

The reviewer prompt is `references/comment-review.md`, next to this file.
Resolve it from this file's absolute path and pass that path. Do not paste a
shorter version.

## 1. Fix the scope before reading a comment

Use the files or the diff the user named. When they named neither, use the
current diff against the repository's default branch, including the working
tree. State the scope in one line before the review starts. A comment outside
that scope is not in this run.

## 2. Run the reviewer, then read the report

The reviewer does not edit application code. It returns deletions, `MUST CHANGE`
flags, and `REVIEW` keeps.

When the host can start a general subagent, give it the prompt file and the
scope, and nothing else. On Claude Code that is a general-purpose subagent. On
Codex that is `spawn_agent`. When the host has no subagent tool, run the same
prompt yourself in a fresh pass over the scope and say that you did. Do not
require a named specialist subagent type.

A comment about an outside rule that cannot be checked is kept and marked for
review. Do not delete it.

## 3. Accept findings one at a time

Read the report against the scoped diff. Reject a finding when any of these
is true:

- It edits application code, or it asks you to treat an edit as already done.
- It names a file or a comment outside the scope.
- It deletes a comment the prompt's keep list protects, including a `REVIEW`
  keep about an outside rule.
- Its `MUST CHANGE` reason is not true of the code today.

Rerun a rejected report once, with the rejected findings named. If the rerun
is rejected too, drop only those findings and leave them open. A rejected
review does not abort accepted findings. Apply the accepted ones.

Before accepting a thin `MUST CHANGE` or a thin keep on a comment that says
the code is important, trace the symbol or run `why` when that skill is
installed. If a deletion is still ambiguous, delete it. If a keep is refuted
or still ambiguous, delete it, except a `REVIEW` keep about an outside rule,
which stays until that rule is checked.

## 4. Apply the accepted deletions and the smallest fix

Delete the accepted comments. Do not rewrite a deleted comment into a shorter
one.

A trivial accepted flag is fixed in place: delete a dead path, drop an unused
parameter, or call the real API. A flag that needs a new shape gets the
smallest change inside the scope that removes the reason for the comment.
When the root cause is outside the scope, land the smallest in-scope fix and
report the rest open. Do not widen the fence, and do not add a guard whose
only job is to silence the comment.

## 5. Encode a constraint only with a yes

A comment that says not to remove it, not to change the wording, or to ask
someone before editing is a constraint, not a narration.

- When it is about something this code cannot change, and the report proved
  that, leave it.
- Otherwise offer the cheapest in-scope type, test, or lint that would make
  the comment unnecessary. Wait for a yes. An unattended run encodes one only
  when the caller already approved that encoding.
- On a yes, add the encoding, then delete the comment.
- On a no, delete the comment, report the constraint open, and sketch the
  encoding without applying it.

## 6. Report the edit

State the deletion count, the comments you restored and why, the `REVIEW`
keeps and the rule each claims, whether the review was rerun, the fixes, the
encodings that landed, and the constraints and flags left open.

## Refusals

- Do not treat a defect review as this skill. That is `interrogate`, and it
  does not edit.
- Do not rewrite prose that is not a code comment. That is `unslop`.
- Do not delete a `REVIEW` keep about an outside rule that was not checked.
- Do not let a rejected finding discard the accepted ones.
- Do not encode a constraint the user has not approved, unless they already
  approved it for an unattended run.

## Integration

**Pairs with:** `why` when a "do not remove" comment needs the record, and
`interrogate` when the user wants the diff judged before the comments go.

**Use instead of:** `interrogate` for a read-only defect review, and `unslop`
for sentences outside the code.
