# skills — Usage

## Installation

### All skills at once (recommended)

```bash
npx skills add -y -g chann/skills
```

`-g` installs globally for your user; `-y` skips prompts. Drop both for an interactive, project-local install.

### A single skill

```bash
npx skills add -y -g chann/skills --skill gen-docs
```

Use `--skill <name>` with the actual skill name, such as `gen-docs`, `code-review`, `git-commit-push`, `gen-frontend-handoff`, or `gen-backend-handoff`. Handoff-only install: `npx skills add chann/skills --skill gen-frontend-handoff --skill gen-backend-handoff`. Backend-only handoff install: `npx skills add chann/skills --skill gen-backend-handoff`. To inspect the available names first, run `npx skills add chann/skills -l --full-depth`.

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
> /code-review-html review staged changes
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
| `/code-review` | Findings in conversation; no file |
| `/code-review-md` | Markdown report at `.reviews/<YYYY-MM-DD>_<short-sha>.md` |
| `/code-review-html` | Markdown + self-contained bilingual HTML report under `.reviews/` |
| `/diff-viewer` | HTML diff at `.diffs/<YYYY-MM-DD>_<tag>.html` (view only — no analysis) |

Review scopes include the working tree, staged changes, a specific commit, a commit range, a branch comparison, and PRs. `/diff-viewer` runs `generate_diff_report.py` and accepts:

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
| `.reviews/` | `code-review-md`, `code-review-html` | Markdown / HTML reports; gitignored |
| `.diffs/` | `diff-viewer` | HTML diff reports; gitignored |
| `.handoffs/` | `gen-frontend-handoff`, `gen-backend-handoff` | Markdown handoff documents |
| `.agent/` | `long-task` | Working-memory and lifecycle state for a run |
| `~/.claude/settings.json` | `long-task` | Stop hook installed under `hooks.Stop` on first run |

`.reviews/` and `.diffs/` are already in `.gitignore`. The skills suggest, but never modify, your `.gitignore`.

## Examples

```
# Review and persist a bilingual HTML report for staged changes
> /code-review-html review staged changes

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
| `/code-review` wrote no file | `/code-review` is conversation-only | use `/code-review-md` or `/code-review-html` |
| long-task won't auto-continue | `.agent/state.md` missing or not `active` | run `/long-task` to start, or `/long-task resume` |
| long-task stopped early | hit `LONG_TASK_MAX_STOP_CONTINUES` | raise it, e.g. `export LONG_TASK_MAX_STOP_CONTINUES=1000` |

## Requirements

- An agent platform that supports skills (Claude Code, Codex, opencode, Copilot CLI, Gemini CLI, …)
- A Git repository
- Python 3.10+ for `code-review-html`, `diff-viewer`, and `git-commit-rewrite` (standard library only — nothing to install)
