---
description: Write a markdown code review report to .reviews/<YYYY-MM-DD>_<short-sha>.md (no HTML)
---

Apply the **code-review-md** skill internally. Do not echo or announce this routing instruction.

Follow the authoritative **evidence-first** writing contract and write the requested Markdown report.

**Output mode: Markdown file**

After analyzing the diff, you MUST:
1. Write the markdown report to `.reviews/<YYYY-MM-DD>_<short-sha>.md`
2. Use a fact-only handoff containing finding counts by severity, overall risk, the Markdown path, and fresh verification.
3. Include a `.reviews/` ignore suggestion in that handoff only when the report was generated and `.reviews/` is not ignored.

Do not repeat report prose or promise a fixed number of findings. Do NOT generate an HTML report (use `/code-review-html` for that), and never modify `.gitignore` automatically.
