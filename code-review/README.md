# code-review

[한국어](README.ko.md) · [← back to main](../README.md)

Automated code review that generates persistent **markdown and HTML report files** from git diffs.

## What it does

- Analyzes code changes across 5 dimensions: correctness, security, complexity/consistency, maintainability, and language-specific best practices
- Produces date-stamped reports in `.reviews/` (e.g., `2026-04-08_a1b2c3d.md`)
- Optionally generates a styled, self-contained **bilingual** HTML report (Korean + English with a full-page language toggle) featuring severity badges, light/dark/auto themes with a code syntax scheme selector, a compact collapsible sidebar, per-finding markdown copy, in-browser per-finding comments, and a "Copy feedback" payload to regenerate the review against reviewer comments
- Includes `/diff-viewer` for a browser-readable HTML view of the current working-tree diff without review analysis
- Supports multiple review scopes: staged changes, specific commits, commit ranges, branch comparisons, and PRs
- Includes reference guides for Python and JavaScript/TypeScript best practices

## Installation

**Recommended (global, one shot):**

```bash
npx skills add -y -g chann/skills \
  --skill code-review \
  --skill code-review-md \
  --skill code-review-html \
  --skill diff-viewer
```

**Project-local:**

```bash
npx skills add chann/skills \
  --skill code-review \
  --skill code-review-md \
  --skill code-review-html \
  --skill diff-viewer
```

Use the actual skill names with `--skill`; this plugin packages the review and diff-viewer skills together.

**Manual:**

```bash
git clone https://github.com/chann/skills.git
ln -s "$(pwd)/skills/code-review" ~/.claude/skills/code-review
```

## Usage

The skill triggers automatically when you ask Claude Code to review code, or you can use explicit commands:

| Command             | Skill              | Output                                                     |
| ------------------- | ------------------ | ---------------------------------------------------------- |
| `/code-review`      | `code-review`      | Findings shown in conversation; no file                    |
| `/code-review-md`   | `code-review-md`   | Markdown report at `.reviews/<YYYY-MM-DD>_<short-sha>.md`  |
| `/code-review-html` | `code-review-html` | Markdown + self-contained HTML report                      |
| `/diff-viewer`      | `diff-viewer`      | HTML diff viewer at `.diffs/<YYYY-MM-DD>_<tag>.html`       |

**Examples:**

```
> review my changes
> review the last commit
> /code-review-html review staged changes
> /code-review-md review branch feature-auth compared to main
> /diff-viewer
```

**Output structure:**

```
.reviews/
├── 2026-04-08_a1b2c3d.md       # Korean report (primary)
├── 2026-04-08_a1b2c3d.en.md    # English report (translation, HTML only)
└── 2026-04-08_a1b2c3d.html     # merged bilingual HTML
.diffs/
└── 2026-04-08_working.html
```

## How it works

1. Gather the relevant git diff
2. Detect languages and load appropriate best-practice references
3. Analyze each changed file across the five dimensions
4. Present findings in conversation, or write report files (depending on the command)
5. Show a summary of findings

`/diff-viewer` is separate: it captures `git diff HEAD`, renders unified and split diff views to HTML, opens the report, and does not analyze the code.

## Report format

Each report includes:

- **Executive Summary** — files changed, lines added/removed, finding counts, overall risk level
- **Findings** — grouped by severity (CRITICAL / HIGH / MEDIUM / LOW), each with file reference, code snippet, and suggested fix
- **Positive Observations** — things the code does well
- **File-by-File Summary** — quick reference table of all changed files and their risk level

## HTML report

`/code-review-html` merges a Korean report and its English translation into one self-contained HTML file with:

- **Language toggle** — Korean shown by default, switch to English for the whole page. Falls back to a single language (toggle hidden) when no translation exists.
- **Theme & code scheme** — light/dark/auto page theme plus an 8-option syntax highlight scheme (GitHub, Monokai, Dracula, Nord, …). Diff and code blocks adapt automatically.
- **Compact sidebar** — collapsible and drag-resizable, with section nav and a comments panel.
- **Per-finding "Copy MD"** — copy any single finding's markdown.
- **Per-finding comments** — leave review comments on individual findings (stored in the browser, keyed by finding ID so they survive language switches).
- **"Copy feedback"** — emits a regeneration payload (original finding markdown + your comments). Paste it into a fresh `/code-review-html` run to revise the review against the feedback.

## Severity levels

| Level    | Meaning                                                       |
| -------- | ------------------------------------------------------------- |
| CRITICAL | Data loss, security breach, or crash in production — must fix |
| HIGH     | Bug, vulnerability, or serious design flaw — should fix       |
| MEDIUM   | Code smell, inconsistency, or moderate risk — recommended fix |
| LOW      | Style, naming, minor improvement — nice to have               |
| INFO     | Positive observation or contextual note                       |

## Project structure

```
code-review/
├── .claude-plugin/
│   └── plugin.json                       # Plugin metadata
├── commands/
│   ├── code-review.md                    # /code-review (conversation-only)
│   ├── code-review-md.md                 # /code-review-md command
│   ├── code-review-html.md               # /code-review-html command
│   └── diff-viewer.md                    # /diff-viewer command
├── skills/
│   ├── code-review/                      # Main skill — full workflow + shared assets
│   │   ├── SKILL.md                      # Skill definition and workflow
│   │   ├── scripts/
│   │   │   ├── diff_stats.py             # Git diff statistics extractor
│   │   │   └── generate_html_report.py   # Markdown → HTML report converter
│   │   ├── references/
│   │   │   ├── review-criteria.md        # Detailed review criteria framework
│   │   │   ├── common-vulnerabilities.md # OWASP-based security checklist
│   │   │   ├── python.md                 # Python best practices
│   │   │   └── javascript-typescript.md  # JS/TS best practices
│   │   └── assets/
│   │       └── report-template.html      # HTML report template
│   ├── code-review-md/
│   │   └── SKILL.md                      # Markdown variant skill
│   ├── code-review-html/
│   │   └── SKILL.md                      # HTML variant skill
│   └── diff-viewer/
│       ├── SKILL.md                      # HTML diff viewer workflow
│       ├── scripts/
│       │   └── generate_diff_report.py   # Git diff -> HTML converter
│       └── assets/
│           └── diff-template.html        # Diff viewer template
└── .snyk                                 # SAST exclude policy for sample fixtures
```

Sample fixtures (intentionally vulnerable code the reviewer is meant to flag) live OUTSIDE this plugin folder, at the repo-root [`samples/code-review/`](../samples/code-review/). They are not part of the published plugin artifact.

## Requirements

- [Claude Code](https://code.claude.com) (CLI, desktop app, or IDE extension)
- Git repository
- Python 3.10+ (for HTML report generation)

## Security notes

If you see Snyk or other SAST tools flag this skill, here is the breakdown:

- **Test fixtures (the main historical High-Risk cause, now removed)**: the previous version of this plugin shipped `samples/python-auth/auth_service.py`, `samples/react-dashboard/Dashboard.tsx`, and `samples/go-api/handler.go` inside the plugin folder. Those files are intentionally vulnerable (SQL injection, MD5, pickle deserialization, hardcoded "secrets", `dangerouslySetInnerHTML`, CORS wildcard, etc.) so the reviewer skill has obvious findings to detect. They have been moved to the repo-root [`samples/code-review/`](../samples/code-review/), outside the published plugin artifact. A `.snyk` policy file additionally tells Snyk Code to skip `samples/**`.
- **`generate_html_report.py` — fence-language attribute XSS (real, fixed)**: prior to the fix, a malicious markdown fence like ` ```a"><script>... ` could break out of the `class="language-..."` attribute because `html.escape(..., quote=False)` does not escape `"`. The lang token is now whitelisted to `[A-Za-z0-9._+-]{0,32}` via `safe_lang()`, eliminating attribute breakout regardless of input.
- **`generate_html_report.py` — `html.escape(quote=False)` flagged broadly (false positive)**: the helper deliberately uses `quote=False` and only inserts the result into element-body contexts. All attribute insertions are either hardcoded class names or anchor values produced by `slugify()` (which strips non-word characters). No tainted value reaches an attribute.
- **`generate_html_report.py` — raw-markdown embed (correctly defended)**: the markdown source is embedded into the HTML inside a `<script type="application/json">` block (not executed by browsers) and `</` sequences are escaped to `<\/` so the script tag cannot be closed prematurely.
- **`generate_html_report.py` — path arguments (false positive)**: the tool reads `args.input` and writes `args.output`. These are CLI arguments the user typed themselves; there is no privileged read/write surface to attack.

If you ever consider re-adding intentionally vulnerable fixtures to this plugin folder, please keep them under the repo-root `samples/` tree instead — that is what `.snyk` excludes and what keeps SAST quiet without lying about real risk.

## License

MIT
