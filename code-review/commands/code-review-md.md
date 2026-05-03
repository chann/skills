---
description: Write a markdown code review report to .reviews/<YYYY-MM-DD>_<short-sha>.md (no HTML)
---

Use the **code-review-md** skill to review the requested changes and write a markdown report.

**Output mode: Markdown file**

After analyzing the diff, you MUST:
1. Write the markdown report to `.reviews/<YYYY-MM-DD>_<short-sha>.md`
2. Present a brief summary in the conversation (top 1–3 findings + path)

Do NOT generate an HTML report (use `/code-review-html` for that).
