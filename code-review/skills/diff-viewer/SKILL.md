---
name: diff-viewer
description: Use when the user asks to render, inspect, open, or share the current git diff as a browser-readable HTML report, or explicitly invokes /diff-viewer, $diff-viewer, "diff viewer", "HTML diff", "split diff", or "unified diff".
---

# Diff Viewer

## Overview

Render the current working-tree diff as an HTML report. This is a viewer only: it does not perform a code review or produce findings.

## Workflow

1. Capture the current diff with the packaged script:

   ```bash
   python3 <skill-path>/scripts/generate_diff_report.py
   ```

2. The script writes `.diffs/<YYYY-MM-DD>_<working|clean|short-sha>.html` unless `-o` is provided.
3. Open the generated HTML file in the browser.
4. Report the file count, added/deleted line counts, and output path.
5. If the script prints `Suggestion: add .diffs/ to .gitignore`, pass that suggestion along. Do not edit `.gitignore` automatically.

## Options

```bash
python3 <skill-path>/scripts/generate_diff_report.py \
  --view unified \
  --theme auto \
  --code-theme auto \
  -o .diffs/my-diff.html
```

Valid `--view` values are `unified` and `split`. Valid page and code themes are `auto`, `light`, and `dark`. The browser controls can change these later and persist choices in `localStorage`.

## Boundaries

- Uses `git diff HEAD` so staged and unstaged changes are shown together.
- Produces HTML only, with no markdown report and no analysis.
- For actual review findings, use `code-review`, `code-review-md`, or `code-review-html`.
