# diff-viewer Skill Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add a `diff-viewer` sub-skill to the `code-review` plugin that renders the current working-tree `git diff` as a self-contained, browser-readable HTML report with unified/split views, independent page and codeblock light/dark themes, and syntax highlighting.

**Architecture:** A Python CLI (`generate_diff_report.py`) captures `git diff` (working tree + staged), parses the unified-diff stream into per-file structures, and emits a single HTML file built from `diff-template.html`. The HTML carries CSS variables for page theme + codeblock theme (independent, persisted via `localStorage`), a JS view toggle for unified/split, and highlight.js (CDN) with a span-aware line splitter that lets us tokenize each file's `before` / `after` content once and inject highlighted spans back into the diff table without breaking multi-line constructs.

**Tech Stack:** Python 3.10+ (stdlib only — `argparse`, `subprocess`, `re`, `html`, `pathlib`, `json`), vanilla JS + CSS, highlight.js 11.11 from CDN, pytest for unit tests.

---

## Scope Decisions (locked)

- **Plugin layout:** sub-skill inside the `code-review` plugin (`code-review/skills/diff-viewer/` + `code-review/commands/diff-viewer.md`). Bumps `code-review` plugin version to `2.1.0`.
- **Diff scope:** current working tree only. Default = unstaged + staged combined (`git diff HEAD`). No `--commit` / `--range` / `--input` flags in v1 — keep surface area small; we add them later if asked.
- **Initial defaults:** `--view unified`, `--theme auto`, `--code-theme auto`. All three are switchable in-browser, persisted to `localStorage` (`diff-viewer:view`, `diff-viewer:theme`, `diff-viewer:code-theme`).
- **Assets:** highlight.js loaded from CDN (matches `code-review-html`).
- **Output path:** `.diffs/<YYYY-MM-DD>_<short-sha-or-tag>.html`. Tag falls back to `working` when HEAD is dirty (default), `clean` when there's no diff. `-o` overrides.
- **.gitignore:** never auto-modify. Print a one-line suggestion if `.diffs/` is missing from `.gitignore`.

---

## File Structure

```
code-review/
├── .claude-plugin/
│   └── plugin.json                           # version bump 2.0.0 → 2.1.0
├── commands/
│   └── diff-viewer.md                        # NEW slash command
├── skills/
│   └── diff-viewer/                          # NEW skill
│       ├── SKILL.md
│       ├── scripts/
│       │   └── generate_diff_report.py
│       └── assets/
│           └── diff-template.html
└── README.md  /  README.ko.md                # add row in commands table
README.md  /  README.ko.md                    # repo root, add row in quick-reference
tests/
└── diff_viewer/                              # NEW test directory
    ├── conftest.py
    ├── fixtures/
    │   ├── simple.diff
    │   ├── multi-file.diff
    │   ├── rename.diff
    │   └── new-file.diff
    └── test_diff_parser.py
```

**Responsibility split inside `generate_diff_report.py`:**

| Module-level concern | Functions |
|---|---|
| Capture diff from git | `capture_diff()`, `head_short_sha()` |
| Parse unified diff into file/hunk records | `parse_git_diff()`, `parse_hunk()`, `FileDiff`, `Hunk`, `Line` |
| Language detection | `detect_language(path)` |
| Render HTML pieces | `render_file_diff()`, `render_unified_table()`, `render_split_table()`, `render_highlight_seeds()` |
| Assemble & write | `assemble_html()`, `main()` |

The diff parser must NOT be DRY'd against `code-review/skills/code-review/scripts/generate_html_report.py` yet — that script parses single-file diffs embedded inside a markdown report, while this one parses full multi-file `git diff` output. Resist refactoring until both are stable.

---

## Task 1: Plugin metadata + slash command wiring

**Files:**
- Modify: `code-review/.claude-plugin/plugin.json`
- Create: `code-review/commands/diff-viewer.md`

- [ ] **Step 1: Bump plugin version**

Read current value (should be `"version": "2.0.0"`), then change to `2.1.0`.

```json
{
  "name": "code-review",
  "description": "Automated code review that generates structured reports from git diffs. Analyzes correctness, security, complexity, maintainability, and language-specific best practices. Includes a standalone diff-viewer for browser-readable diff reports.",
  "version": "2.1.0"
}
```

- [ ] **Step 2: Create the slash command file**

Create `code-review/commands/diff-viewer.md`:

````markdown
---
description: Render the current working-tree git diff as a self-contained HTML report with unified/split views and light/dark themes.
---

Use the **diff-viewer** skill to render the current working-tree diff as a browser-readable HTML report.

**Output mode: HTML only (no markdown report, no findings analysis).**

After capturing the diff, you MUST:
1. Run `python <skill-path>/scripts/generate_diff_report.py` (no positional args needed — defaults to `git diff HEAD`).
2. The script writes `.diffs/<YYYY-MM-DD>_<short-sha-or-tag>.html`.
3. `open` the resulting `.html` file.
4. Print a one-line summary in the conversation: number of files changed, lines added/removed, and the report path.
5. If `.diffs/` is not in `.gitignore`, suggest adding it — do NOT modify `.gitignore` automatically.

This command does NOT perform a code review. For analysis use `/code-review`, `/code-review-md`, or `/code-review-html`.
````

- [ ] **Step 3: Commit**

```bash
git add code-review/.claude-plugin/plugin.json code-review/commands/diff-viewer.md
git commit -m "feat(code-review): scaffold diff-viewer slash command"
```

---

## Task 2: Diff parser — data model & fixtures

**Files:**
- Create: `code-review/skills/diff-viewer/scripts/generate_diff_report.py` (initial parser skeleton only)
- Create: `tests/diff_viewer/__init__.py` (empty)
- Create: `tests/diff_viewer/conftest.py`
- Create: `tests/diff_viewer/fixtures/simple.diff`
- Create: `tests/diff_viewer/fixtures/multi-file.diff`
- Create: `tests/diff_viewer/fixtures/rename.diff`
- Create: `tests/diff_viewer/fixtures/new-file.diff`
- Create: `tests/diff_viewer/test_diff_parser.py`

- [ ] **Step 1: Create fixture `simple.diff`**

```
diff --git a/src/foo.py b/src/foo.py
index 1111111..2222222 100644
--- a/src/foo.py
+++ b/src/foo.py
@@ -1,5 +1,6 @@
 def greet(name):
-    return "Hello, " + name
+    if not name:
+        return "Hello, world!"
+    return f"Hello, {name}!"
 
 print(greet("Ada"))
```

- [ ] **Step 2: Create fixture `multi-file.diff`**

```
diff --git a/a.py b/a.py
index 1111111..2222222 100644
--- a/a.py
+++ b/a.py
@@ -1,2 +1,2 @@
-x = 1
+x = 2
 y = 3
diff --git a/b.js b/b.js
index 3333333..4444444 100644
--- a/b.js
+++ b/b.js
@@ -1,3 +1,3 @@
 function f() {
-  return 1;
+  return 2;
 }
```

- [ ] **Step 3: Create fixture `rename.diff`**

```
diff --git a/old.py b/new.py
similarity index 85%
rename from old.py
rename to new.py
index 1111111..2222222 100644
--- a/old.py
+++ b/new.py
@@ -1,3 +1,3 @@
 def foo():
-    return 1
+    return 2
```

- [ ] **Step 4: Create fixture `new-file.diff`**

```
diff --git a/added.py b/added.py
new file mode 100644
index 0000000..1111111
--- /dev/null
+++ b/added.py
@@ -0,0 +1,3 @@
+def hello():
+    return "world"
+
```

- [ ] **Step 5: Create `conftest.py` with fixture loader**

```python
from pathlib import Path
import pytest

FIXTURES_DIR = Path(__file__).parent / "fixtures"


@pytest.fixture
def load_fixture():
    def _load(name: str) -> str:
        return (FIXTURES_DIR / name).read_text(encoding="utf-8")
    return _load
```

- [ ] **Step 6: Write the failing parser tests**

Create `tests/diff_viewer/test_diff_parser.py`:

```python
import sys
from pathlib import Path

PLUGIN_ROOT = Path(__file__).resolve().parents[2]
SCRIPTS_DIR = PLUGIN_ROOT / "code-review" / "skills" / "diff-viewer" / "scripts"
sys.path.insert(0, str(SCRIPTS_DIR))

from generate_diff_report import parse_git_diff, FileDiff, Line


def test_simple_diff_parses_one_file(load_fixture):
    files = parse_git_diff(load_fixture("simple.diff"))
    assert len(files) == 1
    f = files[0]
    assert isinstance(f, FileDiff)
    assert f.old_path == "src/foo.py"
    assert f.new_path == "src/foo.py"
    assert f.status == "modified"
    assert len(f.hunks) == 1
    types = [line.kind for line in f.hunks[0].lines]
    assert types == ["ctx", "del", "add", "add", "add", "ctx", "ctx"]


def test_multi_file_diff(load_fixture):
    files = parse_git_diff(load_fixture("multi-file.diff"))
    assert [f.new_path for f in files] == ["a.py", "b.js"]


def test_rename_status(load_fixture):
    files = parse_git_diff(load_fixture("rename.diff"))
    assert files[0].status == "renamed"
    assert files[0].old_path == "old.py"
    assert files[0].new_path == "new.py"


def test_new_file_status(load_fixture):
    files = parse_git_diff(load_fixture("new-file.diff"))
    assert files[0].status == "added"
    assert files[0].old_path == "/dev/null"
    assert files[0].new_path == "added.py"


def test_line_numbers(load_fixture):
    files = parse_git_diff(load_fixture("simple.diff"))
    lines = files[0].hunks[0].lines
    # The first line is context: old_no=1, new_no=1
    assert lines[0].old_no == 1 and lines[0].new_no == 1
    # The 'del' line advances old_no only
    assert lines[1].kind == "del" and lines[1].old_no == 2 and lines[1].new_no is None
    # Adds advance new_no only
    assert lines[2].kind == "add" and lines[2].old_no is None and lines[2].new_no == 2
```

- [ ] **Step 7: Run tests to verify they fail with ImportError**

Run: `pytest tests/diff_viewer/test_diff_parser.py -v`
Expected: FAIL — `ModuleNotFoundError: No module named 'generate_diff_report'` (file doesn't exist yet).

- [ ] **Step 8: Implement parser data classes + `parse_git_diff`**

Create `code-review/skills/diff-viewer/scripts/generate_diff_report.py`:

```python
#!/usr/bin/env python3
"""Render the current git diff as a self-contained HTML report.

Usage:
    python generate_diff_report.py [-o output.html]

With no arguments, captures `git diff HEAD` (working tree + staged combined)
and writes .diffs/<YYYY-MM-DD>_<short-sha-or-tag>.html in the repo root.
"""

from __future__ import annotations

import argparse
import html
import json
import re
import subprocess
import sys
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path

# ---------------------------------------------------------------------------
# Data model
# ---------------------------------------------------------------------------

@dataclass
class Line:
    kind: str           # 'ctx' | 'add' | 'del' | 'meta' | 'hunk'
    content: str
    old_no: int | None = None
    new_no: int | None = None


@dataclass
class Hunk:
    header: str
    old_start: int
    new_start: int
    lines: list[Line] = field(default_factory=list)


@dataclass
class FileDiff:
    old_path: str
    new_path: str
    status: str         # 'added' | 'deleted' | 'modified' | 'renamed'
    hunks: list[Hunk] = field(default_factory=list)


# ---------------------------------------------------------------------------
# Parsing
# ---------------------------------------------------------------------------

FILE_HEADER_RE = re.compile(r"^diff --git a/(?P<a>.+?) b/(?P<b>.+)$")
HUNK_HEADER_RE = re.compile(
    r"^@@ -(?P<o>\d+)(?:,(?P<ol>\d+))? \+(?P<n>\d+)(?:,(?P<nl>\d+))? @@"
)


def parse_git_diff(diff_text: str) -> list[FileDiff]:
    """Parse `git diff` output into a list of FileDiff records."""
    files: list[FileDiff] = []
    lines = diff_text.split("\n")
    i, total = 0, len(lines)

    while i < total:
        line = lines[i]
        m = FILE_HEADER_RE.match(line)
        if not m:
            i += 1
            continue

        old_path = m.group("a")
        new_path = m.group("b")
        status = "modified"
        i += 1

        # Walk extended headers until we hit `---` or another `diff --git`.
        while i < total and not lines[i].startswith("@@") \
                and not lines[i].startswith("diff --git"):
            h = lines[i]
            if h.startswith("new file mode"):
                status = "added"
                old_path = "/dev/null"
            elif h.startswith("deleted file mode"):
                status = "deleted"
                new_path = "/dev/null"
            elif h.startswith("rename from "):
                status = "renamed"
                old_path = h[len("rename from "):]
            elif h.startswith("rename to "):
                status = "renamed"
                new_path = h[len("rename to "):]
            elif h.startswith("--- "):
                # tolerate /dev/null or a/path
                pass
            elif h.startswith("+++ "):
                pass
            i += 1

        file_diff = FileDiff(old_path=old_path, new_path=new_path, status=status)

        # Hunks
        while i < total and lines[i].startswith("@@"):
            hunk, consumed = parse_hunk(lines, i)
            file_diff.hunks.append(hunk)
            i += consumed

        files.append(file_diff)

    return files


def parse_hunk(lines: list[str], start: int) -> tuple[Hunk, int]:
    """Parse a single hunk starting at lines[start]. Returns (hunk, lines_consumed)."""
    header = lines[start]
    m = HUNK_HEADER_RE.match(header)
    if not m:
        raise ValueError(f"Bad hunk header at line {start}: {header!r}")
    old_no = int(m.group("o")) - 1
    new_no = int(m.group("n")) - 1
    hunk = Hunk(header=header, old_start=old_no + 1, new_start=new_no + 1)
    i = start + 1
    while i < len(lines):
        raw = lines[i]
        if raw.startswith("@@") or raw.startswith("diff --git"):
            break
        if raw == "" and i + 1 < len(lines) and lines[i + 1].startswith("diff --git"):
            i += 1
            break
        if raw.startswith("\\"):
            # "\\ No newline at end of file" — skip silently
            i += 1
            continue
        if raw.startswith("-"):
            old_no += 1
            hunk.lines.append(Line(kind="del", content=raw[1:], old_no=old_no))
        elif raw.startswith("+"):
            new_no += 1
            hunk.lines.append(Line(kind="add", content=raw[1:], new_no=new_no))
        elif raw.startswith(" "):
            old_no += 1
            new_no += 1
            hunk.lines.append(Line(kind="ctx", content=raw[1:], old_no=old_no, new_no=new_no))
        else:
            # Unknown / blank line at EOF — stop the hunk
            break
        i += 1
    return hunk, i - start
```

- [ ] **Step 9: Run tests to verify they pass**

Run: `pytest tests/diff_viewer/test_diff_parser.py -v`
Expected: 5 passed.

- [ ] **Step 10: Commit**

```bash
git add code-review/skills/diff-viewer/scripts/generate_diff_report.py tests/diff_viewer/
git commit -m "feat(diff-viewer): add unified-diff parser with fixtures"
```

---

## Task 3: Language detection

**Files:**
- Modify: `code-review/skills/diff-viewer/scripts/generate_diff_report.py` (add `detect_language`)
- Modify: `tests/diff_viewer/test_diff_parser.py` (append tests)

- [ ] **Step 1: Write failing tests**

Append to `tests/diff_viewer/test_diff_parser.py`:

```python
from generate_diff_report import detect_language


def test_detect_language_python():
    assert detect_language("src/foo.py") == "python"


def test_detect_language_typescript_tsx():
    assert detect_language("ui/Button.tsx") == "typescript"


def test_detect_language_unknown_returns_plaintext():
    assert detect_language("LICENSE") == "plaintext"


def test_detect_language_dotfile_special_case():
    assert detect_language(".bashrc") == "bash"
    assert detect_language("Dockerfile") == "dockerfile"
```

- [ ] **Step 2: Run tests to verify failure**

Run: `pytest tests/diff_viewer/test_diff_parser.py -v`
Expected: ImportError for `detect_language`.

- [ ] **Step 3: Implement `detect_language`**

Append below the parser section in `generate_diff_report.py`:

```python
# ---------------------------------------------------------------------------
# Language detection
# ---------------------------------------------------------------------------

EXT_TO_LANG: dict[str, str] = {
    ".py": "python", ".pyi": "python",
    ".js": "javascript", ".mjs": "javascript", ".cjs": "javascript",
    ".jsx": "javascript",
    ".ts": "typescript", ".tsx": "typescript",
    ".go": "go", ".rs": "rust",
    ".java": "java", ".kt": "kotlin", ".kts": "kotlin",
    ".rb": "ruby", ".php": "php",
    ".c": "c", ".h": "c",
    ".cpp": "cpp", ".cc": "cpp", ".cxx": "cpp", ".hpp": "cpp", ".hh": "cpp",
    ".cs": "csharp", ".swift": "swift", ".scala": "scala",
    ".sh": "bash", ".bash": "bash", ".zsh": "bash", ".fish": "bash",
    ".html": "xml", ".htm": "xml", ".xml": "xml",
    ".css": "css", ".scss": "scss", ".sass": "scss", ".less": "less",
    ".json": "json", ".jsonc": "json",
    ".yaml": "yaml", ".yml": "yaml", ".toml": "ini", ".ini": "ini",
    ".md": "markdown", ".mdx": "markdown",
    ".sql": "sql", ".graphql": "graphql", ".gql": "graphql",
    ".dart": "dart", ".lua": "lua", ".r": "r", ".pl": "perl",
    ".vue": "xml", ".svelte": "xml",
    ".diff": "diff", ".patch": "diff",
}

SPECIAL_FILENAMES: dict[str, str] = {
    ".bashrc": "bash", ".zshrc": "bash", ".profile": "bash",
    "Dockerfile": "dockerfile", "Containerfile": "dockerfile",
    "Makefile": "makefile", "GNUmakefile": "makefile",
    ".gitignore": "plaintext", ".gitattributes": "plaintext",
}


def detect_language(path: str) -> str:
    """Return a highlight.js language token for the given file path."""
    if path in ("/dev/null", ""):
        return "plaintext"
    name = path.rsplit("/", 1)[-1]
    if name in SPECIAL_FILENAMES:
        return SPECIAL_FILENAMES[name]
    dot = name.rfind(".")
    if dot < 0:
        return "plaintext"
    ext = name[dot:].lower()
    return EXT_TO_LANG.get(ext, "plaintext")
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `pytest tests/diff_viewer/test_diff_parser.py -v`
Expected: all parser + language tests pass.

- [ ] **Step 5: Commit**

```bash
git add code-review/skills/diff-viewer/scripts/generate_diff_report.py tests/diff_viewer/test_diff_parser.py
git commit -m "feat(diff-viewer): map file extensions to highlight.js languages"
```

---

## Task 4: HTML template skeleton (themes + controls, no diff content yet)

**Files:**
- Create: `code-review/skills/diff-viewer/assets/diff-template.html`

The template uses `__PLACEHOLDER__` tokens that Python will substitute, matching the style of `code-review`'s template.

- [ ] **Step 1: Create the template file**

```html
<!DOCTYPE html>
<html lang="en" data-theme="__INIT_THEME__" data-code-theme="__INIT_CODE_THEME__" data-view="__INIT_VIEW__">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>__REPORT_TITLE__</title>
  <script>
    // Resolve "auto" themes BEFORE first paint to avoid FOUC.
    (function () {
      var root = document.documentElement;
      var saved = {
        theme: localStorage.getItem('diff-viewer:theme'),
        code: localStorage.getItem('diff-viewer:code-theme'),
        view: localStorage.getItem('diff-viewer:view'),
      };
      var prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
      function resolve(value, fallback) {
        if (value === 'light' || value === 'dark') return value;
        if (value === 'auto') return prefersDark ? 'dark' : 'light';
        return fallback;
      }
      root.dataset.theme = resolve(saved.theme || root.dataset.theme, prefersDark ? 'dark' : 'light');
      root.dataset.codeTheme = resolve(saved.code || root.dataset.codeTheme, prefersDark ? 'dark' : 'light');
      if (saved.view === 'unified' || saved.view === 'split') root.dataset.view = saved.view;
    })();
  </script>
  <style>
    *, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }

    /* Page palette (independent of code palette) */
    :root[data-theme="light"] {
      --page-bg: #ffffff;
      --page-fg: #1f2328;
      --muted: #59636e;
      --border: #d1d9e0;
      --surface: #f6f8fa;
      --surface-2: #eaeef2;
      --link: #0969da;
      --add-bg: #dafbe1;
      --add-line: #aceebb;
      --del-bg: #ffebe9;
      --del-line: #ffcecb;
    }
    :root[data-theme="dark"] {
      --page-bg: #0d1117;
      --page-fg: #c9d1d9;
      --muted: #8b949e;
      --border: #30363d;
      --surface: #161b22;
      --surface-2: #21262d;
      --link: #58a6ff;
      --add-bg: rgba(46, 160, 67, 0.15);
      --add-line: rgba(46, 160, 67, 0.40);
      --del-bg: rgba(248, 81, 73, 0.15);
      --del-line: rgba(248, 81, 73, 0.40);
    }

    /* Codeblock palette — driven by :root[data-code-theme], inherited by every .code */
    :root[data-code-theme="light"] .code {
      --code-bg: #ffffff;
      --code-fg: #1f2328;
      --code-ln: #8c959f;
      --hl-keyword: #cf222e;
      --hl-string: #0a3069;
      --hl-comment: #59636e;
      --hl-number: #0550ae;
      --hl-function: #8250df;
      --hl-class: #953800;
      --hl-attribute: #116329;
      --hl-builtin: #1f883d;
      --hl-meta: #59636e;
      --hl-tag: #116329;
      --hl-name: #0550ae;
    }
    :root[data-code-theme="dark"] .code {
      --code-bg: #0d1117;
      --code-fg: #c9d1d9;
      --code-ln: #6e7681;
      --hl-keyword: #ff7b72;
      --hl-string: #a5d6ff;
      --hl-comment: #8b949e;
      --hl-number: #79c0ff;
      --hl-function: #d2a8ff;
      --hl-class: #f0883e;
      --hl-attribute: #7ee787;
      --hl-builtin: #ffa657;
      --hl-meta: #8b949e;
      --hl-tag: #7ee787;
      --hl-name: #79c0ff;
    }

    body {
      font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
      background: var(--page-bg);
      color: var(--page-fg);
      line-height: 1.5;
      font-size: 14px;
    }

    /* Header */
    .page-header {
      position: sticky; top: 0; z-index: 10;
      display: flex; align-items: center; gap: 16px;
      padding: 12px 24px;
      background: var(--surface);
      border-bottom: 1px solid var(--border);
    }
    .page-header h1 {
      font-size: 15px; font-weight: 600; letter-spacing: -0.01em;
      flex: 0 1 auto; min-width: 0;
    }
    .page-header .meta { color: var(--muted); font-size: 12px; }
    .page-header .controls {
      margin-left: auto;
      display: flex; gap: 8px; align-items: center;
    }

    .ctrl-group {
      display: inline-flex;
      background: var(--surface-2);
      border: 1px solid var(--border);
      border-radius: 6px;
      padding: 2px;
      font-size: 12px;
    }
    .ctrl-group button {
      border: 0; background: transparent;
      padding: 4px 10px; border-radius: 4px;
      color: var(--muted);
      cursor: pointer; font: inherit;
    }
    .ctrl-group button.active {
      background: var(--page-bg);
      color: var(--page-fg);
      box-shadow: 0 1px 2px rgba(0,0,0,0.08);
    }
    .ctrl-label { font-size: 11px; color: var(--muted); margin-right: 4px; }

    main { padding: 16px 24px 64px; max-width: 1400px; margin: 0 auto; }

    /* File card */
    .file {
      border: 1px solid var(--border);
      border-radius: 8px;
      margin-bottom: 16px;
      overflow: hidden;
      background: var(--surface);
    }
    .file-header {
      padding: 8px 14px;
      display: flex; align-items: center; gap: 12px;
      border-bottom: 1px solid var(--border);
      font-family: ui-monospace, 'SF Mono', Menlo, monospace;
      font-size: 13px;
    }
    .file-status {
      font-size: 10px;
      text-transform: uppercase;
      letter-spacing: 0.06em;
      padding: 2px 8px;
      border-radius: 10px;
      font-weight: 600;
      font-family: -apple-system, sans-serif;
    }
    .file-status-added    { background: var(--add-bg); color: #1a7f37; }
    .file-status-deleted  { background: var(--del-bg); color: #cf222e; }
    .file-status-modified { background: var(--surface-2); color: var(--muted); }
    .file-status-renamed  { background: var(--surface-2); color: var(--link); }
    .file-path { color: var(--page-fg); }

    /* Code container — owns code palette via data-code-theme */
    .code { background: var(--code-bg); color: var(--code-fg); }

    /* Diff table — same styles for unified and split */
    .diff-table {
      width: 100%;
      border-collapse: collapse;
      font-family: ui-monospace, 'SF Mono', Menlo, monospace;
      font-size: 12.5px;
      line-height: 20px;
    }
    .diff-table td { padding: 0; border: 0; vertical-align: top; }

    .ln {
      width: 50px; min-width: 50px;
      padding: 0 10px 0 0;
      text-align: right;
      color: var(--code-ln);
      font-size: 11.5px;
      user-select: none;
      background: var(--code-bg);
      border-right: 1px solid var(--border);
    }
    .code-cell { padding: 0 14px; white-space: pre; }
    .ln-del   { background: var(--del-line); color: var(--page-fg); }
    .code-del { background: var(--del-bg); }
    .ln-add   { background: var(--add-line); color: var(--page-fg); }
    .code-add { background: var(--add-bg); }
    .code-empty { background: rgba(127,127,127,0.04); }
    .hunk-row td {
      background: var(--surface-2);
      color: var(--muted);
      padding: 4px 14px !important;
      font-style: italic;
    }
    .divider { width: 1px; min-width: 1px; background: var(--border); padding: 0; }

    /* View mode toggle — show/hide the right pane */
    :root[data-view="unified"] .pane-split { display: none; }
    :root[data-view="split"]   .pane-unified { display: none; }

    /* Highlight.js token colors — palette comes from .code[data-code-theme] */
    .hljs-keyword, .hljs-built_in, .hljs-literal { color: var(--hl-keyword); }
    .hljs-string, .hljs-attr, .hljs-template-tag, .hljs-template-variable { color: var(--hl-string); }
    .hljs-comment, .hljs-quote { color: var(--hl-comment); font-style: italic; }
    .hljs-number { color: var(--hl-number); }
    .hljs-title, .hljs-title.function_, .hljs-function .hljs-title { color: var(--hl-function); }
    .hljs-class .hljs-title, .hljs-title.class_, .hljs-type, .hljs-params { color: var(--hl-class); }
    .hljs-attribute { color: var(--hl-attribute); }
    .hljs-meta, .hljs-meta .hljs-keyword { color: var(--hl-meta); }
    .hljs-tag, .hljs-tag .hljs-name { color: var(--hl-tag); }
    .hljs-name, .hljs-selector-tag, .hljs-selector-id, .hljs-selector-class { color: var(--hl-name); }

    /* Empty state */
    .empty-state {
      text-align: center;
      padding: 64px 24px;
      color: var(--muted);
    }
    .empty-state h2 { font-size: 18px; margin-bottom: 8px; color: var(--page-fg); }

    @media (max-width: 760px) {
      .page-header { flex-wrap: wrap; padding: 10px 14px; }
      main { padding: 12px 12px 48px; }
    }
  </style>
</head>
<body>
  <header class="page-header">
    <h1>__REPORT_TITLE__</h1>
    <span class="meta">__REPORT_META__</span>
    <div class="controls">
      <div class="ctrl-group" role="group" data-control="view">
        <button data-value="unified">Unified</button>
        <button data-value="split">Split</button>
      </div>
      <span class="ctrl-label">Page</span>
      <div class="ctrl-group" role="group" data-control="theme">
        <button data-value="light">Light</button>
        <button data-value="dark">Dark</button>
      </div>
      <span class="ctrl-label">Code</span>
      <div class="ctrl-group" role="group" data-control="code-theme">
        <button data-value="light">Light</button>
        <button data-value="dark">Dark</button>
      </div>
    </div>
  </header>
  <main>__BODY__</main>
  <script id="highlight-seeds" type="application/json">__HIGHLIGHT_SEEDS__</script>
  <script src="https://cdnjs.cloudflare.com/ajax/libs/highlight.js/11.11.1/highlight.min.js"></script>
  <script>__PAGE_SCRIPT__</script>
</body>
</html>
```

- [ ] **Step 2: Smoke-check the template parses as HTML**

```bash
python -c "from pathlib import Path; html=Path('code-review/skills/diff-viewer/assets/diff-template.html').read_text(); assert '__BODY__' in html and '__HIGHLIGHT_SEEDS__' in html; print('ok')"
```

Expected output: `ok`

- [ ] **Step 3: Commit**

```bash
git add code-review/skills/diff-viewer/assets/diff-template.html
git commit -m "feat(diff-viewer): add HTML template with independent page+code themes"
```

---

## Task 5: HTML rendering — unified & split tables

**Files:**
- Modify: `code-review/skills/diff-viewer/scripts/generate_diff_report.py` (add renderers)
- Modify: `tests/diff_viewer/test_diff_parser.py` (append render tests)

- [ ] **Step 1: Write failing renderer tests**

Append to `tests/diff_viewer/test_diff_parser.py`:

```python
from generate_diff_report import render_unified_table, render_split_table


def test_render_unified_has_expected_rows(load_fixture):
    files = parse_git_diff(load_fixture("simple.diff"))
    html = render_unified_table(files[0])
    assert '<table class="diff-table">' in html
    # 1 hunk row + 7 line rows
    assert html.count('<tr') == 8
    assert "code-del" in html and "code-add" in html
    # Content is HTML-escaped
    assert "&quot;" in html or '"' in html  # tolerate either


def test_render_split_pairs_dels_and_adds(load_fixture):
    files = parse_git_diff(load_fixture("simple.diff"))
    html = render_split_table(files[0])
    assert 'class="diff-table"' in html
    # Split rows have 5 cells (ln, code, divider, ln, code) — at least one row
    assert "<td class=\"divider\"" in html
    # Where adds outnumber dels, we should see an empty del cell
    assert "code-empty" in html
```

- [ ] **Step 2: Run to verify failure**

Run: `pytest tests/diff_viewer/test_diff_parser.py -v`
Expected: ImportError for renderers.

- [ ] **Step 3: Implement renderers**

Append to `generate_diff_report.py`:

```python
# ---------------------------------------------------------------------------
# HTML rendering
# ---------------------------------------------------------------------------

def esc(text: str) -> str:
    return html.escape(text, quote=False)


def render_unified_table(file_diff: FileDiff) -> str:
    rows: list[str] = []
    for hunk in file_diff.hunks:
        rows.append(
            '<tr class="hunk-row"><td colspan="2">'
            f'{esc(hunk.header)}</td></tr>'
        )
        for line in hunk.lines:
            if line.kind == "ctx":
                rows.append(
                    f'<tr><td class="ln">{line.new_no}</td>'
                    f'<td class="code-cell">{esc(line.content)}</td></tr>'
                )
            elif line.kind == "del":
                rows.append(
                    f'<tr><td class="ln ln-del">{line.old_no}</td>'
                    f'<td class="code-cell code-del">{esc(line.content)}</td></tr>'
                )
            elif line.kind == "add":
                rows.append(
                    f'<tr><td class="ln ln-add">{line.new_no}</td>'
                    f'<td class="code-cell code-add">{esc(line.content)}</td></tr>'
                )
    return f'<table class="diff-table">{"".join(rows)}</table>'


def _split_pairs(lines: list[Line]) -> list[tuple]:
    """Group consecutive del/add lines into side-by-side change pairs."""
    pairs: list[tuple] = []
    i, n = 0, len(lines)
    while i < n:
        line = lines[i]
        if line.kind == "ctx":
            pairs.append(("both", line, line))
            i += 1
            continue
        dels: list[Line] = []
        adds: list[Line] = []
        while i < n and lines[i].kind == "del":
            dels.append(lines[i]); i += 1
        while i < n and lines[i].kind == "add":
            adds.append(lines[i]); i += 1
        for j in range(max(len(dels), len(adds))):
            left  = dels[j] if j < len(dels) else None
            right = adds[j] if j < len(adds) else None
            pairs.append(("change", left, right))
    return pairs


def render_split_table(file_diff: FileDiff) -> str:
    rows: list[str] = []
    for hunk in file_diff.hunks:
        rows.append(
            '<tr class="hunk-row"><td colspan="5">'
            f'{esc(hunk.header)}</td></tr>'
        )
        for pair in _split_pairs(hunk.lines):
            kind = pair[0]
            if kind == "both":
                line = pair[1]
                rows.append(
                    '<tr>'
                    f'<td class="ln">{line.old_no}</td>'
                    f'<td class="code-cell">{esc(line.content)}</td>'
                    '<td class="divider"></td>'
                    f'<td class="ln">{line.new_no}</td>'
                    f'<td class="code-cell">{esc(line.content)}</td>'
                    '</tr>'
                )
            else:
                left, right = pair[1], pair[2]
                l_no = left.old_no if left else ""
                l_content = esc(left.content) if left else ""
                l_ln_cls = " ln-del" if left else ""
                l_code_cls = " code-del" if left else " code-empty"
                r_no = right.new_no if right else ""
                r_content = esc(right.content) if right else ""
                r_ln_cls = " ln-add" if right else ""
                r_code_cls = " code-add" if right else " code-empty"
                rows.append(
                    '<tr>'
                    f'<td class="ln{l_ln_cls}">{l_no}</td>'
                    f'<td class="code-cell{l_code_cls}">{l_content}</td>'
                    '<td class="divider"></td>'
                    f'<td class="ln{r_ln_cls}">{r_no}</td>'
                    f'<td class="code-cell{r_code_cls}">{r_content}</td>'
                    '</tr>'
                )
    return f'<table class="diff-table">{"".join(rows)}</table>'
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `pytest tests/diff_viewer/test_diff_parser.py -v`
Expected: all green.

- [ ] **Step 5: Commit**

```bash
git add code-review/skills/diff-viewer/scripts/generate_diff_report.py tests/diff_viewer/test_diff_parser.py
git commit -m "feat(diff-viewer): render unified and split diff tables"
```

---

## Task 6: Assemble per-file cards and the full HTML page

**Files:**
- Modify: `code-review/skills/diff-viewer/scripts/generate_diff_report.py`

- [ ] **Step 1: Write a failing assembly test**

Append to `tests/diff_viewer/test_diff_parser.py`:

```python
from generate_diff_report import render_file_diff, render_body, build_highlight_seeds


def test_render_file_diff_contains_both_panes(load_fixture):
    files = parse_git_diff(load_fixture("simple.diff"))
    html_out = render_file_diff(files[0], file_idx=0)
    assert 'class="file"' in html_out
    assert 'class="code"' in html_out
    assert 'pane-unified' in html_out
    assert 'pane-split' in html_out
    assert 'file-status-modified' in html_out
    assert 'src/foo.py' in html_out


def test_render_body_handles_empty_diff():
    body = render_body([])
    assert 'empty-state' in body


def test_highlight_seeds_has_one_entry_per_file(load_fixture):
    files = parse_git_diff(load_fixture("multi-file.diff"))
    seeds = build_highlight_seeds(files)
    assert len(seeds) == 2
    assert seeds[0]["lang"] == "python"
    assert seeds[1]["lang"] == "javascript"
    # Seeds carry the reconstructed before/after hunk content
    assert "x = 1" in seeds[0]["before"]
    assert "x = 2" in seeds[0]["after"]
```

- [ ] **Step 2: Run to verify failure**

Run: `pytest tests/diff_viewer/test_diff_parser.py -v`
Expected: ImportError for the new symbols.

- [ ] **Step 3: Implement file + body renderers and the highlight-seed builder**

Append to `generate_diff_report.py`:

```python
def render_file_diff(file_diff: FileDiff, file_idx: int) -> str:
    """Render one file card with both panes (unified + split)."""
    status = file_diff.status
    if status == "renamed":
        path_html = f'{esc(file_diff.old_path)} <span class="muted">&rarr;</span> {esc(file_diff.new_path)}'
    elif status == "deleted":
        path_html = esc(file_diff.old_path)
    else:
        path_html = esc(file_diff.new_path)

    unified = render_unified_table(file_diff)
    split = render_split_table(file_diff)
    return (
        f'<section class="file" data-file-idx="{file_idx}">'
        '<header class="file-header">'
        f'<span class="file-status file-status-{status}">{status}</span>'
        f'<span class="file-path">{path_html}</span>'
        '</header>'
        '<div class="code">'
        f'<div class="pane pane-unified">{unified}</div>'
        f'<div class="pane pane-split">{split}</div>'
        '</div>'
        '</section>'
    )


def render_body(files: list[FileDiff]) -> str:
    if not files:
        return (
            '<div class="empty-state">'
            '<h2>No changes</h2>'
            '<p>The working tree is clean.</p>'
            '</div>'
        )
    return "".join(render_file_diff(f, i) for i, f in enumerate(files))


def build_highlight_seeds(files: list[FileDiff]) -> list[dict]:
    """Per-file payload of (lang, before, after) for the JS highlighter.

    `before` and `after` reconstruct the file content limited to the diff
    hunks: deletions+context go into `before`, additions+context into `after`.
    The browser tokenizes both strings once with highlight.js, then a span-
    aware line splitter (in the page script) injects highlighted line spans
    back into each `td.code-cell`.
    """
    seeds: list[dict] = []
    for f in files:
        lang = detect_language(f.new_path if f.status != "deleted" else f.old_path)
        before_lines: list[str] = []
        after_lines: list[str] = []
        for hunk in f.hunks:
            for line in hunk.lines:
                if line.kind in ("ctx", "del"):
                    before_lines.append(line.content)
                if line.kind in ("ctx", "add"):
                    after_lines.append(line.content)
        seeds.append({
            "lang": lang,
            "before": "\n".join(before_lines),
            "after": "\n".join(after_lines),
        })
    return seeds
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `pytest tests/diff_viewer/test_diff_parser.py -v`
Expected: all green.

- [ ] **Step 5: Commit**

```bash
git add code-review/skills/diff-viewer/scripts/generate_diff_report.py tests/diff_viewer/test_diff_parser.py
git commit -m "feat(diff-viewer): assemble file cards and highlight seeds"
```

---

## Task 7: Page script — view toggle, theme toggles, and span-aware line splitter

**Files:**
- Modify: `code-review/skills/diff-viewer/scripts/generate_diff_report.py` (embed JS via `PAGE_SCRIPT` constant)

We keep the JS as a Python string constant inside the script so the template doesn't need a separate `.js` file. The Python emitter then injects it into `__PAGE_SCRIPT__`.

- [ ] **Step 1: Add `PAGE_SCRIPT` constant**

Append below the renderers in `generate_diff_report.py`:

```python
# ---------------------------------------------------------------------------
# Page script (executed in the browser)
# ---------------------------------------------------------------------------

PAGE_SCRIPT = r"""
(function () {
  var root = document.documentElement;
  var STORE = {
    view: 'diff-viewer:view',
    theme: 'diff-viewer:theme',
    'code-theme': 'diff-viewer:code-theme',
  };

  // ----- Control wiring (view / theme / code-theme) -----
  function setActive(control, value) {
    document.querySelectorAll('[data-control="' + control + '"] button').forEach(function (btn) {
      btn.classList.toggle('active', btn.dataset.value === value);
    });
  }
  function applyValue(control, value) {
    if (control === 'view') root.dataset.view = value;
    else if (control === 'theme') root.dataset.theme = value;
    else if (control === 'code-theme') root.dataset.codeTheme = value;
    localStorage.setItem(STORE[control], value);
    setActive(control, value);
  }
  ['view', 'theme', 'code-theme'].forEach(function (control) {
    var current;
    if (control === 'view') current = root.dataset.view;
    else if (control === 'theme') current = root.dataset.theme;
    else current = root.dataset.codeTheme;
    setActive(control, current);
    document.querySelectorAll('[data-control="' + control + '"] button').forEach(function (btn) {
      btn.addEventListener('click', function () { applyValue(control, btn.dataset.value); });
    });
  });

  // ----- Syntax highlighting -----
  // Split highlight.js HTML output by '\n' while keeping spans balanced.
  // Approach: stream-walk the HTML, maintain a stack of currently open
  // <span class="..."> tags. On every newline in text content, close the
  // open spans, emit a line, and reopen them at the start of the next line.
  function splitHighlightedByLine(htmlSource) {
    var lines = [''];
    var openStack = [];
    var i = 0;
    var n = htmlSource.length;
    while (i < n) {
      var ch = htmlSource[i];
      if (ch === '<') {
        var end = htmlSource.indexOf('>', i);
        if (end < 0) { lines[lines.length - 1] += htmlSource.slice(i); break; }
        var tag = htmlSource.slice(i, end + 1);
        if (tag.startsWith('</')) {
          openStack.pop();
        } else if (!tag.endsWith('/>')) {
          openStack.push(tag);
        }
        lines[lines.length - 1] += tag;
        i = end + 1;
      } else if (ch === '\n') {
        // Close all open spans on this line, reopen on the next.
        for (var k = openStack.length - 1; k >= 0; k--) lines[lines.length - 1] += '</span>';
        lines.push('');
        for (var j = 0; j < openStack.length; j++) lines[lines.length - 1] += openStack[j];
        i += 1;
      } else if (ch === '&') {
        // Preserve HTML entities atomically.
        var semi = htmlSource.indexOf(';', i);
        if (semi < 0 || semi - i > 10) { lines[lines.length - 1] += '&amp;'; i += 1; }
        else { lines[lines.length - 1] += htmlSource.slice(i, semi + 1); i = semi + 1; }
      } else {
        lines[lines.length - 1] += ch;
        i += 1;
      }
    }
    return lines;
  }

  var seedsEl = document.getElementById('highlight-seeds');
  var seeds = [];
  try { seeds = JSON.parse(seedsEl.textContent || '[]'); } catch (e) { seeds = []; }

  document.querySelectorAll('section.file').forEach(function (section, idx) {
    var seed = seeds[idx];
    if (!seed || !window.hljs) return;
    var lang = seed.lang && hljs.getLanguage(seed.lang) ? seed.lang : null;
    function highlightSide(text) {
      if (!text) return [];
      var html = lang
        ? hljs.highlight(text, { language: lang, ignoreIllegals: true }).value
        : hljs.highlightAuto(text).value;
      return splitHighlightedByLine(html);
    }
    var beforeLines = highlightSide(seed.before);
    var afterLines = highlightSide(seed.after);

    var beforeIdx = 0, afterIdx = 0;
    section.querySelectorAll('.pane-unified tr').forEach(function (tr) {
      if (tr.classList.contains('hunk-row')) return;
      var cell = tr.querySelector('.code-cell');
      if (!cell) return;
      if (cell.classList.contains('code-del')) {
        var hl = beforeLines[beforeIdx++];
        if (hl !== undefined) cell.innerHTML = hl;
      } else if (cell.classList.contains('code-add')) {
        var hl2 = afterLines[afterIdx++];
        if (hl2 !== undefined) cell.innerHTML = hl2;
      } else {
        // context — consume from both sides (they're identical text)
        var hlc = afterLines[afterIdx++];
        beforeIdx += 1;
        if (hlc !== undefined) cell.innerHTML = hlc;
      }
    });

    // Split pane: walk the rows independently. For each row, the left cell
    // consumes from beforeLines if it's a del or ctx; right cell consumes
    // from afterLines if it's add or ctx. Reset indexes.
    beforeIdx = 0; afterIdx = 0;
    section.querySelectorAll('.pane-split tr').forEach(function (tr) {
      if (tr.classList.contains('hunk-row')) return;
      var cells = tr.querySelectorAll('.code-cell');
      if (cells.length !== 2) return;
      var left = cells[0], right = cells[1];
      if (left.classList.contains('code-del')) {
        var hl = beforeLines[beforeIdx++];
        if (hl !== undefined) left.innerHTML = hl;
      } else if (!left.classList.contains('code-empty')) {
        // context on the left
        var hlcl = beforeLines[beforeIdx++];
        if (hlcl !== undefined) left.innerHTML = hlcl;
      }
      if (right.classList.contains('code-add')) {
        var hl2 = afterLines[afterIdx++];
        if (hl2 !== undefined) right.innerHTML = hl2;
      } else if (!right.classList.contains('code-empty')) {
        var hlcr = afterLines[afterIdx++];
        if (hlcr !== undefined) right.innerHTML = hlcr;
      }
    });
  });
})();
"""
```

- [ ] **Step 2: No automated test (DOM behavior)**

Manual verification will happen in Task 9 (end-to-end). Do not write a JS test runner for this skill — keep the dependency surface to Python stdlib.

- [ ] **Step 3: Commit**

```bash
git add code-review/skills/diff-viewer/scripts/generate_diff_report.py
git commit -m "feat(diff-viewer): add browser script for toggles and span-aware highlighting"
```

---

## Task 8: CLI entry — capture diff, assemble HTML, write file

**Files:**
- Modify: `code-review/skills/diff-viewer/scripts/generate_diff_report.py` (add `main`, `capture_diff`, `assemble_html`, etc.)
- Modify: `tests/diff_viewer/test_diff_parser.py` (append `assemble_html` test)

- [ ] **Step 1: Write a failing test for `assemble_html`**

Append to `tests/diff_viewer/test_diff_parser.py`:

```python
from generate_diff_report import assemble_html


def test_assemble_html_substitutes_placeholders(load_fixture):
    files = parse_git_diff(load_fixture("simple.diff"))
    out = assemble_html(
        files,
        title="diff: working",
        meta="2026-05-22 · 1 file · +3 -1",
        init_view="unified",
        init_theme="auto",
        init_code_theme="auto",
    )
    assert '<!DOCTYPE html>' in out
    assert '__BODY__' not in out
    assert '__REPORT_TITLE__' not in out
    assert '__HIGHLIGHT_SEEDS__' not in out
    assert 'diff: working' in out
    assert 'src/foo.py' in out
    # JSON seeds embedded
    assert '"lang": "python"' in out or '"lang":"python"' in out
```

- [ ] **Step 2: Run to verify failure**

Run: `pytest tests/diff_viewer/test_diff_parser.py -v`
Expected: ImportError for `assemble_html`.

- [ ] **Step 3: Implement assembly, git capture, and `main`**

Append to `generate_diff_report.py`:

```python
# ---------------------------------------------------------------------------
# Template assembly + CLI
# ---------------------------------------------------------------------------

TEMPLATE_PATH = Path(__file__).resolve().parent.parent / "assets" / "diff-template.html"


def assemble_html(
    files: list[FileDiff],
    *,
    title: str,
    meta: str,
    init_view: str,
    init_theme: str,
    init_code_theme: str,
) -> str:
    template = TEMPLATE_PATH.read_text(encoding="utf-8")
    seeds = build_highlight_seeds(files)
    seeds_json = json.dumps(seeds).replace("</", "<\\/")
    body = render_body(files)
    replacements = {
        "__REPORT_TITLE__": esc(title),
        "__REPORT_META__": esc(meta),
        "__INIT_VIEW__": esc(init_view),
        "__INIT_THEME__": esc(init_theme),
        "__INIT_CODE_THEME__": esc(init_code_theme),
        "__BODY__": body,
        "__HIGHLIGHT_SEEDS__": seeds_json,
        "__PAGE_SCRIPT__": PAGE_SCRIPT,
    }
    for key, value in replacements.items():
        template = template.replace(key, value)
    return template


def capture_diff() -> str:
    """Run `git diff HEAD` to get unstaged + staged changes combined."""
    try:
        res = subprocess.run(
            ["git", "diff", "HEAD"],
            check=True,
            capture_output=True,
            text=True,
        )
        return res.stdout
    except subprocess.CalledProcessError as e:
        print(f"git diff failed: {e.stderr}", file=sys.stderr)
        sys.exit(2)
    except FileNotFoundError:
        print("git not found in PATH", file=sys.stderr)
        sys.exit(2)


def head_short_sha() -> str:
    try:
        res = subprocess.run(
            ["git", "rev-parse", "--short", "HEAD"],
            check=True,
            capture_output=True,
            text=True,
        )
        return res.stdout.strip() or "working"
    except (subprocess.CalledProcessError, FileNotFoundError):
        return "working"


def repo_root() -> Path:
    try:
        res = subprocess.run(
            ["git", "rev-parse", "--show-toplevel"],
            check=True,
            capture_output=True,
            text=True,
        )
        return Path(res.stdout.strip())
    except (subprocess.CalledProcessError, FileNotFoundError):
        return Path.cwd()


def default_output_path(files: list[FileDiff]) -> Path:
    root = repo_root()
    date = datetime.now().strftime("%Y-%m-%d")
    tag = "clean" if not files else "working"
    sha = head_short_sha()
    name = f"{date}_{sha}-{tag}.html" if sha != "working" else f"{date}_{tag}.html"
    return root / ".diffs" / name


def summary_line(files: list[FileDiff]) -> str:
    if not files:
        return "no changes"
    added = sum(1 for f in files if f.status == "added")
    deleted = sum(1 for f in files if f.status == "deleted")
    renamed = sum(1 for f in files if f.status == "renamed")
    modified = len(files) - added - deleted - renamed
    plus = minus = 0
    for f in files:
        for h in f.hunks:
            for l in h.lines:
                if l.kind == "add": plus += 1
                elif l.kind == "del": minus += 1
    parts = [f"{len(files)} file{'s' if len(files) != 1 else ''}"]
    if added: parts.append(f"{added} added")
    if deleted: parts.append(f"{deleted} deleted")
    if renamed: parts.append(f"{renamed} renamed")
    parts.append(f"+{plus} -{minus}")
    return " · ".join(parts)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Render the current working-tree git diff as an HTML report."
    )
    parser.add_argument(
        "-o", "--output", type=Path,
        help="Output HTML path (default: <repo>/.diffs/<date>_<sha>-working.html)",
    )
    parser.add_argument(
        "--view", choices=("unified", "split"), default="unified",
        help="Initial view mode (default: unified). User can toggle in-browser.",
    )
    parser.add_argument(
        "--theme", choices=("auto", "light", "dark"), default="auto",
        help="Initial page theme (default: auto = follow OS).",
    )
    parser.add_argument(
        "--code-theme", choices=("auto", "light", "dark"), default="auto",
        help="Initial codeblock theme (default: auto = follow OS).",
    )
    args = parser.parse_args()

    diff_text = capture_diff()
    files = parse_git_diff(diff_text)

    title = "Working-tree diff" if files else "Working tree clean"
    meta_str = f"{datetime.now().strftime('%Y-%m-%d %H:%M')} · {summary_line(files)}"
    html_out = assemble_html(
        files,
        title=title,
        meta=meta_str,
        init_view=args.view,
        init_theme=args.theme,
        init_code_theme=args.code_theme,
    )

    out_path = args.output or default_output_path(files)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(html_out, encoding="utf-8")
    print(f"Wrote {out_path}")


if __name__ == "__main__":
    main()
```

- [ ] **Step 4: Run tests to verify pass**

Run: `pytest tests/diff_viewer/ -v`
Expected: all green.

- [ ] **Step 5: Commit**

```bash
git add code-review/skills/diff-viewer/scripts/generate_diff_report.py tests/diff_viewer/test_diff_parser.py
git commit -m "feat(diff-viewer): add CLI entry, git capture, and html assembly"
```

---

## Task 9: End-to-end smoke test in a real working tree

**Files:** none — this is a verification step.

- [ ] **Step 1: Create a synthetic dirty tree**

```bash
cd /tmp && rm -rf dv-smoke && mkdir dv-smoke && cd dv-smoke
git init -q
cat > app.py <<'EOF'
def greet(name):
    return "Hello, " + name

print(greet("Ada"))
EOF
git add app.py && git commit -q -m "init"
cat > app.py <<'EOF'
def greet(name):
    if not name:
        return "Hello, world!"
    return f"Hello, {name}!"

print(greet("Ada"))
EOF
```

- [ ] **Step 2: Run the script**

```bash
python <repo-root>/code-review/skills/diff-viewer/scripts/generate_diff_report.py
```

Expected output: `Wrote /tmp/dv-smoke/.diffs/2026-05-22_<sha>-working.html`

- [ ] **Step 3: Open in browser and verify visually**

```bash
open /tmp/dv-smoke/.diffs/*.html
```

Manual checklist — confirm each:
- Page renders without console errors (open DevTools).
- File card shows `modified` badge and path `app.py`.
- Unified view shows del+add lines with correct colors.
- Click `Split` → side-by-side layout appears; reload page → split sticks (localStorage).
- Click `Page: Dark` → page background turns dark; codeblock stays the same.
- Click `Code: Dark` → codeblock background changes independently.
- Toggle every combination of page/code light/dark — no contrast issues.
- Python keywords (`def`, `if`, `return`) are colored.
- Refresh and confirm state persists.

- [ ] **Step 4: Cleanup the synthetic tree**

```bash
rm -rf /tmp/dv-smoke
```

- [ ] **Step 5: No commit** — verification only.

---

## Task 10: SKILL.md

**Files:**
- Create: `code-review/skills/diff-viewer/SKILL.md`

- [ ] **Step 1: Write `SKILL.md`**

```markdown
---
name: diff-viewer
description: Use when the user asks for a browser-readable HTML report of the current code changes — render `git diff` (working tree + staged) as a self-contained HTML page with split/unified views and light/dark themes. Trigger on phrases like "diff 보고서", "/diff-viewer", "show this diff in a browser", "make an HTML view of my changes", "split view diff". For a code-quality review of the same diff use `code-review-html`; for plain markdown reports use `code-review-md`.
---

# Diff Viewer (HTML)

## Overview

Renders the current working-tree `git diff` as a self-contained HTML file with:

- **Two view modes** — Unified (default) and Split (side-by-side); toggle in-browser.
- **Independent themes** — page light/dark AND codeblock light/dark are separately switchable, both default to system preference (`prefers-color-scheme`).
- **Syntax highlighting** — highlight.js (CDN) with a span-aware line splitter, so multi-line strings and comments stay intact across diff lines.
- **State persistence** — view + both themes are saved to `localStorage` and survive reload.

This skill does NOT perform code review. It just renders the diff.

**Announce at start:** "I'm using the diff-viewer skill to render the working-tree diff as HTML."

## Workflow

1. Run the script — no positional args needed:

   ```bash
   python <skill-path>/scripts/generate_diff_report.py
   ```

   Internally this runs `git diff HEAD` to combine unstaged + staged changes.

2. The script writes `<repo-root>/.diffs/<YYYY-MM-DD>_<short-sha>-working.html` and prints the path.

3. Open the report:

   ```bash
   open <repo-root>/.diffs/<file>.html
   ```

4. Print a one-line conversation summary (files changed, +added/-removed, path).

5. If `.diffs/` is not in `.gitignore`, suggest adding it. **Never** modify `.gitignore` automatically.

## Options

| Flag | Values | Default | Effect |
|---|---|---|---|
| `-o`, `--output` | path | `<repo>/.diffs/<date>_<sha>-working.html` | Override output path |
| `--view` | `unified` / `split` | `unified` | Initial view (user can toggle in-browser) |
| `--theme` | `auto` / `light` / `dark` | `auto` | Initial page theme (`auto` = system pref) |
| `--code-theme` | `auto` / `light` / `dark` | `auto` | Initial codeblock theme |

## Scope (v1)

- **In scope:** working tree + staged changes (`git diff HEAD`), file renames, added/deleted files, syntax highlighting via highlight.js.
- **Out of scope:** specific commit / range diffs, PR diffs from GitHub, stdin input, image diffs, binary file content, word-level intra-line diff. These can be added later without breaking the v1 surface.

## Red Flags

**Never:**
- Modify `.gitignore` automatically — suggest only.
- Run against a non-git directory; the script will exit with a clear error.
- Overwrite `-o` paths without warning when the path already exists (the script silently overwrites — that's expected for `.diffs/<date>_<sha>...` since reruns are idempotent).

**Always:**
- Print the output path in the conversation summary.
- Confirm the file opened successfully (or instruct the user to `open` it manually if the platform `open` command fails).

## Integration

**Pairs with:**
- **code-review-html** — when you also want findings analysis on the same diff.
- **git-commit** — render the diff before deciding how to split commits.
```

- [ ] **Step 2: Smoke-check the YAML frontmatter parses**

```bash
python -c "
import re
text = open('code-review/skills/diff-viewer/SKILL.md').read()
m = re.match(r'---\n(.*?)\n---', text, re.S)
assert m, 'frontmatter missing'
import yaml  # stdlib? if missing, fallback
" 2>/dev/null || python -c "
text = open('code-review/skills/diff-viewer/SKILL.md').read()
assert text.startswith('---\nname: diff-viewer\n'), 'frontmatter malformed'
print('ok')
"
```

Expected: `ok` (the `yaml` import will probably fail since it's not stdlib — that's fine, the fallback validates the prefix).

- [ ] **Step 3: Commit**

```bash
git add code-review/skills/diff-viewer/SKILL.md
git commit -m "docs(diff-viewer): add SKILL.md"
```

---

## Task 11: README updates (plugin + repo root)

**Files:**
- Modify: `code-review/README.md`
- Modify: `code-review/README.ko.md`
- Modify: `README.md` (repo root)
- Modify: `README.ko.md` (repo root)

- [ ] **Step 1: Add a row in `code-review/README.md` Commands table**

Locate the commands table in `code-review/README.md` (it has rows for `/code-review`, `/code-review-md`, `/code-review-html`) and add:

```markdown
| `/diff-viewer`      | Render the current working-tree diff as a self-contained HTML report with unified/split views and light/dark themes. No findings analysis. |
```

(Match the column count of the existing table — open the file first and mirror its shape.)

- [ ] **Step 2: Mirror the addition in `code-review/README.ko.md`**

Use the Korean translation:

```markdown
| `/diff-viewer`      | 현재 워킹 트리의 diff 를 unified/split 뷰와 light/dark 테마를 지원하는 HTML 리포트로 렌더링합니다. 코드 리뷰 분석은 수행하지 않습니다. |
```

- [ ] **Step 3: Add a row to the repo-root `README.md` quick reference**

In the "Quick reference → code-review" section, add:

```markdown
| `/diff-viewer`      | Render current working-tree diff as a browser-readable HTML page |
```

- [ ] **Step 4: Add the same to `README.ko.md`**

```markdown
| `/diff-viewer`      | 현재 워킹 트리 diff 를 브라우저용 HTML 페이지로 렌더링                |
```

- [ ] **Step 5: Commit**

```bash
git add code-review/README.md code-review/README.ko.md README.md README.ko.md
git commit -m "docs(code-review): document /diff-viewer command in READMEs"
```

---

## Task 12: Edge-case hardening (deleted, added, renamed, large diff)

**Files:**
- Modify: `tests/diff_viewer/test_diff_parser.py`
- Modify: `code-review/skills/diff-viewer/scripts/generate_diff_report.py` (only if bugs surface)

- [ ] **Step 1: Add fixtures for edge cases**

Add to `tests/diff_viewer/fixtures/`:

`deleted-file.diff`:
```
diff --git a/gone.py b/gone.py
deleted file mode 100644
index 1111111..0000000
--- a/gone.py
+++ /dev/null
@@ -1,3 +0,0 @@
-def gone():
-    pass
-
```

`pure-rename.diff` (rename with no edits — no hunks):
```
diff --git a/old.py b/new.py
similarity index 100%
rename from old.py
rename to new.py
```

- [ ] **Step 2: Add tests covering each edge case**

```python
def test_deleted_file_status(load_fixture):
    files = parse_git_diff(load_fixture("deleted-file.diff"))
    assert len(files) == 1
    assert files[0].status == "deleted"
    assert files[0].old_path == "gone.py"
    assert files[0].new_path == "/dev/null"
    # All hunk lines should be deletions
    kinds = [l.kind for l in files[0].hunks[0].lines]
    assert set(kinds) == {"del"}


def test_pure_rename_has_no_hunks(load_fixture):
    files = parse_git_diff(load_fixture("pure-rename.diff"))
    assert len(files) == 1
    assert files[0].status == "renamed"
    assert files[0].old_path == "old.py"
    assert files[0].new_path == "new.py"
    assert files[0].hunks == []


def test_render_body_handles_pure_rename(load_fixture):
    files = parse_git_diff(load_fixture("pure-rename.diff"))
    body = render_body(files)
    assert "old.py" in body
    assert "new.py" in body
    # Renderer should produce an empty table — but no crash
    assert 'class="file"' in body
```

- [ ] **Step 3: Run tests**

Run: `pytest tests/diff_viewer/ -v`
Expected: all green. If any fail, fix the parser/renderer — the most likely culprit is the hunk loop assuming at least one hunk follows the file header.

- [ ] **Step 4: Commit**

```bash
git add tests/diff_viewer/fixtures/deleted-file.diff tests/diff_viewer/fixtures/pure-rename.diff tests/diff_viewer/test_diff_parser.py
git commit -m "test(diff-viewer): cover deleted files and pure renames"
```

---

## Task 13: Final verification

- [ ] **Step 1: Run the full test suite**

Run: `pytest tests/ -v`
Expected: every test passes.

- [ ] **Step 2: Run a real smoke against this repo**

```bash
# Make a trivial edit then render
echo "// scratch" >> README.md
python code-review/skills/diff-viewer/scripts/generate_diff_report.py
open .diffs/*.html
git checkout README.md  # revert the scratch edit
```

Confirm in the browser:
- Both view modes work.
- Both theme toggles work independently.
- Highlight colors appear for the diffed lines.
- Reload preserves state.

- [ ] **Step 3: Clean up the smoke artifact**

```bash
rm -rf .diffs   # or keep it; just confirm it's not staged
```

- [ ] **Step 4: No commit needed** — verification only.

---

## Self-Review Checklist (run before handing off)

**Spec coverage:**
- [x] HTML output of `git diff` — Task 6, 8
- [x] Split mode + Unified mode — Task 5, 7
- [x] Light/Dark page theme — Task 4 (CSS), Task 7 (JS toggle)
- [x] Light/Dark codeblock theme (separate) — Task 4 (`.code[data-code-theme]`), Task 7
- [x] Syntax highlighting — Task 4 (token CSS), Task 6 (seeds), Task 7 (JS line splitter)
- [x] Tests — every behavioral task ships with a pytest case

**Placeholder scan:**
- All "TODO" / "TBD" / "implement later" are limited to the v1 scope-out list in `SKILL.md` (intentional, documented).
- Every step that changes code shows the actual code.
- No "add appropriate error handling" — error paths are explicit (`sys.exit(2)` on git failure, graceful empty-state for no-diff).

**Type/name consistency:**
- Parser exports: `parse_git_diff`, `FileDiff`, `Hunk`, `Line` — used identically in Tasks 2, 5, 6, 8, 12.
- Renderer exports: `render_unified_table`, `render_split_table`, `render_file_diff`, `render_body`, `build_highlight_seeds`, `assemble_html` — names match between definition and test.
- HTML placeholders: `__REPORT_TITLE__`, `__REPORT_META__`, `__INIT_VIEW__`, `__INIT_THEME__`, `__INIT_CODE_THEME__`, `__BODY__`, `__HIGHLIGHT_SEEDS__`, `__PAGE_SCRIPT__` — every one of these is replaced in `assemble_html`.
- `localStorage` keys: `diff-viewer:view`, `diff-viewer:theme`, `diff-viewer:code-theme` — used consistently in template inline script and `PAGE_SCRIPT`.

---

## Execution Handoff

Plan complete and saved to `docs/superpowers/plans/2026-05-22-diff-viewer.md`. Two execution options:

**1. Subagent-Driven (recommended)** — I dispatch a fresh subagent per task, review between tasks, fast iteration.

**2. Inline Execution** — Execute tasks in this session using `executing-plans`, batch execution with checkpoints.

Which approach?
