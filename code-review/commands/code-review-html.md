---
description: Write a markdown + styled HTML code review report (severity badges, syntax highlighting, sidebar) to .reviews/
---

Follow the code-review **evidence-first** writing contract and produce the requested Markdown and HTML reports.

**Output mode: HTML + Markdown**

After analyzing the diff, you MUST:
1. Write the markdown report to `.reviews/<YYYY-MM-DD>_<short-sha>.md`
2. Run `python <skill-path>/scripts/generate_html_report.py` on the markdown
3. Open the resulting `.html` file
4. Report only finding counts by severity, overall risk, the Markdown and HTML paths, fresh verification, and the browser-open fact in the conversation.

Do not repeat report prose or promise a fixed number of findings. Mention at most one urgent finding inline only when immediate action is necessary.
