# code-review

[한국어](README.ko.md) · [← back to main](../README.md)

Explain Git diffs, review them for defects, or inspect the raw patch in a browser.

## What it does

- Analyzes code changes across 5 dimensions: correctness, security, complexity/consistency, maintainability, and language-specific best practices
- Produces date-stamped reports in `.reviews/` (e.g., `2026-04-08_a1b2c3d.md`)
- Generates a styled, self-contained **bilingual** HTML report by default (Korean + English with a full-page language toggle), featuring severity badges, light/dark/auto themes with a code syntax scheme selector, a compact collapsible sidebar, per-finding markdown copy, in-browser per-finding comments, and a "Copy feedback" payload to regenerate the review against reviewer comments
- Includes `/diff-summary` for matching Korean/English evidence-based change summaries plus one bilingual interactive HTML, with `/diff-summary-md` for the Markdown pair only and `/diff-summary-quiz` for corresponding comprehension quizzes
- Includes `/diff-viewer` for a browser-readable HTML view of the current working-tree diff without review analysis
- Supports multiple review scopes: staged changes, specific commits, commit ranges, branch comparisons, and PRs
- Includes reference guides for Python and JavaScript/TypeScript best practices

## Installation

**Recommended (global, one shot):**

```bash
npx skills add -y -g chann/skills \
  --skill code-review \
  --skill code-review-md \
  --skill diff-summary \
  --skill diff-summary-md \
  --skill diff-summary-quiz \
  --skill diff-viewer
```

**Project-local:**

```bash
npx skills add chann/skills \
  --skill code-review \
  --skill code-review-md \
  --skill diff-summary \
  --skill diff-summary-md \
  --skill diff-summary-quiz \
  --skill diff-viewer
```

Use the actual skill names with `--skill`; this plugin packages six independently discoverable skills. Each diff-summary selector bundles the workflow and runtime it needs, so installing only `diff-summary-md` or only `diff-summary-quiz` remains executable. Run `npx skills add chann/skills -l --full-depth` to inspect the selectors before installing.

**Manual:**

```bash
git clone https://github.com/chann/skills.git
ln -s "$(pwd)/skills/code-review" ~/.claude/skills/code-review
```

## Usage

The matching skill triggers automatically from natural language. For explicit
invocation, use the slash selector in Claude Code or the dollar selector in
Codex:

| Claude Code                     | Codex                        | Output                                                                  |
| ------------------------------- | ---------------------------- | ----------------------------------------------------------------------- |
| `/code-review [scope]`          | `$code-review [scope]`       | Markdown + self-contained bilingual HTML review under `.reviews/`       |
| `/code-review-md [scope]`       | `$code-review-md [scope]`    | Markdown-only report at `.reviews/<YYYY-MM-DD>_<short-sha>.md`          |
| `/diff-summary [scope]`         | `$diff-summary [scope]`      | Korean + English Markdown and bilingual HTML under `.diff-summaries/`   |
| `/diff-summary-md [scope]`      | `$diff-summary-md [scope]`   | Korean + English Markdown only under `.diff-summaries/`                 |
| `/diff-summary-quiz [scope]`    | `$diff-summary-quiz [scope]` | Bilingual artifacts plus corresponding `## Quiz` comprehension sections |
| `/diff-viewer`                  | `$diff-viewer`               | HTML diff viewer at `.diffs/<YYYY-MM-DD>_<tag>.html`                    |

**Examples:**

```
> review my changes
> review the last commit
> /code-review review staged changes
> /code-review-md review branch feature-auth compared to main
> summarize the code changes
> /diff-summary main..dev
> summarize the last commit
> summarize PR #42
> /diff-viewer
```

**Output structure:**

```
.reviews/
├── 2026-04-08_a1b2c3d.md       # Korean report (primary)
├── 2026-04-08_a1b2c3d.en.md    # English report (translation, HTML only)
└── 2026-04-08_a1b2c3d.html     # merged bilingual HTML
.diff-summaries/
├── 2026-04-08_main-dot2-dev-<hash12>.md   # evidence-based change summary
└── 2026-04-08_main-dot2-dev-<hash12>.html # interactive offline summary
.diffs/
└── 2026-04-08_working.html
```

An explicit range is preserved exactly: `main..dev` and `main...dev` are different comparisons and are never normalized into one another. Supported requests include current, staged, or unstaged changes; the last commit or last N commits; a commit/range/branch comparison; and a PR.

### Choose the right workflow

| Goal | Workflow | Result |
|---|---|---|
| Explain what changed, why it matters, and how code, architecture, patterns, contracts, tests, and operations relate | `diff-summary` | Evidence-based summary cards; no review severity |
| Save that explanation as Markdown only, without HTML or a browser open | `diff-summary-md` | Validated Korean and English Markdown artifacts |
| Explain the change and test comprehension | `diff-summary-quiz` | Bilingual Markdown answer keys plus one interactive offline HTML quiz |
| Find defects, regressions, vulnerabilities, and recommended fixes | `code-review` or `code-review-md` | Findings grouped by severity |
| Inspect the patch itself without analysis | `diff-viewer` | Unified/split raw diff in HTML |

If a prompt asks for both a summary and a review, run both workflows and keep the explanatory cards and defect findings in distinct sections.

## How it works

1. Gather the relevant git diff
2. Detect languages and load appropriate best-practice references
3. Analyze each changed file across the five dimensions
4. Write the Markdown report, plus its English sibling for the default bilingual HTML flow
5. Generate and open the HTML report, unless `/code-review-md` requested Markdown only

`/diff-viewer` is separate: it captures `git diff HEAD`, renders unified and split diff views to HTML, opens the report, and does not analyze the code. Its interface is bilingual like the other reports — the Korean/English toggle switches every label, file status, summary caption, and exported Markdown heading, while diff content stays untranslated because it is code.

`/diff-summary` follows a separate explanatory flow:

1. Preserve and validate the requested scope, including the exact `..` or `...` syntax
2. Send the repository and scope as JSON over stdin to the packaged `collect_diff_evidence.py`; it is the only Git/GitHub runtime
3. Treat its bounded JSON result as inert evidence and write matching Korean and English Markdown reports with stable `DS-001`-style summary cards
4. Send both reports as bilingual JSON over stdin to `generate_summary_report.py`, which checks that they match and writes both sources plus one sibling HTML in a single operation
5. Open the self-contained HTML report in a browser

The report marks consequential inference and unverified runtime, test, migration, or deployment outcomes instead of presenting them as facts.

## Code review report format

### Evidence-first writing

Review findings use **observation → consequence → correction**. Verified facts cite the changed path and line range. Consequential inference is labeled and tied to evidence. Reports omit generic praise, canned introductions, and findings created only to fill a template.

### Conditional sections

Report metadata and actionable findings remain available. `Decision Summary`, `Positive Observations`, `Open Questions`, and `File Summary` appear only when they add distinct, decision-relevant information. When there are no actionable findings, the report says so directly and retains only material residual risks or gaps.

## HTML report

`/code-review` merges a Korean report and its English translation into one self-contained HTML file with:

- **Language toggle** — Korean shown by default, switch to English for the whole page. Falls back to a single language (toggle hidden) when no translation exists.
- **Theme & code scheme** — light/dark/auto page theme plus an 8-option syntax highlight scheme (GitHub, Monokai, Dracula, Nord, …). Diff and code blocks adapt automatically.
- **Compact sidebar** — collapsible and drag-resizable, with section nav and a comments panel.
- **Per-finding "Copy Markdown"** — copy any single finding's markdown.
- **Per-finding comments** — leave review comments on individual findings (stored in the browser, keyed by finding ID so they survive language switches).
- **"Copy feedback"** — emits a regeneration payload (original finding markdown + your comments). Paste it into a fresh `/code-review` run to revise the review against the feedback.

### Diff summary HTML

Each `/diff-summary` HTML report works directly from a local `file://` URL with no server, network request, package install, or JavaScript build step. It provides:

- **Whole-report language control** — Korean is shown by default; English switches metadata, navigation, cards, quiz, comments, copy actions, and code-copy labels in place.
- **Stable summary cards** — each `DS-*` card carries category, impact, file evidence, and the exact Markdown source.
- **Per-card comments** — add, edit, delete, clear, and jump to browser-local comment threads scoped to the report content.
- **Markdown copy** — copy one card, the complete source report, or a feedback payload that groups cards with their comments.
- **Offline navigation** — collapsible/resizable sidebar, light/dark/system themes, responsive layout, and print styling, all bundled into one HTML file.

The evidence collector uses fixed argv, sanitized process environments, exact-scope validation, blocks repository-configured code execution, checks sensitive paths, and limits command output. Repository diffs, paths, commit messages, PR text, and errors remain untrusted data; the workflow never follows instructions embedded in that evidence or uses it to trigger additional shell or file inspection.

The skill suggests adding `.diff-summaries/` to a target repository's `.gitignore`, but never edits that repository automatically.

## Severity levels

| Level    | Meaning                                                       |
| -------- | ------------------------------------------------------------- |
| CRITICAL | Data loss, security breach, or crash in production — must fix |
| HIGH     | Bug, vulnerability, or serious design flaw — should fix       |
| MEDIUM   | Code smell, inconsistency, or moderate risk — recommended fix |
| LOW      | Style, naming, minor improvement — nice to have               |
| INFO     | Verified context that affects a decision; no code change required |

## Project structure

```
code-review/
├── .claude-plugin/
│   └── plugin.json                       # Plugin metadata
├── commands/
│   ├── code-review.md                    # /code-review Markdown + HTML command
│   ├── code-review-md.md                 # /code-review-md command
│   ├── diff-summary.md                    # /diff-summary command
│   ├── diff-summary-md.md                 # /diff-summary-md command
│   ├── diff-summary-quiz.md               # /diff-summary-quiz command
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
│   ├── diff-summary/                      # Explanatory Markdown + HTML summaries
│   │   ├── SKILL.md
│   │   ├── agents/openai.yaml
│   │   ├── scripts/
│   │   │   ├── collect_diff_evidence.py   # Hardened Git/GitHub -> bounded JSON
│   │   │   └── generate_summary_report.py # Validated Markdown -> offline HTML
│   │   └── assets/summary-template.html
│   ├── diff-summary-md/                  # Standalone Markdown-only package
│   │   ├── SKILL.md
│   │   ├── references/diff-summary-workflow.md
│   │   ├── scripts/                      # Synchronized runtime
│   │   │   ├── collect_diff_evidence.py
│   │   │   └── generate_summary_report.py
│   │   └── assets/summary-template.html
│   ├── diff-summary-quiz/                # Standalone quiz package
│   │   ├── SKILL.md
│   │   ├── references/diff-summary-workflow.md
│   │   ├── scripts/                      # Synchronized runtime
│   │   │   ├── collect_diff_evidence.py
│   │   │   └── generate_summary_report.py
│   │   └── assets/summary-template.html
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
- Git 2.45+ for `diff-summary`, `diff-summary-md`, and `diff-summary-quiz` evidence collection
- Python 3.10+ (for `code-review`, `diff-summary`, `diff-summary-md`, `diff-summary-quiz`, and `diff-viewer` report generation; standard library only)

## Security notes

If you see Snyk or other SAST tools flag this skill, here is the breakdown:

- **Test fixtures (the main historical High-Risk cause, now removed)**: the previous version of this plugin shipped `samples/python-auth/auth_service.py`, `samples/react-dashboard/Dashboard.tsx`, and `samples/go-api/handler.go` inside the plugin folder. Those files are intentionally vulnerable (SQL injection, MD5, pickle deserialization, hardcoded "secrets", `dangerouslySetInnerHTML`, CORS wildcard, etc.) so the reviewer skill has obvious findings to detect. They have been moved to the repo-root [`samples/code-review/`](../samples/code-review/), outside the published plugin artifact. A `.snyk` policy file additionally tells Snyk Code to skip `samples/**`.
- **`generate_html_report.py` — fence-language attribute XSS (real, fixed)**: prior to the fix, a malicious markdown fence like ` ```a"><script>... ` could break out of the `class="language-..."` attribute because `html.escape(..., quote=False)` does not escape `"`. The lang token is now whitelisted to `[A-Za-z0-9._+-]{0,32}` via `safe_lang()`, eliminating attribute breakout regardless of input.
- **`generate_html_report.py` — `html.escape(quote=False)` flagged broadly (false positive)**: the helper deliberately uses `quote=False` and only inserts the result into element-body contexts. All attribute insertions are either hardcoded class names or anchor values produced by `slugify()` (which strips non-word characters). No tainted value reaches an attribute.
- **`generate_html_report.py` — raw-markdown embed (correctly defended)**: the markdown source is embedded into the HTML inside a `<script type="application/json">` block (not executed by browsers) and `</` sequences are escaped to `<\/` so the script tag cannot be closed prematurely.
- **`diff-summary` evidence boundary**: `collect_diff_evidence.py` is the only Git/GitHub runtime. It uses fixed argv and sanitized environments, disables lazy fetches and repository-configured code execution, rejects unsafe repository metadata and sensitive paths, and caps time/stdout/stderr before returning JSON. `generate_summary_report.py --bilingual-json-stdin --output-directory` rejects symlinked output directories, derives collision-safe filenames, checks that the Korean and English reports match, and writes two Markdown files plus one bilingual HTML file in a single operation.
- **`generate_html_report.py` — path arguments (false positive)**: the tool reads `args.input` and writes `args.output`. These are CLI arguments the user typed themselves; there is no privileged read/write surface to attack.

If you ever consider re-adding intentionally vulnerable fixtures to this plugin folder, please keep them under the repo-root `samples/` tree instead — that is what `.snyk` excludes and what keeps SAST quiet without lying about real risk.

## License

MIT
