---
description: Write a markdown + styled HTML code review report (severity badges, syntax highlighting, sidebar) to .reviews/
---

Use the **code-review-html** skill to review the requested changes and produce both markdown and HTML reports.

**Output mode: HTML + Markdown**

After analyzing the diff, you MUST:
1. Write the markdown report to `.reviews/<YYYY-MM-DD>_<short-sha>.md`
2. Run `python <skill-path>/scripts/generate_html_report.py` on the markdown
3. Open the resulting `.html` file
4. Present a brief summary in the conversation
