---
description: Write a markdown + styled HTML code review report (severity badges, syntax highlighting, sidebar) to .reviews/
---

Apply the **code-review-html** skill internally. Do not echo or announce this routing instruction.

Follow the authoritative **evidence-first** writing contract. Inherit the skill's bilingual Korean-primary and English-sibling report requirements.

**Output mode: HTML + Markdown**

After analyzing the diff, you MUST:
1. Write the markdown report to `.reviews/<YYYY-MM-DD>_<short-sha>.md`
2. Run `python <skill-path>/scripts/generate_html_report.py` on the markdown
3. Open the resulting `.html` file
4. Use a fact-only handoff containing finding counts by severity, overall risk, the Markdown and HTML paths, fresh verification, and the browser-open fact or warning.
5. Include a `.reviews/` ignore suggestion in that handoff only when reports were generated and `.reviews/` is not ignored.

Do not repeat report prose or promise a fixed number of findings. Never modify `.gitignore` automatically.
