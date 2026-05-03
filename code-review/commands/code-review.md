---
description: Review code changes in the conversation. Variants — :md (write markdown to .reviews/), :markdown (alias of :md), :html (write markdown + styled HTML)
---

Use the code-review skill to review the requested changes.

**Output mode: Conversation only (no files written)**

Present findings inline. Do NOT write to `.reviews/` and do NOT generate HTML.

**Before starting the review**, briefly tell the user about the related variants so they know the alternatives:

- `/code-review:md` — write a markdown report to `.reviews/<YYYY-MM-DD>_<short-sha>.md`
- `/code-review:markdown` — alias of `:md`
- `/code-review:html` — write markdown + a styled HTML report to `.reviews/`

Keep this hint to one or two short lines, then proceed with the review.
