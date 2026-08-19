# skills — Architecture

## Overview

`skills` is a monorepo of [Claude Code](https://code.claude.com) skill plugins for everyday software-engineering workflows. It bundles 13 independent plugins — `code-review`, `review-me`, `bug-hunt`, `research-brief`, `doc-skill`, `git-skill`, `handoff`, `long-task`, `build-reinstall`, `work-summary`, `plan-summary`, `human-friendly-writing`, and `skill-forge` — that together expose 30 canonical workflows through 31 installable Codex selectors.

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
| `bug-hunt` | 0.1.0 | `bug-hunt` | Diagnose a broken behavior against a written falsification ledger — reproduce first, one variable per round, widen after three failures in a layer, pin the fix with a failing-first check, and persist the record under `.bug-hunts/` |
| `research-brief` | 0.1.0 | `research-brief` | Answer a technical question from primary sources and persist a cited brief under `.research/` — tiered sources, version-pinned claims, a contradiction ledger, and mandatory open questions |
| `doc-skill` | 0.2.0 | `gen-docs` | Generate/update `README.md`, `README.ko.md`, `ARCHITECTURE.md`, `USAGE.md` while preserving hand-written prose |
| `git-skill` | 0.9.0 | `git-commit`, `git-commit-push`, `git-commit-push-realtime`, `gcpr` (selector alias), `git-commit-realtime`, `git-commit-rewrite`, `git-merge-to-main`, `git-merge-to-dev`, `git-branch-cleanup`, `git-resolve-conflicts` | Conventional-Commit creation, one-shot or realtime checkpoint commits and pushes, history rewrite, guarded merges, conflict resolution, and merged-branch cleanup |
| `handoff` | 0.2.0 | `gen-frontend-handoff`, `gen-backend-handoff` | Generate evidence-based continuation handoffs for frontend/client and backend/server developers from diffs, ranges, branch comparisons, and session context |
| `long-task` | 0.3.0 | `long-task` | Autonomously orchestrate multi-milestone projects with parallel worktree subagents, milestone reviews, and a Stop-hook auto-continue loop |
| `build-reinstall` | 0.1.0 | `build-reinstall` | Build a project with project-owned commands, reinstall its local result, and verify the installed copy with smoke checks and artifact digests |
| `work-summary` | 0.1.0 | `work-summary` | Daily, weekly, monthly, quarterly, yearly, or custom Markdown work reports mined read-only from local coding-agent history stores |
| `plan-summary` | 1.0.0 | `plan-summary`, `plan-summary-md`, `plan-summary-quiz` | Summarize explicit plan, PRD, specification, and design files as aligned Korean/English Markdown with optional interactive HTML quizzes |
| `human-friendly-writing` | 0.1.0 | `human-friendly-writing` | Rewrite AI-written Korean text into natural, human-sounding prose — slop-term lexicon plus style pass, meaning-preserving |
| `skill-forge` | 0.1.0 | `skill-forge`, `skill-audit` | Author skill packages against the nine-rule skill contract and audit every packaged skill against it, from frontmatter and Codex descriptor through catalog, locales, and published counts |

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
- **`git-skill`** keeps its single Python helper, `rewrite_msg.py`, under `git-commit/scripts/`; the `git-commit-rewrite` workflow shares it. `git-commit-push-realtime` composes the `git-commit` and `git-commit-push` safety contracts with outcome-based checkpoint planning, per-checkpoint verification, immediate ordinary pushes, and upstream-parity proof. `git-commit-realtime` applies the same checkpoint planning and verification while never touching the remote: it composes the `git-commit` contract alone and reports unpushed checkpoint hashes instead of push parity. `git-resolve-conflicts` finishes an in-progress merge, rebase, cherry-pick, or revert instead of abandoning it: its `SKILL.md` owns operation identification including the rebase label inversion, the `--diff-filter=U` inventory read under `--conflict=zdiff3`, a per-class resolution policy that regenerates lockfiles and generated files rather than hand-merging them and resolves a submodule from its own log, intent recovery from both sides' history before a hunk is touched, the resolution ledger recording which intent survived each hunk, and the refusal to run `--abort`, `--skip`, or any push.
- **`handoff`** keeps both handoff generators as self-contained `SKILL.md` files. `gen-frontend-handoff` focuses on client-visible API contract changes, type/rendering/error-state work, and `client action 없음` for DB-only changes. `gen-backend-handoff` focuses on API contracts, database migrations, jobs/queues, rollout, verification, and backend continuation prompts.
- **`long-task`** carries `long_task.py` (lifecycle commands + Stop-hook installer) and two references (`completion-audit`, `project-templates`).
- **`build-reinstall`** is an explicit-only local installation workflow. Its `SKILL.md` resolves project-owned build, reinstall, and verification commands, requires build success before changing the installed target, and separates unavailable runtime proof from checks that passed. `references/build-reinstall.example.yaml` documents optional version 1 configuration with explicit target paths and built/installed SHA-256 pairs.
- **`work-summary`** is a read-only reporter over local agent history. Its `SKILL.md` owns the date-range grammar, local-timezone bucketing, period-classified save paths, store mining order, summary/detailed report contract, and self-contained Korean prose fallback; `references/agent-history-stores.md` maps each store's paths, record shapes, timestamp fields, and epoch units so the workflow filters records instead of guessing.
- **`plan-summary`** owns the explicit-file boundary and evidence-first document workflow. `collect_plan_evidence.py` returns ordered UTF-8 contents and SHA-256 identities from a bounded JSON request; `generate_plan_summary.py` validates aligned `PS-*` and optional `QZ-*` contracts, derives collision-safe names, and assembles offline HTML from `summary-template.html`. `plan-summary-md` and `plan-summary-quiz` bundle byte-synchronized workflow, natural-Korean fallback, and runtime copies so exact-selector installs remain executable.
- **`doc-skill`** carries four output templates under `gen-docs/templates/` and keeps its natural-Korean fallback inside `gen-docs` rather than depending on another package.
- **`bug-hunt`** is a stateful diagnosis loop rather than debugging advice. Its `SKILL.md` owns the defect statement, the reproduce-before-editing gate, the four-column hypothesis ledger (hypothesis, falsified-if, observed, verdict), the widening rule that forbids a fourth hypothesis in a layer that produced three falsified ones, the failing-first check gate, the `BUGHUNT` marker whose removal is proven by search, and the closing record with its kept falsified list. `references/instrumentation-playbook.md` carries the probe-selection ladder, per-ecosystem probe spellings, the intermittent-failure loop, bisection over commits, inputs, and configuration, and the measure-before-hypothesizing rule for performance work.
- **`research-brief`** makes provenance a structural requirement rather than a habit. Its `SKILL.md` owns the question-sharpening step, optional background-agent delegation seeded with the format rather than a topic, the T1/T2/T3 source tiers with the rule that a T3 claim is a lead and never an answer, per-claim version or date pinning, the contradiction ledger that keeps both sides with the resolution and its reason, and the answer-first document shape whose open-questions section is mandatory even when empty.
- **`skill-forge`** owns the repository's skill contract. `skills/skill-forge/references/skill-package-contract.md` states rules C1 through C9 — name parity, description grammar, invocation-mode declaration, Codex descriptor, slash command, evals, catalog and locale parity, plugin manifest, and published counts — and `references/description-grammar.md` explains how a description earns reliable invocation. `skill-audit` carries the executable form, `scripts/audit_skills.py`: a stdlib-only walker over `*/skills/*/SKILL.md` that reports each violation as rule, skill, detail, and file, emits text, JSON, or Markdown, and exits non-zero so it works as a merge gate. `tests/test_skill_contract.py` runs it over this repository, which is why a half-published skill fails the suite rather than shipping.
- **`human-friendly-writing`** rewrites AI-written Korean prose without moving meaning. Its `SKILL.md` owns the hard preservation rules, the three-part judgment test for unlisted slop terms, and the ban on leaked method vocabulary; `references/slop-lexicon.md` carries the replaceable-term tables plus the keep list of established technical terms, and `references/style-rules.md` carries the translation-ese/rhythm/tone pass with the final self-check checklist.

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
4. Outputs land where the skill specifies — a conversational closure record for `review-me`, review reports under `.reviews/`, change summaries under `.diff-summaries/`, plan summaries under `.plan-summaries/`, raw diff reports under `.diffs/`, work reports in the reply or under `.work-summaries/`, a verified local install from `build-reinstall`, git history changes, or `long-task` state under `.agent/`.

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

### Plan summary report pipeline

Claude Code `/plan-summary`, `/plan-summary-md`, and `/plan-summary-quiz` map directly to Codex `$plan-summary`, `$plan-summary-md`, and `$plan-summary-quiz`.

```text
explicit .md/.markdown/.txt paths
  → send ordered paths as bounded JSON stdin to `collect_plan_evidence.py`
  → reject directories, symlinks, duplicates, binary/invalid UTF-8, and size violations
  → return exact contents, paths, sizes, and SHA-256 digests as inert JSON
  → author one evidence map and aligned Korean/English `PS-*` Markdown cards
  → optionally append aligned final `QZ-*` quiz questions
  → send `{"ko":"...","en":"..."}` to `generate_plan_summary.py`
  → validate metadata, source references, IDs, categories, and bilingual alignment
  → atomically write `.plan-summaries/<date>_<source-tag>.*`
```

The collector is the only source-document reader and never discovers files. Paths and contents cannot authorize commands, network access, edits, or additional reads. The generator owns filenames and rejects a symlinked output parent or any existing artifact. `plan-summary` writes Korean Markdown, English Markdown, and self-contained bilingual HTML; `plan-summary-md` adds `--markdown-only`; `plan-summary-quiz` validates matching option counts and answer indexes before rendering one-shot accessible controls and a print answer key. Python 3.10+ standard library code is copied into each exact selector so installed runtime paths remain local to that selector.

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
│   │   ├── git-branch-cleanup/SKILL.md
│   │   └── git-resolve-conflicts/SKILL.md
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
├── build-reinstall/                  # plugin (v0.1.0)
│   ├── .claude-plugin/plugin.json
│   ├── commands/build-reinstall.md   # /build-reinstall
│   ├── skills/build-reinstall/
│   │   ├── SKILL.md                  # build → reinstall → installed proof
│   │   ├── agents/openai.yaml
│   │   └── references/build-reinstall.example.yaml
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
├── plan-summary/                     # plugin (v1.0.0)
│   ├── .claude-plugin/plugin.json
│   ├── commands/                     # plan-summary, plan-summary-md, plan-summary-quiz
│   ├── skills/
│   │   ├── plan-summary/             # authoritative workflow + collector + generator + HTML
│   │   ├── plan-summary-md/          # standalone Markdown-only synchronized package
│   │   └── plan-summary-quiz/        # standalone quiz synchronized package
│   └── README.md · README.ko.md
├── human-friendly-writing/           # plugin (v0.1.0)
│   ├── .claude-plugin/plugin.json
│   ├── commands/human-friendly-writing.md
│   ├── skills/human-friendly-writing/
│   │   ├── SKILL.md                  # de-jargon + style pass, meaning-preserving
│   │   ├── agents/openai.yaml
│   │   └── references/               # slop-lexicon.md, style-rules.md
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
- **One plugin per workflow domain.** `code-review`, `review-me`, `doc-skill`, `git-skill`, `handoff`, `long-task`, `build-reinstall`, `work-summary`, `plan-summary`, and `human-friendly-writing` are versioned and installable independently, so users adopt only what they need.
- **Local reinstall is explicit and evidence-based.** `build-reinstall` never runs as a completion hook. It chooses commands from optional versioned YAML or project-owned instructions, stops before installation when the build or target is unresolved, and reports success only after installed-result verification.
- **Natural prose is an optional enhancement, not a dependency.** Document-generating selectors carry a compact built-in Korean writing contract. They may use `human-friendly-writing` when the runtime already exposes it, but never install, fetch, or require it; missing support cannot block or reduce output.
- **Work reporting is read-only and local.** `work-summary` mines the machine's own agent history stores, never mutates them, keeps history content off the network, and leaves generated reports out of version control (`.work-summaries/` is ignored here).
- **Leaf-complete decision review is distinct from code review.** `review-me` resolves plans, designs, and choices conversationally; `code-review` evaluates concrete Git changes for defects. The former stays user-invoked and read-only through confirmation, while the latter may trigger naturally from a diff-review request and writes reports.
- **Canonical logic with installable variants.** The `code-review` skill owns the workflow, references, and scripts; its `-md`/`-html` variants stay thin because they are installed with that plugin contract. `diff-summary` is the canonical authoring source, while `diff-summary-md` and `diff-summary-quiz` carry synchronized standalone copies of the workflow reference and runtime. `plan-summary` uses the same release discipline: `plan-summary-md` and `plan-summary-quiz` carry byte-synchronized standalone workflow and runtime copies. Package tests enforce parity for both families. `git-commit` owns shared commit semantics and `rewrite_msg.py`; `git-commit-push-realtime` references that canonical workflow plus `git-commit-push` instead of duplicating their safety policy, `gcpr` only loads that canonical workflow as a Codex selector alias, and `git-commit-realtime` references the `git-commit` contract alone for local-only checkpoints.
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
- **Generated reports stay local.** `.reviews/`, `.diff-summaries/`, `.plan-summaries/`, and `.diffs/` are ignored in this repository. Skills may suggest an ignore entry in target repositories, but do not mutate their `.gitignore` automatically.
- **Sample vulnerabilities live outside the plugins.** Demo fixtures sit in repo-root `samples/` and are excluded via `.snyk`, so a published plugin neither ships exploitable code nor trips SAST scanners.
- **Self-contained stdlib Python.** Helper scripts, including the `diff-summary` and `plan-summary` collectors and parser/renderers, import only the Python 3.10+ standard library, so there is no dependency install step.
- **Bounded autonomy for `long-task`.** Auto-continuation is gated on a per-directory `.agent/state.md` flag and a runaway cap (`LONG_TASK_MAX_STOP_CONTINUES`, default 500), so a runaway loop is contained and easy to pause.
- **Date-stamped versioning.** `VERSION` uses the `head.yymmdd.patch` scheme.
