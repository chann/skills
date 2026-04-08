# skills

[한국어](README.ko.md)

A collection of practical agent skills for software engineering workflows.

## Skills

### code-review

Automated code review that generates persistent **markdown and HTML report files** from git diffs.

**What it does:**

- Analyzes code changes across 5 dimensions: correctness, security, complexity/consistency, maintainability, and language-specific best practices
- Produces date-stamped reports in `.reviews/` (e.g., `2026-04-08_a1b2c3d.md`)
- Optionally generates a styled, self-contained HTML report with severity badges, collapsible findings, and sidebar navigation
- Supports multiple review scopes: staged changes, specific commits, commit ranges, branch comparisons, and PRs
- Includes reference guides for Python and JavaScript/TypeScript best practices

**Example output structure:**

```
.reviews/
├── 2026-04-08_a1b2c3d.md
└── 2026-04-08_a1b2c3d.html
```

## Installation

### Using [skills.sh](https://skills.sh) (recommended)

```bash
npx skills add chann/skills
```

Install globally (available across all projects):

```bash
npx skills add -g chann/skills
```

### Manual installation

Clone and symlink the skill into your Claude Code skills directory:

```bash
git clone https://github.com/chann/skills.git
ln -s "$(pwd)/skills/code-review" ~/.claude/skills/code-review
```

## Usage

Once installed, the skill triggers automatically when you ask Claude Code to review code, or you can use explicit commands:

| Command | Output |
|---|---|
| `/code-review` | Show findings in conversation (no file) |
| `/code-review:md` | Write markdown report to `.reviews/` |
| `/code-review:markdown` | Same as `:md` |
| `/code-review:html` | Write markdown + HTML reports to `.reviews/` |

**Examples:**

```
> review my changes
> review the last commit
> /code-review:html review staged changes
> /code-review:md review branch feature-auth compared to main
```

The skill will:

1. Gather the relevant git diff
2. Detect languages and load appropriate best practice references
3. Analyze each changed file for issues
4. Present findings in the conversation, or write report files (depending on command)
5. Show a summary of findings

### Report format

Each report includes:

- **Executive Summary** — files changed, lines added/removed, finding counts, overall risk level
- **Findings** — grouped by severity (CRITICAL / HIGH / MEDIUM / LOW), each with file reference, code snippet, and suggested fix
- **Positive Observations** — things the code does well
- **File-by-File Summary** — quick reference table of all changed files and their risk level

### Severity levels

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
│   └── plugin.json                   # Plugin metadata
├── commands/
│   ├── html.md                       # /code-review:html command
│   ├── md.md                         # /code-review:md command
│   └── markdown.md                   # /code-review:markdown command
├── skills/
│   └── code-review/
│       ├── SKILL.md                  # Skill definition and workflow
│       ├── scripts/
│       │   ├── diff_stats.py         # Git diff statistics extractor
│       │   └── generate_html_report.py  # Markdown → HTML report converter
│       ├── references/
│       │   ├── review-criteria.md    # Detailed review criteria framework
│       │   ├── common-vulnerabilities.md  # OWASP-based security checklist
│       │   ├── python.md            # Python best practices
│       │   └── javascript-typescript.md   # JS/TS best practices
│       └── assets/
│           └── report-template.html  # HTML report template
└── samples/                          # Test sample files
```

## Requirements

- [Claude Code](https://code.claude.com) (CLI, desktop app, or IDE extension)
- Git repository
- Python 3.10+ (for HTML report generation)

## License

MIT
