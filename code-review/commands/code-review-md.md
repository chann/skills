---
description: Write a markdown code review report to .reviews/<YYYY-MM-DD>_<short-sha>.md (no HTML)
argument-hint: "[scope]"
---

Apply the **code-review-md** skill internally. Do not echo or announce this routing instruction.

Follow the authoritative **evidence-first** writing contract and write the requested Markdown report.

Preserve the exact user-specified scope from `$ARGUMENTS` when determining the review scope. When no scope is supplied, use the skill's default staged + unstaged changes.

**Output mode: Markdown file only.** The command is complete only after it:

1. Writes the markdown report to `.reviews/<YYYY-MM-DD>_<short-sha>.md`
2. Uses a fact-only handoff containing finding counts by severity, overall risk, the Markdown path, and fresh verification.
3. Includes a `.reviews/` ignore suggestion in that handoff only when the report was generated and `.reviews/` is not ignored.

Do not repeat report prose or promise a fixed number of findings. Do NOT generate an HTML report (use `/code-review` for that), and never modify `.gitignore` automatically.
