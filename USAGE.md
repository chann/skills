# skills — Usage

This repository exposes 17 independently discoverable skills across five workflow plugins.

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

Use `--skill <name>` with the actual skill name, such as `gen-docs`, `code-review`, `diff-summary`, `diff-summary-md`, `diff-summary-quiz`, `git-commit-push`, `gen-frontend-handoff`, or `gen-backend-handoff`. Each diff-summary selector is independently executable: install only the Markdown variant with `npx skills add chann/skills --skill diff-summary-md`, or only the quiz variant with `npx skills add chann/skills --skill diff-summary-quiz`. Diff-summary-only install: `npx skills add chann/skills --skill diff-summary`. Handoff-only install: `npx skills add chann/skills --skill gen-frontend-handoff --skill gen-backend-handoff`. Backend-only handoff install: `npx skills add chann/skills --skill gen-backend-handoff`. To inspect the available names first, run `npx skills add chann/skills -l --full-depth`.

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

Installing through `npx skills` records each skill in `skills-lock.json` with a content hash, so re-running the command detects upstream changes. For the deepest per-skill detail, see each plugin's own README: [code-review](code-review/README.md), [doc-skill](doc-skill/README.md), [git-skill](git-skill/README.md), [handoff](handoff/README.md), [long-task](long-task/README.md).

## Quick start

```
> review my changes                         # code-review
> /code-review review staged changes
> /diff-summary main..dev                  # explanatory Markdown + interactive HTML
> /diff-summary-md main..dev               # explanatory Markdown only
> /diff-summary-quiz main..dev             # summary + comprehension quiz
> /git-commit                               # group changes into Conventional Commits
> /gen-docs                                   # generate/update project docs
> /gen-frontend-handoff main...feature-api  # hand off backend API changes to client work
> /gen-backend-handoff HEAD~5..HEAD         # hand off recent backend/server work
> /long-task build a CLI todo app end to end
```

## Command reference

### code-review

| Command | Output |
|---|---|
| `/code-review [scope]` | Markdown + self-contained bilingual HTML report under `.reviews/` |
| `/code-review-md [scope]` | Markdown-only report at `.reviews/<YYYY-MM-DD>_<short-sha>.md` |
| `/diff-summary [scope]` | Prompt-language Markdown + interactive offline HTML under `.diff-summaries/` |
| `/diff-summary-md [scope]` | Prompt-language Markdown only under `.diff-summaries/` (no HTML, no browser open) |
| `/diff-summary-quiz [scope]` | Same as `/diff-summary` plus an interactive `## Quiz` comprehension section in both Markdown and HTML |
| `/diff-viewer` | HTML diff at `.diffs/<YYYY-MM-DD>_<tag>.html` (view only — no analysis) |

Review and summary scopes include the working tree, staged or unstaged changes, the last commit or last N commits, a specific commit, an exact commit range, a branch comparison, and PRs. `diff-summary` validates and preserves an explicit range verbatim: `main..dev` and `main...dev` retain their different Git semantics.

Choose the workflow by the result you need:

| Goal | Workflow | Output contract |
|---|---|---|
| Explain purpose, behavior, architecture, patterns, contracts, tests, and operational implications supported by the diff | `diff-summary` | Descriptive `DS-*` cards without defect severity |
| Save the same explanation as Markdown only, without HTML or a browser open | `diff-summary-md` | One validated `.md` artifact |
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

The skill then sends its completed Markdown report to `generate_summary_report.py --markdown-stdin --output-directory .diff-summaries`. The generator validates the output parent and report contract, derives the filename from the report's `Date` and exact `Scope`, and atomically writes `.diff-summaries/<YYYY-MM-DD>_<scope-tag>.md` plus a sibling `.html`; the host agent opens the printed absolute HTML file URI. Arbitrary scope tags encode `..` as `dot2` and `...` as `dot3`, cap the readable part, and append a 12-hex SHA-256 suffix over the exact scope so sanitized names cannot overwrite one another. Every `DS-*` card supports comments and exact Markdown copy; report-level controls copy the whole report or a feedback payload containing cards plus comments. The self-contained page also provides light/dark/system themes, a collapsible/resizable sidebar, responsive and print layouts, and guarded browser-local persistence. It works without a web server or network connection.

The bundled presentation-only renderer can also render an existing Markdown file directly:

```text
/absolute/trusted/python3 -I code-review/skills/diff-summary/scripts/generate_summary_report.py \
  .diff-summaries/2026-07-13_main-dot2-dev-<hash12>.md \
  -o .diff-summaries/2026-07-13_main-dot2-dev-<hash12>.html \
  --theme auto
```

`--theme` accepts `auto`, `light`, or `dark`. The renderer does not collect a diff or write analytical prose; the skill workflow owns evidence collection and Markdown authoring. Optional `--open` uses a fixed system launcher with ambient `BROWSER` and Python startup variables removed, but host-controlled opening is preferred.

For the skill's write path, invoke the same script with `--markdown-stdin --output-directory .diff-summaries`, then provide the report through the process's standard-input API. This mode creates only the direct output directory, refuses a symlinked parent, derives collision-safe names itself, and writes both Markdown and HTML without a shell redirection or repository-created helper.

`/diff-viewer` runs `generate_diff_report.py` and accepts:

| Flag | Values | Default |
|---|---|---|
| `-o`, `--output` | output HTML path | `.diffs/<YYYY-MM-DD>_<tag>.html` |
| `--view` | `unified`, `split` | `unified` |
| `--theme` | `auto`, `light`, `dark` | `auto` |
| `--code-scheme` | `github`, `atom-one`, `monokai`, `dracula`, `nord`, `tokyo-night`, `solarized`, `gruvbox` | `github` |

### git-skill

| Command | Action |
|---|---|
| `/git-commit` | Group working-tree changes into Conventional Commits, one per logical unit |
| `/git-commit-push` | Same, then `git push` (never `--force`) |
| `/git-commit-rewrite` | Rewrite recent non-Conventional commit subjects |
| `/git-merge-to-main` | Merge the current branch into `main`, then `git branch -d` the source |
| `/git-merge-to-dev` | Merge into `dev` (fallback `develop`), then `git branch -d` the source |
| `/git-branch-cleanup` | Delete every local branch already merged into a protected branch |

Protected branches — never deleted, never force-anything — are `main`, `master`, `dev`, `develop`, `development`, `stg`, `stage`, `staging`, `root`. Every workflow shows a plan and waits for confirmation before any commit, merge, or delete; none run `git add .`, `--no-verify`, or `git branch -D`. A bare `--force` push is used only by `/git-commit-rewrite` in its explicit force path, which prefers `--force-with-lease`.

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
| `.diff-summaries/` | `diff-summary`, `diff-summary-md`, `diff-summary-quiz` | Markdown source, plus interactive self-contained HTML for `diff-summary` and `diff-summary-quiz`; gitignored |
| `.diffs/` | `diff-viewer` | HTML diff reports; gitignored |
| `.handoffs/` | `gen-frontend-handoff`, `gen-backend-handoff` | Markdown handoff documents |
| `.agent/` | `long-task` | Working-memory and lifecycle state for a run |
| `~/.claude/settings.json` | `long-task` | Stop hook installed under `hooks.Stop` on first run |

`.reviews/`, `.diff-summaries/`, and `.diffs/` are already in this repository's `.gitignore`. In another repository the skills may suggest the matching ignore entry, but never edit `.gitignore` automatically.

## Examples

```
# Review and persist a bilingual HTML report for staged changes
> /code-review review staged changes

# Summarize current changes, an exact branch range, the last commit, or a PR
> summarize the code changes
> /diff-summary main..dev
> summarize the last commit
> summarize PR #42

# Turn a messy working tree into clean Conventional Commits, then push
> /git-commit-push

# Refresh this repo's docs (root from cwd, or pass a path)
> /gen-docs
> /gen-docs ../my-other-project

# Generate role-specific handoffs from exact git scopes
> /gen-frontend-handoff main...feature-user-api
> /gen-backend-handoff HEAD~5..HEAD

# Kick off an autonomous build, then check on it later
> /long-task build a REST API for a URL shortener with tests
> /long-task status
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
