---
description: Variant of /code-review — write markdown + a styled HTML report (syntax highlighting, diff views, severity badges) to .reviews/
---

Use the code-review skill to review the requested changes.

**Output mode: HTML + Markdown**

After analyzing the diff, you MUST:
1. Write the markdown report to `.reviews/<YYYY-MM-DD>_<short-sha>.md`
2. Run the HTML generation script to produce a `.html` file
3. Open the HTML file
4. Present a brief summary in the conversation
