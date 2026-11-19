---
description: Try to break a git diff and write proof-graded, severity-tagged findings to .reviews/ as Markdown plus a bilingual HTML report (or Markdown only with --md).
argument-hint: "[scope] [--md]"
---

Apply the **interrogate** skill internally. Do not echo or announce this routing instruction.

Follow the authoritative **evidence-first** writing contract. Every finding carries an `**Evidence:**` level (`cited`, `traced`, `ran`, `reproduced`) with its proof; a finding below `cited` is only counted under `**Dropped:**`. Report findings and never apply a fix. Proof commands stay read-only on the reviewed tree, never destructive, and never send repository content to the network.

Preserve the exact user-specified scope from `$ARGUMENTS` when determining the review scope. When no scope is supplied, use the skill's default staged + unstaged changes.

**Output mode.** Without `--md`, the command is complete only after it:

1. Writes the Korean report to `.reviews/<YYYY-MM-DD>_<short-sha>.md` and its bilingual `.en.md` sibling.
2. Runs `python <skill-path>/scripts/generate_html_report.py` on the markdown.
3. Opens the resulting `.html` file in a browser.

With `--md` (or "markdown only", "마크다운만"), it writes one Markdown report and generates no HTML and opens no browser.

Finish with a fact-only handoff: finding counts by severity, the dropped count, overall risk, artifact paths, proof commands run with a clean-tree check, fresh verification, panel status, and the browser-open fact or warning when HTML was generated. Include a `.reviews/` ignore suggestion only when reports were generated and `.reviews/` is not ignored.

Do not repeat report prose or promise a fixed number of findings. Never modify `.gitignore` automatically. Route explanations to `/diff-summary` and impact outside the diff to `/blast-radius`.
