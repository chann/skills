# skills — Architecture

## Overview

`skills` is a monorepo of [Claude Code](https://code.claude.com) skill plugins for everyday software-engineering workflows. It bundles seven independent plugins — `code-review`, `review-me`, `doc-skill`, `git-skill`, `handoff`, `long-task`, and `work-summary` — that together expose 20 canonical workflows through 21 installable Codex selectors.

Each skill is authored as a portable `SKILL.md` document, a Codex interface
descriptor at `agents/openai.yaml`, and optional `references/`, `templates/`,
`assets/`, and `scripts/`. A thin Claude Code wrapper
(`.claude-plugin/plugin.json` + `commands/*.md`) adds slash-command ergonomics
on top, while every Codex descriptor publishes a display name and `$name`
default prompt.

## Components

### Plugins

| Plugin | Version | Skills | Responsibility |
|---|---|---|---|
| `code-review` | 2.5.0 | `code-review`, `code-review-md`, `diff-summary`, `diff-summary-md`, `diff-summary-quiz`, `diff-viewer` | Explain changes across code and architecture; review diffs for defects; emit Markdown/HTML reports; render standalone raw HTML diffs |
| `review-me` | 0.1.0 | `review-me` | Review a plan, design, or consequential choice one decision at a time; recursively expand downstream decisions and audit every leaf before confirmation |
| `doc-skill` | 0.2.0 | `gen-docs` | Generate/update `README.md`, `README.ko.md`, `ARCHITECTURE.md`, `USAGE.md` while preserving hand-written prose |
| `git-skill` | 0.8.0 | `git-commit`, `git-commit-push`, `git-commit-push-realtime`, `gcpr` (selector alias), `git-commit-realtime`, `git-commit-rewrite`, `git-merge-to-main`, `git-merge-to-dev`, `git-branch-cleanup` | Conventional-Commit creation, one-shot or realtime checkpoint commits and pushes, history rewrite, guarded merges, and merged-branch cleanup |
| `handoff` | 0.2.0 | `gen-frontend-handoff`, `gen-backend-handoff` | Generate evidence-based continuation handoffs for frontend/client and backend/server developers from diffs, ranges, branch comparisons, and session context |
| `long-task` | 0.3.0 | `long-task` | Autonomously orchestrate multi-milestone projects with parallel worktree subagents, milestone reviews, and a Stop-hook auto-continue loop |
| `work-summary` | 0.1.0 | `work-summary` | Date-ranged Markdown work reports mined read-only from local coding-agent history stores (Claude Code, Codex, opencode, agy) |

### Skill internals

Every plugin shares the same layout:

```
<plugin>/
├── .claude-plugin/plugin.json   # name, version, description
├── commands/<command>.md        # one slash command per skill
└── skills/<skill>/
    ├── SKILL.md                 # the portable skill definition
    ├── agents/openai.yaml       # Codex display name, description, and $name prompt
    ├── references/              # optional knowledge the skill loads on demand
    ├── templates/               # optional output templates
    ├── assets/                  # optional static assets (e.g. HTML templates)
    └── scripts/                 # optional Python helpers (stdlib only)
```

- **`code-review`** centralizes defect analysis and the default Markdown + bilingual HTML output in the main `code-review` skill: the shared review workflow, four reference guides (`review-criteria`, `common-vulnerabilities`, `python`, `javascript-typescript`), and two scripts (`diff_stats.py`, `generate_html_report.py`). The `code-review-md` variant is a thin skill that reuses that workflow while stopping after the Markdown artifact. `diff-summary` is the canonical authoring source — `collect_diff_evidence.py` owns the hardened Git/GitHub boundary, its `SKILL.md` owns aligned Korean/English analysis, and `generate_summary_report.py` plus `summary-template.html` validate and merge the two Markdown sources into interactive offline HTML. For exact-selector installation, `diff-summary-md` and `diff-summary-quiz` each bundle a synchronized workflow reference, collector, generator, and template: the first invokes bilingual `--markdown-only` (no HTML, no browser open), and the second appends aligned validated `## Quiz` sections rendered as interactive multiple-choice quizzes. `diff-viewer` is also standalone — `generate_diff_report.py` plus `diff-template.html` — and displays the raw patch without analysis behind the same bilingual interface, localizing only its chrome because the diff body is code. The three canonical templates deliberately duplicate the shared design tokens, icon geometry, and accessibility shell so each skill stays independently installable; `tests/test_html_report_style_contract.py` is what keeps those copies identical rather than a runtime import.
- **`review-me`** is a user-invoked, read-only decision-tree interview. Its `SKILL.md` owns the dependency-ordered frontier, single-question loop, recursive child expansion, descendant reopening, five leaf-closure tests, and final confirmation. `references/review-lenses.md` is the disclosed audit checklist loaded before the first substantive question, so the execution steps stay legible while every applicable product, system, human-interface, security, operational, and evolution consequence is accounted for.
- **`git-skill`** keeps its single Python helper, `rewrite_msg.py`, under `git-commit/scripts/`; the `git-commit-rewrite` workflow shares it. `git-commit-push-realtime` composes the `git-commit` and `git-commit-push` safety contracts with outcome-based checkpoint planning, per-checkpoint verification, immediate ordinary pushes, and upstream-parity proof. `git-commit-realtime` applies the same checkpoint planning and verification while never touching the remote: it composes the `git-commit` contract alone and reports unpushed checkpoint hashes instead of push parity.
- **`handoff`** keeps both handoff generators as self-contained `SKILL.md` files. `gen-frontend-handoff` focuses on client-visible API contract changes, type/rendering/error-state work, and `client action 없음` for DB-only changes. `gen-backend-handoff` focuses on API contracts, database migrations, jobs/queues, rollout, verification, and backend continuation prompts.
- **`long-task`** carries `long_task.py` (lifecycle commands + Stop-hook installer) and two references (`completion-audit`, `project-templates`).
- **`work-summary`** is a read-only reporter over local agent history. Its `SKILL.md` owns the date-range grammar, local-timezone bucketing, store mining order, and the summary/detailed report contract; `references/agent-history-stores.md` maps each store's paths, record shapes, timestamp fields, and epoch units so the workflow filters records instead of guessing.
- **`doc-skill`** carries four output templates under `gen-docs/templates/`.

### Supporting files

- **`.agents/skills/`** — optional local flattened mirror of skill directories for platforms that load skills from a single flat folder (e.g. Codex's `~/.agents/skills/`).
- **`samples/code-review/`** — intentionally vulnerable fixtures (`go-api`, `python-auth`, `react-dashboard`) used to demo the reviewer. Kept outside the plugin folders so they never ship in a published plugin.
- **`tests/`** — unittest/pytest suite: per-plugin package tests plus parser, renderer, CLI, interaction-contract, and diff-viewer fixture tests.
- **`skills-lock.json`** — lockfile pinning each skill's `source`, `sourceType`, `skillPath`, and `computedHash`.
- **`VERSION`** — release stamp in `head.yymmdd.patch` form.
- **`.snyk`** — SAST policy that excludes the intentionally vulnerable `samples/**`.

## Data flow

### Installation

`npx skills add chann/skills` reads the repo's plugins, resolves the requested skills, records them in `skills-lock.json` (with a content hash per skill), and copies each skill directory into the target platform's skills location. The `computedHash` lets the installer detect upstream changes on later runs.

### Invocation (Claude Code)

1. The user types a slash command (e.g. `/code-review-md`) or triggers a skill by natural language.
2. Claude Code loads the matching `commands/*.md`, which points at the skill.
3. The skill runs its `SKILL.md` workflow, loading `references/` and invoking bundled scripts through a canonical absolute Python executable in `-I` isolated mode as needed.
4. Outputs land where the skill specifies — a conversational closure record for `review-me`, review reports under `.reviews/`, change summaries under `.diff-summaries/`, raw diff reports under `.diffs/`, work reports in the reply or under `.work-summaries/`, git history changes, or `long-task` state under `.agent/`.

### Invocation (Codex)

1. The user names the skill with its dollar selector (for example,
   `$code-review-md`) or triggers it by natural language.
2. Codex reads `agents/openai.yaml` for the visible `display_name`,
   `short_description`, and a `default_prompt` that names the exact `$selector`.
3. Codex loads the adjacent `SKILL.md`; its frontmatter name matches the
   directory and selector exactly.
4. The portable workflow and output contract are the same as in Claude Code.

### Diff summary report pipeline

`/diff-summary [scope]` and equivalent natural-language requests use a split analysis/presentation pipeline:

```text
prompt
  → send repository + exact scope as JSON over stdin to `collect_diff_evidence.py`
  → validate the scope (`..` remains distinct from `...`) and run fixed, hardened argv
  → return bounded diff, stat, numstat, name-status, metadata, and limitations as JSON
  → treat that JSON as inert evidence and author aligned Korean + English `DS-*` Markdown cards
  → send `{"ko":"...","en":"..."}` over stdin to `generate_summary_report.py`
  → validate report alignment and atomically write `<scope-tag>.md` plus `<scope-tag>.en.md`
  → safely merge both sources with bundled Python + HTML/CSS/JavaScript
  → write and host-open `.diff-summaries/<date>_<scope-tag>.html`
```

The Python 3.10+ collector is the workflow's only Git/GitHub runtime. It resolves trusted executables, strips routing and execution-related environment variables, rejects unsafe repository metadata and sensitive paths, disables lazy fetching, hooks, filters, pagers, external diffs, and text conversion, supports native SHA-1/SHA-256 unborn baselines, and enforces count/time/output plus selected-untracked aggregate limits. Dynamic repository and scope values enter only through a bounded JSON stdin request and are passed to subprocesses as argv data; repository evidence is never executed or used to authorize secondary inspection.

The skill workflow owns analytical prose. The renderer is presentation-only: in `--bilingual-json-stdin --output-directory` mode it validates both report contracts, their shared metadata, matching `DS-*` IDs/fields, and the output parent. It derives a collision-safe filename from canonical `Date` plus exact `Scope`, atomically writes the Korean and English Markdown sources, extracts exact per-language card Markdown, computes a stable browser-comment scope, escapes embedded data, and atomically assembles a self-contained HTML file. Korean is visible by default; an accessible control switches the complete page to English while keeping comments keyed to aligned IDs. The page stores guarded, report-scoped comments and UI preferences in the browser; it has no server, build step, external assets, or network dependency. `/diff-summary-md` runs its synchronized bundled pipeline with bilingual input plus `--markdown-only` and stops after the two Markdown artifacts; `/diff-summary-quiz` runs its synchronized bundled pipeline and appends aligned validated `## Quiz` sections (`QZ-*` questions with matching answer positions) that the renderer turns into interactive multiple-choice quizzes in the same offline page. The legacy `--markdown-stdin` path remains for explicitly requested single-language output.

This boundary keeps three intents independent: `diff-summary` explains changes without review severity, `code-review` identifies defects and recommends fixes, and `diff-viewer` displays the raw patch. A combined summary-and-review request runs both analytical workflows and keeps their outputs distinct.

### long-task autonomy loop

`/long-task` Phase 1 writes the working-memory files under `.agent/` (`goal.md`, `plans.md`, `standards.md`, `implement.md`, `progress.md`, `state.md`) and, on first run, `long_task.py` installs a `Stop` hook in `~/.claude/settings.json`. While `.agent/state.md` holds `status: active`, the Stop hook re-invokes Claude to continue Phase 2 orchestration — dispatching up to five parallel worktree subagents per milestone, verifying tests, merging, and running an architectural review — until Phase 3 runs the completion audit and sets `status: complete`. The hook is scoped to the project's working directory and bounded by a runaway counter (`LONG_TASK_MAX_STOP_CONTINUES`).

## Directory structure

```
skills/
├── code-review/                      # plugin (v2.5.0)
│   ├── .claude-plugin/plugin.json
│   ├── commands/                     # code-review, code-review-md, diff-summary, diff-summary-md, diff-summary-quiz, diff-viewer
│   ├── skills/
│   │   ├── code-review/              # main skill: workflow + shared assets
│   │   │   ├── SKILL.md
│   │   │   ├── references/           # review-criteria, common-vulnerabilities, python, javascript-typescript
│   │   │   ├── scripts/              # diff_stats.py, generate_html_report.py
│   │   │   └── assets/report-template.html
│   │   ├── code-review-md/SKILL.md
│   │   ├── diff-summary/             # hardened evidence + explanatory offline report
│   │   │   ├── SKILL.md
│   │   │   ├── agents/openai.yaml
│   │   │   ├── scripts/              # collect_diff_evidence.py, generate_summary_report.py
│   │   │   └── assets/summary-template.html
│   │   ├── diff-summary-md/          # standalone Markdown-only package
│   │   │   ├── SKILL.md
│   │   │   ├── references/diff-summary-workflow.md
│   │   │   ├── scripts/
│   │   │   │   ├── collect_diff_evidence.py
│   │   │   │   └── generate_summary_report.py
│   │   │   └── assets/summary-template.html
│   │   ├── diff-summary-quiz/        # standalone comprehension-quiz package
│   │   │   ├── SKILL.md
│   │   │   ├── references/diff-summary-workflow.md
│   │   │   ├── scripts/
│   │   │   │   ├── collect_diff_evidence.py
│   │   │   │   └── generate_summary_report.py
│   │   │   └── assets/summary-template.html
│   │   └── diff-viewer/              # standalone HTML diff viewer
│   │       ├── SKILL.md
│   │       ├── scripts/generate_diff_report.py
│   │       └── assets/diff-template.html
│   ├── README.md · README.ko.md
│   └── .snyk
├── doc-skill/                        # plugin (v0.2.0)
│   ├── .claude-plugin/plugin.json
│   ├── commands/gen-docs.md            # /gen-docs command → gen-docs skill
│   ├── skills/gen-docs/                # skill "gen-docs" — invoked as /gen-docs
│   │   ├── SKILL.md
│   │   └── templates/                # README.md.tmpl, README.ko.md.tmpl, ARCHITECTURE.md.tmpl, USAGE.md.tmpl
│   └── README.md · README.ko.md
├── review-me/                        # plugin (v0.1.0)
│   ├── .claude-plugin/plugin.json
│   ├── commands/review-me.md         # /review-me
│   ├── skills/review-me/
│   │   ├── SKILL.md                  # decision frontier + leaf closure
│   │   ├── agents/openai.yaml
│   │   ├── evals/evals.json
│   │   └── references/review-lenses.md
│   └── README.md · README.ko.md
├── git-skill/                        # plugin (v0.8.0)
│   ├── .claude-plugin/plugin.json
│   ├── commands/                     # eight git-* commands + the /gcpr and /gcr aliases
│   ├── skills/
│   │   ├── git-commit/               # SKILL.md + scripts/rewrite_msg.py (shared by the rewrite flow)
│   │   ├── git-commit-push/SKILL.md
│   │   ├── git-commit-push-realtime/  # SKILL.md + agents/openai.yaml + evals
│   │   ├── gcpr/                      # thin Codex selector alias + agents/openai.yaml
│   │   ├── git-commit-realtime/       # SKILL.md + agents/openai.yaml + evals
│   │   ├── git-commit-rewrite/SKILL.md
│   │   ├── git-merge-to-main/SKILL.md
│   │   ├── git-merge-to-dev/SKILL.md
│   │   └── git-branch-cleanup/SKILL.md
│   └── README.md · README.ko.md
├── handoff/                          # plugin (v0.2.0)
│   ├── .claude-plugin/plugin.json
│   ├── commands/                     # gen-frontend-handoff, gen-backend-handoff
│   ├── skills/
│   │   ├── gen-frontend-handoff/SKILL.md
│   │   └── gen-backend-handoff/SKILL.md
│   └── README.md · README.ko.md
├── long-task/                        # plugin (v0.3.0)
│   ├── .claude-plugin/plugin.json
│   ├── commands/long-task.md         # /long-task
│   ├── skills/long-task/
│   │   ├── SKILL.md
│   │   ├── scripts/long_task.py      # lifecycle + Stop hook
│   │   └── references/               # completion-audit.md, project-templates.md
│   └── README.md · README.ko.md
├── work-summary/                     # plugin (v0.1.0)
│   ├── .claude-plugin/plugin.json
│   ├── commands/work-summary.md      # /work-summary
│   ├── skills/work-summary/
│   │   ├── SKILL.md                  # date-range grammar + report contract
│   │   ├── agents/openai.yaml
│   │   ├── evals/evals.json
│   │   └── references/agent-history-stores.md
│   └── README.md · README.ko.md
├── .agents/skills/                   # optional local flat skill mirror
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
- **One plugin per workflow domain.** `code-review`, `review-me`, `doc-skill`, `git-skill`, `handoff`, `long-task`, and `work-summary` are versioned and installable independently, so users adopt only what they need.
- **Work reporting is read-only and local.** `work-summary` mines the machine's own agent history stores, never mutates them, keeps history content off the network, and leaves generated reports out of version control (`.work-summaries/` is ignored here).
- **Leaf-complete decision review is distinct from code review.** `review-me` resolves plans, designs, and choices conversationally; `code-review` evaluates concrete Git changes for defects. The former stays user-invoked and read-only through confirmation, while the latter may trigger naturally from a diff-review request and writes reports.
- **Canonical logic with installable variants.** The `code-review` skill owns the workflow, references, and scripts; its `-md`/`-html` variants stay thin because they are installed with that plugin contract. `diff-summary` is the canonical authoring source, while `diff-summary-md` and `diff-summary-quiz` carry synchronized standalone copies of the workflow reference and runtime so each exact selector works by itself; package tests enforce byte parity. `git-commit` owns shared commit semantics and `rewrite_msg.py`; `git-commit-push-realtime` references that canonical workflow plus `git-commit-push` instead of duplicating their safety policy, `gcpr` only loads that canonical workflow as a Codex selector alias, and `git-commit-realtime` references the `git-commit` contract alone for local-only checkpoints.
- **Platform names are explicit and paired.** Every skill directory name matches
  its `SKILL.md` frontmatter name, every Claude Code command wrapper uses
  `/name`, and every `agents/openai.yaml` publishes a Codex display name plus a
  `$name` default prompt. Package tests enforce all three surfaces. Short
  Claude Code aliases are additive command wrappers: `commands/gcpr.md` and
  `commands/gcr.md` republish `/git-commit-push-realtime` as `/gcpr` and
  `/git-commit-realtime` as `/gcr` with byte-identical bodies. Codex has no
  alias metadata, so `skills/gcpr/` is a thin, installable selector package that
  loads the canonical workflow before any Git action. It adds `$gcpr` without
  duplicating policy or adding a second catalog workflow; `$gcr` remains a
  natural-language trigger advertised by the canonical skill, not a selector.
- **Evidence, analysis, and presentation are separate boundaries.** `collect_diff_evidence.py` is the only Git/GitHub runtime and emits bounded JSON; `diff-summary/SKILL.md` treats it as inert evidence and authors the Markdown contract; the bundled renderer never invokes Git or invents analytical prose. This keeps the exact scope and verified/unverified boundary visible in the source report.
- **Generated reports stay local.** `.reviews/`, `.diff-summaries/`, and `.diffs/` are ignored in this repository. Skills may suggest an ignore entry in target repositories, but do not mutate their `.gitignore` automatically.
- **Sample vulnerabilities live outside the plugins.** Demo fixtures sit in repo-root `samples/` and are excluded via `.snyk`, so a published plugin neither ships exploitable code nor trips SAST scanners.
- **Self-contained stdlib Python.** Helper scripts, including the `diff-summary` collector and parser/renderer, import only the Python 3.10+ standard library, so there is no dependency install step.
- **Bounded autonomy for `long-task`.** Auto-continuation is gated on a per-directory `.agent/state.md` flag and a runaway cap (`LONG_TASK_MAX_STOP_CONTINUES`, default 500), so a runaway loop is contained and easy to pause.
- **Date-stamped versioning.** `VERSION` uses the `head.yymmdd.patch` scheme.
