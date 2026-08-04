# skills — Usage

This repository exposes 20 canonical workflows and 21 installable Codex selectors across seven workflow plugins.

## Installation

### All skills at once (recommended)

```bash
npx skills add chann/skills --skill '*' --agent claude-code codex --global --yes
```

`--global` installs for your user, `--yes` skips prompts, and omitting `--copy`
keeps the installer's default symlink mode. The explicit agent list avoids the
`skills@1.5.19` bugs that can implicitly target the project-only PromptScript
adapter or fall back to copy mode during non-interactive global installs.

### A single skill

```bash
npx skills add -y -g chann/skills --skill gen-docs
```

Use `--skill <name>` with the actual selector package name, such as `review-me`, `gen-docs`, `code-review`, `diff-summary`, `diff-summary-md`, `diff-summary-quiz`, `git-commit-push`, `git-commit-push-realtime`, `gcpr`, `git-commit-realtime`, `gen-frontend-handoff`, or `gen-backend-handoff`. Each diff-summary selector is independently executable: install only the Markdown variant with `npx skills add chann/skills --skill diff-summary-md`, or only the quiz variant with `npx skills add chann/skills --skill diff-summary-quiz`. Review-me-only install: `npx skills add chann/skills --skill review-me`. Work-summary-only install: `npx skills add chann/skills --skill work-summary`. Diff-summary-only install: `npx skills add chann/skills --skill diff-summary`. Realtime checkpoint install: `npx skills add chann/skills --skill git-commit-push-realtime`. Codex `$gcpr` install, including its canonical and shared workflows: `npx skills add chann/skills --skill gcpr --skill git-commit-push-realtime --skill git-commit --skill git-commit-push`. Local realtime checkpoint install: `npx skills add chann/skills --skill git-commit-realtime`. Handoff-only install: `npx skills add chann/skills --skill gen-frontend-handoff --skill gen-backend-handoff`. Backend-only handoff install: `npx skills add chann/skills --skill gen-backend-handoff`. To inspect the available names first, run `npx skills add chann/skills -l --full-depth`.

### Manual / other platforms

```bash
git clone https://github.com/chann/skills.git
# Claude Code: symlink a plugin into your skills dir
ln -s "$(pwd)/skills/code-review" ~/.claude/skills/code-review
```

| Platform | How to install |
|---|---|
| **Claude Code** | `npx skills add chann/skills` — installs skills + slash commands |
| **Codex** | Symlink `<plugin>/skills/<name>/` into your Codex skills dir (e.g. `~/.agents/skills/`) |
| **opencode** | Drop the skill directory into your opencode skills path |
| **Copilot CLI / Gemini CLI / others** | Point the platform's skill loader at `<plugin>/skills/<name>/SKILL.md` |

Installing through `npx skills` records each skill in `skills-lock.json` with a content hash, so re-running the command detects upstream changes. For the deepest per-skill detail, see each plugin's own README: [code-review](code-review/README.md), [review-me](review-me/README.md), [doc-skill](doc-skill/README.md), [git-skill](git-skill/README.md), [handoff](handoff/README.md), [long-task](long-task/README.md), [work-summary](work-summary/README.md).

## Quick start

```
> review my changes                         # code-review
> /code-review review staged changes
> /diff-summary main..dev                  # Korean + English Markdown + bilingual HTML
> /diff-summary-md main..dev               # Korean + English Markdown only
> /diff-summary-quiz main..dev             # bilingual summary + aligned quiz
> /review-me the team invitation plan      # close every consequential decision leaf
> /git-commit                               # group changes into Conventional Commits
> /git-commit-push-realtime                 # push each verified outcome while working
> /gcpr                                      # same workflow, short alias
> /git-commit-realtime                      # commit each verified outcome locally, no push
> /gcr                                       # same local workflow, short alias
> /gen-docs                                   # generate/update project docs
> /gen-frontend-handoff main...feature-api  # hand off backend API changes to client work
> /gen-backend-handoff HEAD~5..HEAD         # hand off recent backend/server work
> /long-task build a CLI todo app end to end
> /work-summary this week                   # Markdown report of the week's agent work
```

### Explicit selectors

Claude Code uses slash commands; Codex uses dollar-prefixed skill selectors.
These are the exact names published by every package:

| Workflow | Claude Code | Codex |
|---|---|---|
| Default code review | `/code-review` | `$code-review` |
| Markdown-only code review | `/code-review-md` | `$code-review-md` |
| Diff summary | `/diff-summary` | `$diff-summary` |
| Markdown-only diff summary | `/diff-summary-md` | `$diff-summary-md` |
| Diff summary quiz | `/diff-summary-quiz` | `$diff-summary-quiz` |
| Raw diff viewer | `/diff-viewer` | `$diff-viewer` |
| Plan and design review | `/review-me` | `$review-me` |
| Project docs | `/gen-docs` | `$gen-docs` |
| Git commit | `/git-commit` | `$git-commit` |
| Git commit and push | `/git-commit-push` | `$git-commit-push` |
| Realtime commit and push | `/git-commit-push-realtime` · `/gcpr` | `$git-commit-push-realtime` · `$gcpr` |
| Realtime local commit | `/git-commit-realtime` · `/gcr` | `$git-commit-realtime` |
| Commit-message rewrite | `/git-commit-rewrite` | `$git-commit-rewrite` |
| Merge to main | `/git-merge-to-main` | `$git-merge-to-main` |
| Merge to dev | `/git-merge-to-dev` | `$git-merge-to-dev` |
| Merged-branch cleanup | `/git-branch-cleanup` | `$git-branch-cleanup` |
| Frontend handoff | `/gen-frontend-handoff` | `$gen-frontend-handoff` |
| Backend handoff | `/gen-backend-handoff` | `$gen-backend-handoff` |
| Autonomous long task | `/long-task` | `$long-task` |
| Work-history report | `/work-summary` | `$work-summary` |

## Command reference

### review-me

| Command | Action |
|---|---|
| `/review-me [topic]` | Review one consequential decision at a time until every applicable leaf passes choice, boundary, variant, consequence, and proof checks |

Codex invokes the same contract as `$review-me [topic]`. With no topic argument,
the skill reviews the plan, design, or decision already under discussion. It
inspects available evidence for discoverable facts, gives a recommended answer
with each question, and waits for one answer before following the next node.
When the decision frontier is empty, it audits every review lens and asks for
confirmation of the closure record; implementation remains outside the review
unless the surrounding request already authorized it.

### work-summary

| Command | Action |
|---|---|
| `/work-summary [range]` | Summarize coding-agent work for `today` (default), `yesterday`, `this week`, `last week`, `this month`, `last month`, a single day, or `YYYY-MM-DD..YYYY-MM-DD` as a Markdown report |

Codex invokes the same contract as `$work-summary [range]`. The skill mines
the local history stores of Claude Code, Codex, opencode, and agy read-only
(silently skipping absent ones), buckets records in the user's local timezone,
and replies with a summary or — on request — a detailed report that adds a
timeline and per-request log. Reports stay local: history content is never
sent anywhere, and a file is written under `.work-summaries/` only when asked.

### code-review

| Command | Output |
|---|---|
| `/code-review [scope]` | Markdown + self-contained bilingual HTML report under `.reviews/` |
| `/code-review-md [scope]` | Markdown-only report at `.reviews/<YYYY-MM-DD>_<short-sha>.md` |
| `/diff-summary [scope]` | Aligned Korean + English Markdown and one bilingual offline HTML under `.diff-summaries/` |
| `/diff-summary-md [scope]` | Aligned Korean + English Markdown only under `.diff-summaries/` (no HTML, no browser open) |
| `/diff-summary-quiz [scope]` | Same as `/diff-summary` plus aligned interactive `## Quiz` sections |
| `/diff-viewer` | HTML diff at `.diffs/<YYYY-MM-DD>_<tag>.html` (view only — no analysis) |

Review and summary scopes include the working tree, staged or unstaged changes, the last commit or last N commits, a specific commit, an exact commit range, a branch comparison, and PRs. `diff-summary` validates and preserves an explicit range verbatim: `main..dev` and `main...dev` retain their different Git semantics.

Choose the workflow by the result you need:

| Goal | Workflow | Output contract |
|---|---|---|
| Explain purpose, behavior, architecture, patterns, contracts, tests, and operational implications supported by the diff | `diff-summary` | Descriptive `DS-*` cards without defect severity |
| Save the same explanation as Markdown only, without HTML or a browser open | `diff-summary-md` | Validated Korean and English `.md` artifacts |
| Explain the change and test comprehension | `diff-summary-quiz` | Markdown answer key plus an interactive offline HTML quiz |
| Find correctness, security, or maintainability problems and recommend fixes | `code-review` or `code-review-md` | Findings grouped by review severity |
| Inspect changed lines without analysis | `diff-viewer` | Unified/split raw patch |

Natural-language requests such as `summarize the code changes`, `코드를 요약해줘`, `main..dev 코드를 요약해줘`, `summarize the last commit`, and `summarize PR #42` select `diff-summary`. Requests such as `마크다운 요약만 저장` select `diff-summary-md`; `이 변경 이해했는지 퀴즈로 확인` or `quiz me on this diff` select `diff-summary-quiz`. When summary and review are both requested, the explanatory cards and review findings remain separate.

`/diff-summary` uses `collect_diff_evidence.py` as its only Git/GitHub runtime. Before entering the target repository, the agent resolves a canonical absolute Python 3.10+ executable outside that repository and launches both packaged scripts with `-I`; bare `python3`, script shebangs, repository virtual environments, and Python startup injection are not allowed. The collector's fixed argv is `/absolute/trusted/python3 -I <skill-path>/scripts/collect_diff_evidence.py`. The agent sends the repository and scope as a bounded JSON request over standard input and treats the returned JSON as inert data. The collector preserves exact ranges, disables repository-configured execution surfaces, rejects unsafe repository metadata and sensitive paths, and caps command time, output, and filesystem enumeration. It never falls back to a different scope.

Representative request bodies are:

```json
{"repository": ".", "scope": {"kind": "current"}}
```

```json
{"repository": ".", "scope": {"kind": "range", "value": "main..dev"}}
```

Supported scope kinds are `current`, `staged`, `unstaged`, `last_commit`, `last_n`, `range`, `commit`, and `pr`. Current/unstaged collection lists untracked paths without content by default; an explicit second request may name up to 32 safe untracked files, with 256 KiB per-file and 2 MiB aggregate content limits. Unborn SHA-1 and SHA-256 repositories use their native empty-tree ID. Git 2.45+ is required so the collector can fail closed with the global no-lazy-fetch option.

The skill then sends its completed Korean and English Markdown reports to `generate_summary_report.py --bilingual-json-stdin --output-directory .diff-summaries`. The generator validates the output parent, both report contracts, and matching `DS-*` identities and fields. It derives filenames from the reports' shared `Date` and exact `Scope`, then atomically writes `.diff-summaries/<YYYY-MM-DD>_<scope-tag>.md`, its `.en.md` sibling, and one bilingual `.html`; the host agent opens the printed absolute HTML file URI. Korean is the default view and an accessible control switches the complete interface to English. Arbitrary scope tags encode `..` as `dot2` and `...` as `dot3`, cap the readable part, and append a 12-hex SHA-256 suffix over the exact scope so sanitized names cannot overwrite one another. Every `DS-*` card supports comments and exact language-specific Markdown copy; report-level controls copy the active source report or a feedback payload containing cards plus comments. The self-contained page also provides light/dark/system themes, a collapsible/resizable sidebar, responsive and print layouts, and guarded browser-local persistence. It works without a web server or network connection.

The bundled presentation-only renderer can also render an existing Markdown file directly:

```text
/absolute/trusted/python3 -I code-review/skills/diff-summary/scripts/generate_summary_report.py \
  .diff-summaries/2026-07-13_main-dot2-dev-<hash12>.md \
  -o .diff-summaries/2026-07-13_main-dot2-dev-<hash12>.html \
  --theme auto
```

`--theme` accepts `auto`, `light`, or `dark`. The renderer does not collect a diff or write analytical prose; the skill workflow owns evidence collection and Markdown authoring. Optional `--open` uses a fixed system launcher with ambient `BROWSER` and Python startup variables removed, but host-controlled opening is preferred.

For the skill's default write path, invoke the same script with `--bilingual-json-stdin --output-directory .diff-summaries`, then provide the exact `{"ko":"...","en":"..."}` object through the process's standard-input API. This mode creates only the direct output directory, refuses a symlinked parent, derives collision-safe names itself, and writes two Markdown sources plus one HTML report without a shell redirection or repository-created helper. Explicit single-language requests use the legacy `--markdown-stdin` mode.

`/diff-viewer` runs `generate_diff_report.py` and accepts:

| Flag | Values | Default |
|---|---|---|
| `-o`, `--output` | output HTML path | `.diffs/<YYYY-MM-DD>_<tag>.html` |
| `--view` | `unified`, `split` | `unified` |
| `--theme` | `auto`, `light`, `dark` | `auto` |
| `--language` | `auto`, `en`, `ko` | `auto` |
| `--code-scheme` | `github`, `atom-one`, `monokai`, `dracula`, `nord`, `tokyo-night`, `solarized`, `gruvbox` | `github` |

`--language` sets the initial interface language; `auto` follows the browser. The
report's Korean/English toggle switches every label, file status, summary
caption, comment control, and exported Markdown heading, and persists the choice
in `localStorage`. Diff content is code and is never translated.

### Shared HTML report interface

`code-review`, `diff-summary`, `diff-summary-quiz`, and `diff-viewer` render
different content through one deliberately shared interface. Each report is a
single self-contained file that needs no web server and no network connection.

| Capability | Behavior |
|---|---|
| Language | Korean/English toggle on every report; the choice persists per browser |
| Theme | Light, dark, and system, with a light palette forced for printing |
| Color | One `--status-*` vocabulary — success, warning, danger, info — behind every severity, impact, and diff accent, at 4.5:1 or better in both themes |
| Typography | Korean faces after the Latin system faces, and Korean prose broken on 어절 boundaries while code and paths still break anywhere |
| Icons | Inline SVG on one 24-grid with 2px round strokes; no icon font and no network request |
| Keyboard | Skip link as the first focusable element, visible focus rings, and a polite live region for copy and comment outcomes |
| Motion | Honors `prefers-reduced-motion: reduce` |

`tests/test_html_report_style_contract.py` enforces this shared contract across
the templates, so the reports cannot drift apart.

### git-skill

| Command | Action |
|---|---|
| `/git-commit` | Group working-tree changes into Conventional Commits, one per logical unit |
| `/git-commit-push` | Same, then `git push` (never `--force`) |
| `/git-commit-push-realtime` · `/gcpr` | During implementation, verify, commit, and immediately push each meaningful outcome |
| `/git-commit-realtime` · `/gcr` | During implementation, verify and commit each meaningful outcome locally — never push |
| `/git-commit-rewrite` | Rewrite recent non-Conventional commit subjects |
| `/git-merge-to-main` | Merge the current branch into `main`, then `git branch -d` the source |
| `/git-merge-to-dev` | Merge into `dev` (fallback `develop`), then `git branch -d` the source |
| `/git-branch-cleanup` | Delete every local branch already merged into a protected branch |

Protected branches — never deleted, never force-anything — are `main`, `master`, `dev`, `develop`, `development`, `stg`, `stage`, `staging`, `root`. Every workflow shows a plan before any commit, merge, or delete; the realtime invocation pre-authorizes its displayed checkpoint sequence while the other mutating workflows wait for confirmation. None run `git add .`, `--no-verify`, or `git branch -D`. `/git-commit-push-realtime` commits only green, outcome-based checkpoints, pushes each one before starting the next, and stops rather than auto-reconciling upstream drift. `/git-commit-realtime` holds the same green-checkpoint bar but keeps every checkpoint local; publication stays a separate, explicit request. A bare `--force` push is used only by `/git-commit-rewrite` in its explicit force path, which prefers `--force-with-lease`.

### doc-skill

| Command | Action |
|---|---|
| `/gen-docs [project-root]` | Generate or update `README.md`, `README.ko.md`, `ARCHITECTURE.md`, `USAGE.md` |

Invoked as `/gen-docs` (the skill name; some platforms use `$gen-docs`). It merges by heading, preserves unknown prose (and any section marked `<!-- doc-skill:keep -->`), shows per-file diffs, and writes only after you confirm. With no argument it targets the current working directory.

### handoff

| Command | Action |
|---|---|
| `/gen-frontend-handoff [scope]` | Generate `.handoffs/<date>_<scope>_frontend.md` for frontend/mobile/SDK/client implementers |
| `/gen-backend-handoff [scope]` | Generate `.handoffs/<date>_<scope>_backend.md` for backend/server implementers |

Scopes can be the current working tree, staged changes, a commit range such as `HEAD~5..HEAD`, a branch comparison such as `main...feature`, or user-provided session context. Both skills preserve the user-specified scope and mark unverified tests, deploys, or runtime behavior as unverified.

### long-task

| Command | Action |
|---|---|
| `/long-task <objective>` | Start an autonomous multi-milestone build |
| `/long-task status` | Show phase, status, elapsed time, and recent progress |
| `/long-task pause` | Stop the Stop-hook auto-continue loop |
| `/long-task resume` | Resume the auto-continue loop |
| `/long-task clear` | Delete `.agent/state.md` (keeps the other `.agent/` files) |
| `/long-task complete` | Run the completion audit and finish the run |

## Configuration

### Environment variables

| Variable | Used by | Default | Purpose |
|---|---|---|---|
| `LONG_TASK_MAX_STOP_CONTINUES` | `long-task` | `500` | Cap on automatic Stop-hook continuations (runaway guard) |
| `CLAUDE_SETTINGS` | `long-task` | `~/.claude/settings.json` | Path to the settings file the Stop hook is written to |
| `CC_REWRITE_MAP` | `git-commit-rewrite` | `/tmp/cc-rewrite-map.tsv` | Temp old→new message map used during `git filter-branch` |

### Generated paths

| Path | Written by | Notes |
|---|---|---|
| `.reviews/` | `code-review`, `code-review-md` | Markdown / HTML reports; gitignored |
| `.diff-summaries/` | `diff-summary`, `diff-summary-md`, `diff-summary-quiz` | Korean + English Markdown sources, plus bilingual self-contained HTML for `diff-summary` and `diff-summary-quiz`; gitignored |
| `.diffs/` | `diff-viewer` | HTML diff reports; gitignored |
| `.handoffs/` | `gen-frontend-handoff`, `gen-backend-handoff` | Markdown handoff documents |
| `.agent/` | `long-task` | Working-memory and lifecycle state for a run |
| `.work-summaries/` | `work-summary` | Markdown work reports, written only on request; gitignored |
| `~/.claude/settings.json` | `long-task` | Stop hook installed under `hooks.Stop` on first run |

`.reviews/`, `.diff-summaries/`, and `.diffs/` are already in this repository's `.gitignore`. In another repository the skills may suggest the matching ignore entry, but never edit `.gitignore` automatically.

## Examples

```
# Review and persist a bilingual HTML report for staged changes
> /code-review review staged changes

# Review a plan one decision at a time through every consequential leaf
> /review-me our tenant-by-tenant billing migration

# Summarize current changes, an exact branch range, the last commit, or a PR
> summarize the code changes
> /diff-summary main..dev
> summarize the last commit
> summarize PR #42

# Turn a messy working tree into clean Conventional Commits, then push
> /git-commit-push

# Build a longer change and publish each verified outcome as it completes
> /git-commit-push-realtime

# Refresh this repo's docs (root from cwd, or pass a path)
> /gen-docs
> /gen-docs ../my-other-project

# Generate role-specific handoffs from exact git scopes
> /gen-frontend-handoff main...feature-user-api
> /gen-backend-handoff HEAD~5..HEAD

# Kick off an autonomous build, then check on it later
> /long-task build a REST API for a URL shortener with tests
> /long-task status

# Report what was worked on across coding agents
> /work-summary this week
> /work-summary 2026-07-01..2026-07-31 detailed
```

## Troubleshooting

| Symptom | Likely cause | Fix |
|---|---|---|
| "Not a git repository" | Skill run outside a git repo | `cd` into a repository |
| "Detached HEAD" | git-skill needs an attached branch | `git checkout <branch>` |
| "Working tree has uncommitted changes" | merge/rewrite needs a clean tree | commit or `git stash` first |
| `/git-merge-to-main` aborts | `main` doesn't exist locally | create it, or use `/git-merge-to-dev` |
| Commit rejected by a hook | a pre-commit hook failed | fix the root cause — the skills won't `--no-verify` |
| `/git-commit-rewrite` stops on pushed commits | rewriting published history | pick the branch-based option, or pass `force` to accept `--force-with-lease` |
| No HTML report generated | Python 3.10+ missing | install Python 3.10 or newer |
| `/diff-summary` reports an invalid or empty scope | The requested ref/range is unresolved or contains no changes | Correct the exact scope; the skill will not silently fall back to the working tree |
| `/code-review` wrote no file | Report generation did not complete | inspect the handoff warning and rerun `/code-review`; use `/code-review-md` only when HTML is not wanted |
| long-task won't auto-continue | `.agent/state.md` missing or not `active` | run `/long-task` to start, or `/long-task resume` |
| long-task stopped early | hit `LONG_TASK_MAX_STOP_CONTINUES` | raise it, e.g. `export LONG_TASK_MAX_STOP_CONTINUES=1000` |

## Requirements

- An agent platform that supports skills (Claude Code, Codex, opencode, Copilot CLI, Gemini CLI, …)
- A Git repository
- Git 2.45+ for `diff-summary`, `diff-summary-md`, and `diff-summary-quiz`
- Python 3.10+ for `code-review`, `diff-summary`, `diff-summary-md`, `diff-summary-quiz`, `diff-viewer`, and `git-commit-rewrite` (standard library only — nothing to install)
