---
description: Write a markdown code review report to .reviews/<YYYY-MM-DD>_<short-sha>.md (no HTML)
---

Follow the code-review **evidence-first** writing contract and write the requested Markdown report.

**Output mode: Markdown file**

After analyzing the diff, you MUST:
1. Write the markdown report to `.reviews/<YYYY-MM-DD>_<short-sha>.md`
2. Report only finding counts by severity, overall risk, the Markdown path, and fresh verification in the conversation.

Do not repeat report prose or promise a fixed number of findings. Mention at most one urgent finding inline only when immediate action is necessary. Do NOT generate an HTML report (use `/code-review-html` for that).
