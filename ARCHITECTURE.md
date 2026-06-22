# skills — Architecture

## Overview

`skills` is a monorepo of [Claude Code](https://code.claude.com) skill plugins for everyday software-engineering workflows. It bundles four independent plugins — `code-review`, `doc-skill`, `git-skill`, and `long-task` — that together expose 12 skills.

Each skill is authored as a portable `SKILL.md` document plus optional `references/`, `templates/`, `assets/`, and `scripts/`. A thin Claude Code wrapper (`.claude-plugin/plugin.json` + `commands/*.md`) adds slash-command ergonomics on top, but the skill bodies reference no Claude-Code-only tooling, so the same skills run on any agent platform that loads skills (Codex, opencode, Copilot CLI, Gemini CLI, …).

## Components

### Plugins

| Plugin | Version | Skills | Responsibility |
|---|---|---|---|
| `code-review` | 2.2.0 | `code-review`, `code-review-md`, `code-review-html`, `diff-viewer` | Review git diffs for correctness, security, complexity, maintainability, and language best practices; emit conversation, markdown, or bilingual HTML reports; render standalone HTML diffs |
| `doc-skill` | 0.1.0 | `gen-docs` | Generate/update `README.md`, `README.ko.md`, `ARCHITECTURE.md`, `USAGE.md` while preserving hand-written prose |
| `git-skill` | 0.3.0 | `git-commit`, `git-commit-push`, `git-commit-rewrite`, `git-merge-to-main`, `git-merge-to-dev`, `git-branch-cleanup` | Conventional-Commit creation, push, history rewrite, guarded merges, and merged-branch cleanup |
| `long-task` | 0.2.1 | `long-task` | Autonomously orchestrate multi-milestone projects with parallel worktree subagents, milestone reviews, and a Stop-hook auto-continue loop |

### Skill internals

Every plugin shares the same layout:

```
<plugin>/
├── .claude-plugin/plugin.json   # name, version, description
├── commands/<command>.md        # one slash command per skill
└── skills/<skill>/
    ├── SKILL.md                 # the portable skill definition
    ├── references/              # optional knowledge the skill loads on demand
    ├── templates/               # optional output templates
    ├── assets/                  # optional static assets (e.g. HTML templates)
    └── scripts/                 # optional Python helpers (stdlib only)
```

- **`code-review`** centralizes the work in the main `code-review` skill: the shared review workflow, four reference guides (`review-criteria`, `common-vulnerabilities`, `python`, `javascript-typescript`), and two scripts (`diff_stats.py`, `generate_html_report.py`). The `code-review-md` and `code-review-html` variants are thin skills that reuse that workflow and only choose an output format. `diff-viewer` is standalone — `generate_diff_report.py` plus `diff-template.html` — and does no analysis.
- **`git-skill`** keeps its single Python helper, `rewrite_msg.py`, under `git-commit/scripts/`; the `git-commit-rewrite` workflow shares it.
- **`long-task`** carries `long_task.py` (lifecycle commands + Stop-hook installer) and two references (`completion-audit`, `project-templates`).
- **`doc-skill`** carries four output templates under `gen-docs/templates/`.

### Supporting files

- **`.agents/skills/`** — a committed, flattened mirror of all 12 skill directories, for platforms that load skills from a single flat folder (e.g. Codex's `~/.agents/skills/`).
- **`samples/code-review/`** — intentionally vulnerable fixtures (`go-api`, `python-auth`, `react-dashboard`) used to demo the reviewer. Kept outside the plugin folders so they never ship in a published plugin.
- **`tests/`** — pytest suite: per-plugin package tests plus `diff_viewer/` unit tests with `.diff` fixtures.
- **`skills-lock.json`** — lockfile pinning each skill's `source`, `sourceType`, `skillPath`, and `computedHash`.
- **`VERSION`** — release stamp in `head.yymmdd.patch` form.
- **`.snyk`** — SAST policy that excludes the intentionally vulnerable `samples/**`.

## Data flow

### Installation

`npx skills add chann/skills` reads the repo's plugins, resolves the requested skills, records them in `skills-lock.json` (with a content hash per skill), and copies each skill directory into the target platform's skills location. The `computedHash` lets the installer detect upstream changes on later runs.

### Invocation (Claude Code)

1. The user types a slash command (e.g. `/code-review-md`) or triggers a skill by natural language.
2. Claude Code loads the matching `commands/*.md`, which points at the skill.
3. The skill runs its `SKILL.md` workflow, loading `references/` and invoking bundled `python3` scripts as needed.
4. Outputs land where the skill specifies — review reports under `.reviews/`, diff reports under `.diffs/`, git history changes, or `long-task` state under `.agent/`.

### long-task autonomy loop

`/long-task` Phase 1 writes the working-memory files under `.agent/` (`goal.md`, `plans.md`, `standards.md`, `implement.md`, `progress.md`, `state.md`) and, on first run, `long_task.py` installs a `Stop` hook in `~/.claude/settings.json`. While `.agent/state.md` holds `status: active`, the Stop hook re-invokes Claude to continue Phase 2 orchestration — dispatching up to five parallel worktree subagents per milestone, verifying tests, merging, and running an architectural review — until Phase 3 runs the completion audit and sets `status: complete`. The hook is scoped to the project's working directory and bounded by a runaway counter (`LONG_TASK_MAX_STOP_CONTINUES`).

## Directory structure

```
skills/
├── code-review/                      # plugin (v2.2.0)
│   ├── .claude-plugin/plugin.json
│   ├── commands/                     # code-review, code-review-md, code-review-html, diff-viewer
│   ├── skills/
│   │   ├── code-review/              # main skill: workflow + shared assets
│   │   │   ├── SKILL.md
│   │   │   ├── references/           # review-criteria, common-vulnerabilities, python, javascript-typescript
│   │   │   ├── scripts/              # diff_stats.py, generate_html_report.py
│   │   │   └── assets/report-template.html
│   │   ├── code-review-md/SKILL.md
│   │   ├── code-review-html/SKILL.md
│   │   └── diff-viewer/              # standalone HTML diff viewer
│   │       ├── SKILL.md
│   │       ├── scripts/generate_diff_report.py
│   │       └── assets/diff-template.html
│   ├── README.md · README.ko.md
│   └── .snyk
├── doc-skill/                        # plugin (v0.1.0)
│   ├── .claude-plugin/plugin.json
│   ├── commands/gen-docs.md            # /gen-docs command → gen-docs skill
│   ├── skills/gen-docs/                # skill "gen-docs" — invoked as /gen-docs
│   │   ├── SKILL.md
│   │   └── templates/                # README.md.tmpl, README.ko.md.tmpl, ARCHITECTURE.md.tmpl, USAGE.md.tmpl
│   └── README.md · README.ko.md
├── git-skill/                        # plugin (v0.3.0)
│   ├── .claude-plugin/plugin.json
│   ├── commands/                     # six git-* commands
│   ├── skills/
│   │   ├── git-commit/               # SKILL.md + scripts/rewrite_msg.py (shared by the rewrite flow)
│   │   ├── git-commit-push/SKILL.md
│   │   ├── git-commit-rewrite/SKILL.md
│   │   ├── git-merge-to-main/SKILL.md
│   │   ├── git-merge-to-dev/SKILL.md
│   │   └── git-branch-cleanup/SKILL.md
│   └── README.md · README.ko.md
├── long-task/                        # plugin (v0.2.1)
│   ├── .claude-plugin/plugin.json
│   ├── commands/long-task.md         # /long-task
│   ├── skills/long-task/
│   │   ├── SKILL.md
│   │   ├── scripts/long_task.py      # lifecycle + Stop hook
│   │   └── references/               # completion-audit.md, project-templates.md
│   └── README.md · README.ko.md
├── .agents/skills/                   # flattened committed mirror of all 12 skills
├── samples/code-review/              # intentionally vulnerable demo fixtures (outside plugin artifacts)
├── tests/                            # pytest: package tests + diff_viewer/ unit tests + fixtures
├── docs/                             # design / planning notes
├── skills-lock.json                  # per-skill source, path, and content hash
├── VERSION                           # head.yymmdd.patch
├── LICENSE                           # MIT
├── README.md · README.ko.md
├── .snyk
└── .gitignore
```

## Design decisions

- **Portable `SKILL.md` is the unit of work.** Skill bodies avoid Claude-Code-only tools, so the same files run on other agent platforms. The Claude Code plugin wrapper (`.claude-plugin` + `commands` + `npx skills`) is additive, not required.
- **One plugin per workflow domain.** `code-review`, `doc-skill`, `git-skill`, and `long-task` are versioned and installable independently, so users adopt only what they need.
- **Shared logic centralized, variants kept thin.** The `code-review` skill owns the workflow, references, and scripts; the `-md`/`-html` variants add only an output format. `git-commit` owns `rewrite_msg.py` for the whole git family.
- **Sample vulnerabilities live outside the plugins.** Demo fixtures sit in repo-root `samples/` and are excluded via `.snyk`, so a published plugin neither ships exploitable code nor trips SAST scanners.
- **Self-contained stdlib Python.** Helper scripts import only the Python 3.10+ standard library, so there is no dependency install step.
- **Bounded autonomy for `long-task`.** Auto-continuation is gated on a per-directory `.agent/state.md` flag and a runaway cap (`LONG_TASK_MAX_STOP_CONTINUES`, default 500), so a runaway loop is contained and easy to pause.
- **Date-stamped versioning.** `VERSION` uses the `head.yymmdd.patch` scheme.
