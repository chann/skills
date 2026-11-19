# diff-summary

[한국어](README.ko.md) · [← back to main](../README.md)

Explain a Git diff as matching Korean and English reports, or render the raw patch in a browser. One summary skill covers three output modes through options; `diff-viewer` stays separate because it shows the patch without analysis.

## What it does

- `/diff-summary` explains what changed, why, and how code, architecture, patterns, contracts, tests, and operations relate. It writes aligned Korean and English Markdown plus one self-contained bilingual interactive HTML report under `.diff-summaries/`.
- `--md` keeps only the two Markdown files: no HTML, no browser.
- `--quiz` adds an aligned `## Quiz` to both reports and an interactive quiz to the HTML.
- `/diff-viewer` renders the current working-tree diff as unified and split HTML views with a Korean/English toggle. It does not analyze the code.
- Supports current, staged, or unstaged changes, the last commit or last N commits, a commit, a range or branch comparison, and a PR.

## Installation

**Recommended (global, one shot):**

```bash
npx skills add -y -g chann/skills \
  --skill diff-summary \
  --skill diff-viewer
```

**Project-local:**

```bash
npx skills add chann/skills \
  --skill diff-summary \
  --skill diff-viewer
```

Each skill installs alone. `diff-summary` bundles its collector, generator, and HTML template, so it does not need `diff-viewer`. Run `npx skills add chann/skills -l --full-depth` to inspect the selectors before installing.

**Manual:**

```bash
git clone https://github.com/chann/skills.git
ln -s "$(pwd)/skills/diff-summary" ~/.claude/skills/diff-summary
```

## Usage

The matching skill triggers from natural language. For explicit invocation, use the slash selector in Claude Code or the dollar selector in Codex:

| Claude Code | Codex | Output |
| --- | --- | --- |
| `/diff-summary [scope]` | `$diff-summary [scope]` | Korean + English Markdown and bilingual HTML under `.diff-summaries/` |
| `/diff-summary [scope] --md` | `$diff-summary [scope] --md` | Korean + English Markdown only |
| `/diff-summary [scope] --quiz` | `$diff-summary [scope] --quiz` | The default artifacts plus aligned `## Quiz` sections and an interactive quiz |
| `/diff-viewer` | `$diff-viewer` | HTML diff viewer at `.diffs/<YYYY-MM-DD>_<tag>.html` |

Natural-language equivalents also work: "markdown only" and "마크다운만" select `--md`; "퀴즈" and "quiz me" select `--quiz`.

`--md --quiz` together writes the two Markdown files with their quiz sections and no HTML. The generator validates the `## Quiz` section in Markdown-only mode, and `--md` decides that no HTML or browser is produced.

**Examples:**

```
> summarize the code changes
> /diff-summary main..dev
> summarize the last commit
> summarize PR #42
> /diff-summary HEAD~3..HEAD --md
> 마지막 커밋 diff 퀴즈 만들어줘
> /diff-viewer
```

**Output structure:**

```
.diff-summaries/
├── 2026-04-08_main-dot2-dev-<hash12>.md     # Korean report
├── 2026-04-08_main-dot2-dev-<hash12>.en.md  # English report
└── 2026-04-08_main-dot2-dev-<hash12>.html   # bilingual interactive page (not with --md)
.diffs/
└── 2026-04-08_working.html
```

An explicit range is preserved exactly: `main..dev` and `main...dev` are different comparisons and are never normalized into one another.

### Choose the right workflow

| Goal | Workflow | Result |
|---|---|---|
| Explain what changed, why it matters, and how the pieces relate | `diff-summary` | Evidence-based summary cards; no review severity |
| Save that explanation as Markdown only | `diff-summary --md` | Validated Korean and English Markdown |
| Explain the change and test comprehension | `diff-summary --quiz` | Markdown answer keys plus one offline HTML quiz |
| Find defects, regressions, or vulnerabilities | `interrogate` | Findings with severity |
| Understand how existing code works | `how` | A traced explanation of the code |
| Inspect the patch itself without analysis | `diff-viewer` | Unified or split raw diff in HTML |

If a prompt asks for both a summary and a review, run both workflows and keep the explanatory cards and the defect findings in distinct sections.

## How it works

`/diff-summary`:

1. Preserve and validate the requested scope, including the exact `..` or `...` syntax.
2. Send the repository and scope as JSON over stdin to the packaged `collect_diff_evidence.py`, the only Git/GitHub runtime.
3. Treat its bounded JSON result as inert evidence and write matching Korean and English Markdown reports with stable `DS-001`-style cards (and `QZ-001` questions with `--quiz`).
4. Send both reports as bilingual JSON over stdin to `generate_summary_report.py`, which checks that they match and writes both sources plus one sibling HTML in a single operation (`--markdown-only` writes just the sources).
5. Open the self-contained HTML in a browser, except with `--md`.

The report marks consequential inference and unverified runtime, test, migration, or deployment outcomes instead of presenting them as facts.

`/diff-viewer` is separate: it captures `git diff HEAD`, renders unified and split views, opens the report, and does not analyze the code. Its Korean/English toggle switches every label, file status, summary caption, and exported Markdown heading; diff content stays untranslated because it is code.

### Diff summary HTML

Each report works from a local `file://` URL with no server, network request, package install, or JavaScript build step:

- **Whole-report language control** — Korean is shown by default; English switches metadata, navigation, cards, quiz, comments, copy actions, and code-copy labels in place.
- **Stable summary cards** — each `DS-*` card carries category, impact, file evidence, and the exact Markdown source.
- **Per-card comments** — add, edit, delete, clear, and jump to browser-local comment threads scoped to the report content.
- **Markdown copy** — copy one card, the complete source report, or a feedback payload that groups cards with their comments.
- **Quiz** — with `--quiz`, one click marks an option correct or incorrect, shows the answer and explanation, and printing gives an answer key.
- **Offline navigation** — collapsible and resizable sidebar, light/dark/system themes, responsive layout, and print styling in one file.

### Diff viewer

- **Korean/English toggle**, within-line word diff highlighting, drag-to-select line comments, a collapsible and resizable sidebar, light/dark/auto themes, and eight syntax schemes (GitHub, Atom One, Monokai, Dracula, Nord, Tokyo Night, Solarized, Gruvbox).
- **Copy Markdown** copies the current review thread as a Markdown report.
- Options: `-o output.html`, `--view unified|split`, `--theme auto|light|dark`, `--language auto|en|ko`, `--code-scheme <scheme>`.

## Safety boundary

The evidence collector uses fixed argv, sanitized process environments, exact-scope validation, blocks repository-configured code execution, checks sensitive paths, and limits command output. Repository diffs, paths, commit messages, PR text, and errors remain untrusted data; the workflow never follows instructions embedded in that evidence or uses it to trigger additional shell or file inspection. The generator rejects symlinked output directories and derives collision-safe file names itself.

The skill suggests adding `.diff-summaries/` and `.diffs/` to a target repository's `.gitignore`, but never edits that repository automatically.

## Project structure

```
diff-summary/
├── .claude-plugin/
│   └── plugin.json                        # Plugin metadata
├── commands/
│   ├── diff-summary.md                    # /diff-summary [scope] [--md] [--quiz]
│   └── diff-viewer.md                     # /diff-viewer
└── skills/
    ├── diff-summary/
    │   ├── SKILL.md
    │   ├── agents/openai.yaml
    │   ├── evals/evals.json
    │   ├── scripts/
    │   │   ├── collect_diff_evidence.py   # Hardened Git/GitHub -> bounded JSON
    │   │   └── generate_summary_report.py # Validated Markdown -> offline HTML
    │   └── assets/summary-template.html
    └── diff-viewer/
        ├── SKILL.md
        ├── scripts/generate_diff_report.py
        └── assets/diff-template.html
```

## Requirements

- [Claude Code](https://code.claude.com) (CLI, desktop app, or IDE extension) or Codex
- Git repository
- Git 2.45+ for `diff-summary` evidence collection
- Python 3.10+ for `diff-summary` and `diff-viewer` report generation (standard library only)

## License

MIT
