---
description: Render the current working-tree git diff as a browser-readable HTML report with unified/split views and light/dark themes.
argument-hint: "[-o output.html] [--view unified|split] [--theme auto|light|dark] [--code-scheme github|ayu|one|flexoki|dracula|monokai|sublime|terminal]"
---

Use the **diff-viewer** skill to render the current working-tree diff as a browser-readable HTML report.

**Output mode: HTML only (no markdown report, no findings analysis).**

Run the packaged viewer script:

```bash
python3 "$CLAUDE_PLUGIN_ROOT/skills/diff-viewer/scripts/generate_diff_report.py" $ARGUMENTS
```

After the script writes the report:

1. Open the resulting `.html` file.
2. Print a one-line summary in the conversation: number of files changed, lines added/removed, and the report path.
3. If `.diffs/` is not in `.gitignore`, suggest adding it. Do not modify `.gitignore` automatically.

This command does NOT perform a code review. For analysis use `/code-review`, `/code-review-md`, or `/code-review-html`.
