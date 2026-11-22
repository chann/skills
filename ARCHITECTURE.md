# skills — Architecture

## Overview

`skills` is a monorepo of [Claude Code](https://code.claude.com) skill plugins for everyday software-engineering workflows. It bundles 19 independent plugins — `chann-mode`, `understand`, `research-brief`, `recall`, `diff-summary`, `plan-summary`, `review-me`, `swarm`, `bug-hunt`, `doc-skill`, `unslop`, `no-comments`, `make-bot-ui`, `build-reinstall`, `interrogate`, `git-skill`, `long-task`, `handoff`, and `skill-forge` — that together expose 29 canonical workflows through 33 installable Codex selectors. The four extra selectors are the aliases `gcr`, `gcpr`, `gcprm`, and `gcpd`.

Each skill is authored as a portable `SKILL.md` document, a Codex interface
descriptor at `agents/openai.yaml`, and optional `references/`, `templates/`,
`assets/`, and `scripts/`. A thin Claude Code wrapper
(`.claude-plugin/plugin.json` + `commands/*.md`) adds slash-command ergonomics
on top, while every Codex descriptor publishes a display name and `$name`
default prompt.

The catalog is organized in eight stages, the same grouping the website uses: mode, understand, design, build, verify, ship, delegate, and meta. `chann` is the single entry point; every other skill is situational and can be called directly.

## Components

### Plugins

| Plugin | Version | Skills | Responsibility |
|---|---|---|---|
| `chann-mode` | 0.4.0 | `chann` | The one entry point: restate the goal and the smallest change, match one of 22 playbooks, route each step to the skill that owns it when installed, apply named principles, and reply with labelled evidence |
| `understand` | 0.1.0 | `how`, `why` | Read-only answers about a codebase, split by source of truth: `how` from the code with `file:line` citations, `why` from the commit, pull-request, and issue record, with inference and gaps labelled |
| `research-brief` | 0.1.0 | `research-brief` | Answer a technical question from primary sources and persist a cited brief under `.research/` — tiered sources, version-pinned claims, a contradiction ledger, and mandatory open questions |
| `recall` | 2.0.0 | `recall`, `catchup` | `recall` mines Claude Code, Codex, opencode, and agy history read-only into a date-ranged report or a topic brief for resuming work; `catchup` tells you what moved in this conversation after your last message |
| `diff-summary` | 3.0.0 | `diff-summary`, `diff-viewer` | Evidence-based change summaries as aligned Korean/English Markdown and interactive HTML (`--md`, `--quiz`), plus a standalone raw diff viewer |
| `plan-summary` | 2.0.0 | `plan-summary` | Summarize explicit plan, PRD, specification, and design files as aligned Korean/English Markdown and HTML (`--md`, `--quiz`) |
| `review-me` | 0.1.1 | `review-me` | Review a plan, design, or consequential choice one decision at a time; recursively expand downstream decisions and audit every leaf before confirmation |
| `swarm` | 1.0.0 | `swarm`, `arena` | `swarm` fans work out to subagents or other installed coding agents with a recorded route rationale and a call-tree report; `arena` runs competing attempts at one artifact and grafts the best parts onto one base |
| `bug-hunt` | 0.1.1 | `bug-hunt` | Diagnose a broken behavior against a written falsification ledger — reproduce first, one variable per round, widen after three failures in a layer, pin the fix with a failing-first check, and persist the record under `.bug-hunts/` |
| `doc-skill` | 0.2.1 | `gen-docs` | Generate/update `README.md`, `README.ko.md`, `ARCHITECTURE.md`, `USAGE.md` while preserving hand-written prose |
| `unslop` | 1.0.0 | `unslop` | Rewrite AI-written Korean or English text into natural, human-sounding prose — lexicon and style passes, meaning-preserving |
| `no-comments` | 0.1.0 | `no-comments` | Remove comments that only narrate the code. A general subagent runs the shipped reviewer prompt, accepted findings are applied, and a comment about an outside rule that cannot be checked is kept and marked for review |
| `make-bot-ui` | 0.1.0 | `make-bot-ui` | Build a page whose controls wake a bot through a webhook the user supplies. The sender key stays in server-side config, and the local server sends the POST |
| `build-reinstall` | 0.1.0 | `build-reinstall` | Build a project with project-owned commands, reinstall its local result, and verify the installed copy with smoke checks and artifact digests |
| `interrogate` | 3.0.0 | `interrogate`, `blast-radius` | Adversarial review that grades every finding on a proof ladder and writes Markdown plus bilingual HTML under `.reviews/`, and a blast-radius check that proves what a change could break outside the diff |
| `git-skill` | 1.1.0 | `git-commit`, `gcr`, `gcpr`, `gcprm`, `gcpd`, `git-merge`, `git-resolve-conflicts`, `git-cleanup` | One commit workflow with once, push, realtime, push realtime, push realtime merge-main, deploy, and rewrite modes; guarded merges into `main`, `dev`, or any local branch; conflict resolution; cleanup of merged branches and finished worktrees |
| `long-task` | 0.3.0 | `long-task` | Autonomously orchestrate multi-milestone projects with parallel worktree subagents, milestone reviews, and a Stop-hook auto-continue loop |
| `handoff` | 1.0.0 | `handoff` | One handoff skill with an audience argument: frontend/client and backend/server handoffs from diffs, ranges, and branch comparisons, plus session-to-session handoffs that separate proven state from unproven |
| `skill-forge` | 0.2.0 | `skill-forge`, `skill-audit`, `reflect` | Author skill packages against the nine-rule skill contract, audit every packaged skill against it, and turn lessons from a session or repository into enforcement |

### Skill internals

Every plugin shares the same layout:

```
<plugin>/
├── .claude-plugin/plugin.json   # name, version, description
├── commands/<command>.md        # one slash command per skill
└── skills/<skill>/
    ├── SKILL.md                 # the portable skill definition
    ├── agents/openai.yaml       # Codex display name, description, and $name prompt
    ├── evals/evals.json         # happy path, a boundary or refusal, a sibling-skill case
    ├── references/              # optional knowledge the skill loads on demand
    ├── templates/               # optional output templates
    ├── assets/                  # optional static assets (e.g. HTML templates)
    └── scripts/                 # optional Python helpers (stdlib only)
```

- **`chann-mode`** holds one router skill, `chann`, with data around it. `SKILL.md` owns the first move, the routing table, the index of principles, the autonomy rules, delegation, the evidence vocabulary, and the reply contract. `playbooks/<name>.md` holds the [22 playbooks](chann-mode/README.md#playbooks) shared by both hosts. Each file carries numbered steps and names any catalog skill that can handle a step. `references/principles.md` states twenty-seven principles, each with the test that tells whether it applies, and `references/decision-trail.md` defines the log for long or unattended runs. `worker.md` is the first file every delegate reads. The router requires explicit invocation in Claude Code via frontmatter and in Codex via `agents/openai.yaml`.
- **`understand`** holds two read-only skills with no scripts. `how` answers in a fixed five-part shape (overview, key concepts, runtime flow, a `file:line` map, gotchas) and labels anything unread `inferred`. `why` reads git history, blame, pull-request and issue discussion, and design notes through `git` and, when available, `gh`, and answers with a decision timeline whose rows each carry a commit or PR and a date.
- **`recall`** carries two skills. `recall` is a read-only reporter over local agent history. Its `SKILL.md` owns the mode choice between a report and a brief, the date-range grammar, local-timezone bucketing, period-classified save paths, store mining order, the summary/detailed report contract, the brief's scope lock and status tags, and a self-contained Korean prose fallback; `references/agent-history-stores.md` maps each store's paths, record shapes, timestamp fields, and epoch units so the workflow filters records instead of guessing. Every branch, PR, and file a brief names is checked against live `git` first. `catchup` reads only the current conversation plus live branch, PR, CI, and agent state.
- **`diff-summary`** holds two standalone skills. `diff-summary` is the single authoring source — `collect_diff_evidence.py` owns the hardened Git/GitHub boundary, its `SKILL.md` owns aligned Korean/English analysis and the `--md` and `--quiz` options, and `generate_summary_report.py` plus `summary-template.html` validate and merge the two Markdown sources into interactive offline HTML. `--md` adds `--markdown-only` (no HTML, no browser open) and `--quiz` appends aligned validated `## Quiz` sections rendered as interactive multiple-choice quizzes. `diff-viewer` is a separate skill — `generate_diff_report.py` plus `diff-template.html` — that displays the raw patch without analysis behind the same bilingual interface, localizing only its chrome because the diff body is code.
- **`plan-summary`** owns the explicit-file boundary and evidence-first document workflow. `collect_plan_evidence.py` returns ordered UTF-8 contents and SHA-256 identities from a bounded JSON request; `generate_plan_summary.py` validates aligned `PS-*` and optional `QZ-*` contracts, derives collision-safe names, and assembles offline HTML from `summary-template.html`. One skill carries all three output modes through `--md` and `--quiz`, so there is one workflow and one runtime copy.
- **`interrogate`** centralizes defect analysis in the `interrogate` skill: the review workflow, five reference guides (`review-criteria`, `proof-and-panel`, `common-vulnerabilities`, `python`, `javascript-typescript`), and two scripts (`diff_stats.py`, `generate_html_report.py`) plus `report-template.html`. `--md` stops after the Markdown artifact. Each finding is graded on the proof ladder, and `proof-and-panel.md` defines how proofs are run read-only and how an optional adversary panel is merged. `blast-radius` is a separate read-only skill with no scripts that answers a different question, what the change breaks outside the diff.
- **`review-me`** is a user-invoked, read-only decision-tree interview. Its `SKILL.md` owns the dependency-ordered frontier, single-question loop, recursive child expansion, descendant reopening, five leaf-closure tests, and final confirmation. `references/review-lenses.md` is the disclosed audit checklist loaded before the first substantive question, so the execution steps stay legible while every applicable product, system, human-interface, security, operational, and evolution consequence is accounted for.
- **`git-skill`** keeps its single Python helper, `rewrite_msg.py`, under `git-commit/scripts/`. `git-commit` is the one commit skill: its `SKILL.md` owns mode resolution, the Conventional Commit format, the default workflow, and the safety rules, and three references carry the long parts — `references/checkpoints.md` (outcome-based checkpoint planning, per-checkpoint verification, push parity proof), `references/deploy.md` (settings resolved from `AGENTS.md` or its referenced deployment instructions, exact pushed-SHA or artifact selection, direct or CI deployment, required runtime checks, and the gate before the next outcome), and `references/rewrite.md` (validated range, clean-tree and pushed-commit checks, and confirmed local rewrites). `gcr`, `gcpr`, `gcprm`, and `gcpd` are thin selector skills that load `git-commit` with the mode fixed to `realtime`, `push realtime`, `push realtime merge-main`, and `deploy`. `git-merge` resolves its target (`main`, `dev` with a `develop` fallback, or any local branch), plans, confirms, merges without pushing, and deletes the source with `git branch -d` only. `git-cleanup` runs a worktree pass and a branch pass behind one confirmed plan, using `git worktree remove` without `--force` and `git branch -d`. `git-resolve-conflicts` finishes an in-progress merge, rebase, cherry-pick, or revert instead of abandoning it: its `SKILL.md` owns operation identification including the rebase label inversion, the `--diff-filter=U` inventory read under `--conflict=zdiff3`, a per-class resolution policy that regenerates lockfiles and generated files rather than hand-merging them and resolves a submodule from its own log, intent recovery from both sides' history before a hunk is touched, the resolution ledger recording which intent survived each hunk, and the refusal to run `--abort`, `--skip`, or any push.
- **`handoff`** is one skill with an audience argument. `SKILL.md` resolves the audience (argument, then the request's wording, then the diff), states the choice in the first line, and loads one reference: `references/frontend.md` (client-visible API contract changes, type/rendering/error-state work, and `client action 없음` for DB-only changes), `references/backend.md` (API contracts, database migrations, jobs/queues, rollout, verification, and backend continuation prompts), or `references/session.md` (hands the session itself rather than a diff: proven state split from unproven with the exact command behind each proven claim, plans, specs, and diagnosis records referenced by path, decisions recorded with their reasons and the approaches ruled out, and ordered next actions with done-checks plus a copyable resume prompt).
- **`swarm`** holds two skills. `swarm` routes work asked for through subagents to other installed coding agents. `swarm.py` probes the local CLIs, validates the route plan, builds the invocation, and writes the run under `$XDG_CACHE_HOME/swarm/runs/<run-id>/` (or `~/.cache/swarm/runs/<run-id>/`); `references/routes.md`, `selection.md`, and `execution.md` hold the route table, selection rules, and execution rules, and `assets/prompts/common.md` is the shared delegate prompt. The plan records why the route was chosen, a missing quota transcript cannot invent a percentage, and independent checks use different vendors. `arena` has no script of its own: it writes a hidden rubric, seats candidates through `swarm` when installed, runs one cross-vendor judge on neutral labels, and grafts by hand.
- **`long-task`** carries `long_task.py` (lifecycle commands + Stop-hook installer) and two references (`completion-audit`, `project-templates`).
- **`build-reinstall`** is an explicit-only local installation workflow. Its `SKILL.md` resolves project-owned build, reinstall, and verification commands, requires build success before changing the installed target, and separates unavailable runtime proof from checks that passed. `references/build-reinstall.example.yaml` documents optional version 1 configuration with explicit target paths and built/installed SHA-256 pairs.
- **`doc-skill`** carries four output templates under `gen-docs/templates/` and keeps its natural-Korean fallback inside `gen-docs` rather than depending on another package.
- **`bug-hunt`** is a stateful diagnosis loop rather than debugging advice. Its `SKILL.md` owns the defect statement, the reproduce-before-editing gate, the four-column hypothesis ledger (hypothesis, falsified-if, observed, verdict), the widening rule that forbids a fourth hypothesis in a layer that produced three falsified ones, the failing-first check gate, the `BUGHUNT` marker whose removal is proven by search, and the closing record with its kept falsified list. `references/instrumentation-playbook.md` carries the probe-selection ladder, per-ecosystem probe spellings, the intermittent-failure loop, bisection over commits, inputs, and configuration, and the measure-before-hypothesizing rule for performance work.
- **`research-brief`** makes provenance a structural requirement rather than a habit. Its `SKILL.md` owns the question-sharpening step, optional background-agent delegation seeded with the format rather than a topic, the T1/T2/T3 source tiers with the rule that a T3 claim is a lead and never an answer, per-claim version or date pinning, the contradiction ledger that keeps both sides with the resolution and its reason, and the answer-first document shape whose open-questions section is mandatory even when empty.
- **`unslop`** rewrites AI-written prose without moving meaning. Its `SKILL.md` owns the hard preservation rules, per-passage language detection, the three-part judgment test for unlisted Korean slop terms, and the ban on leaked method vocabulary; `references/slop-lexicon.md` carries the replaceable-term tables plus the keep list of established technical terms, `references/style-rules.md` carries the translation-ese/rhythm/tone pass with the final self-check checklist, and `references/english-rules.md` carries the English rules `E1`–`E21` with stable ids.
- **`no-comments`** removes comments that only narrate the code. `references/comment-review.md` is the reviewer prompt. A general subagent runs it, or the session runs it inline when the host has no subagent tool. The reviewer does not edit application code. A rejected review does not abort accepted findings. A comment about an outside rule that cannot be checked is kept and marked for review. A real constraint is encoded in a type, test, or lint only after a yes.
- **`make-bot-ui`** builds a page whose controls wake a bot through a webhook the user supplies. `scripts/webhook_post.py` renders a page that posts only to the local server, rejects a page that contains the sender key or the webhook host, and builds the one POST the server sends. The sender key stays in server-side config. A key pasted in chat is refused and is not repeated.
- **`skill-forge`** owns the repository's skill contract and holds three skills. `skills/skill-forge/references/skill-package-contract.md` states rules C1 through C9 — name parity, description grammar, invocation-mode declaration, Codex descriptor, slash command, evals, catalog and locale parity, plugin manifest, and published counts — and `references/description-grammar.md` explains how a description earns reliable invocation. `skill-audit` carries the executable form, `scripts/audit_skills.py`: a stdlib-only walker over `*/skills/*/SKILL.md` that reports each violation as rule, skill, detail, and file, emits text, JSON, or Markdown, and exits non-zero so it works as a merge gate. `tests/test_skill_contract.py` runs it over this repository, which is why a half-published skill fails the suite rather than shipping. `reflect` collects what a session or repository history taught, keeps only lessons that will still hold in six months, routes each to the strongest enforcement that works, and stops at Accepted, Rejected, and Backlog lists before editing anything.

### Supporting files

- **`website/`** — the interactive catalog. `website/src/data/skills.ts` and four locale files under `website/src/i18n/content/` carry every workflow; `.github/workflows/pages.yml` deploys the built bundle to GitHub Pages on a push to `main`.
- **`samples/code-review/`** — intentionally vulnerable fixtures (`go-api`, `python-auth`, `react-dashboard`) used to demo the reviewer. Kept outside the plugin folders so they never ship in a published plugin.
- **`tests/`** — unittest/pytest suite: per-plugin package tests plus parser, renderer, CLI, interaction-contract, and diff-viewer fixture tests.
- **`docs/`** — design and planning notes under `docs/superpowers/`.
- **`AGENTS.md`** and **`CLAUDE.md`** — repository instructions: the skill contract, website sync rules, and deploy configuration.
- **`VERSION`** — release stamp in `head.yymmdd.patch` form.
- **`.snyk`** — SAST policy that excludes the intentionally vulnerable `samples/**`; `interrogate/.snyk` does the same for the plugin.

## Data flow

### Installation

`npx skills add chann/skills` runs the external `skills` installer. It reads the repository's skill folders, `<plugin>/skills/<name>/SKILL.md`, resolves the names requested with `--skill` (or all of them with `--skill '*'`), and links or copies each skill directory into the target agent's skills location. This repository holds no installer state of its own.

### Invocation (Claude Code)

1. The user types a slash command (e.g. `/interrogate --md`) or triggers a skill by natural language.
2. Claude Code loads the matching `commands/*.md`, which points at the skill.
3. The skill runs its `SKILL.md` workflow, loading `references/` and invoking bundled scripts through a canonical absolute Python executable in `-I` isolated mode as needed.
4. Outputs land where the skill specifies — a conversational closure record for `review-me`, review reports under `.reviews/`, change summaries under `.diff-summaries/`, plan summaries under `.plan-summaries/`, raw diff reports under `.diffs/`, handoffs under `.handoffs/`, work reports in the reply or under `.work-summaries/`, a verified local install from `build-reinstall`, git history changes, `long-task` state under `.agent/`, or a `swarm` run directory with the route rationale, each task result, and a call-tree report.

### Invocation (Codex)

1. The user names the skill with its dollar selector (for example,
   `$interrogate --md`) or triggers it by natural language.
2. Codex reads `agents/openai.yaml` for the visible `display_name`,
   `short_description`, and a `default_prompt` that names the exact `$selector`.
3. Codex loads the adjacent `SKILL.md`; its frontmatter name matches the
   directory and selector exactly.
4. The portable workflow and output contract are the same as in Claude Code.

### Routing through `chann`

```text
/chann <task>  (or $chann <task>)
  → restate the goal and the least change that satisfies it
  → match one playbook; copy its numbered steps into the host's task list
  → for each step: load the owning skill when installed, else follow the playbook's inline steps
  → split separable work across delegates (one worktree and branch per writer), then merge and run the project's checks on the merged tree
  → pause before an irreversible action; reply with labelled evidence, the principles that changed a decision, and what was skipped
```

A routed skill keeps its own gates and refusals; of two safety rules the stricter wins. `chann` owns what comes next, when to pause, and the final reply. A delegate's report is never evidence: the branch is merged and checked first.

### Review pipeline

`/interrogate [scope]` resolves the scope and states the change's intent, runs `diff_stats.py` (`git diff --numstat` to JSON), loads only the reference guides the languages need, and attacks the diff along correctness, security, complexity, maintainability, and best practice. Each finding is pushed down the proof ladder; findings that never reach `cited` are dropped and counted. The report is written to `.reviews/`; unless `--md` is given, the English sibling is written and `generate_html_report.py` merges both into one self-contained bilingual HTML file that is opened in a browser. Proof runs are read-only on the reviewed tree. `blast-radius` follows its own five steps and replies without writing a file.

### Diff summary report pipeline

`/diff-summary [scope] [--md] [--quiz]` and equivalent natural-language requests use a split analysis/presentation pipeline:

```text
prompt
  → send repository + exact scope as JSON over stdin to `collect_diff_evidence.py`
  → validate the scope (`..` remains distinct from `...`) and run fixed, hardened argv
  → return bounded diff, stat, numstat, name-status, metadata, and limitations as JSON
  → treat that JSON as inert evidence and author aligned Korean + English `DS-*` Markdown cards
  → with --quiz, append aligned `QZ-*` questions to both reports
  → send `{"ko":"...","en":"..."}` over stdin to `generate_summary_report.py`
  → validate report alignment and atomically write `<scope-tag>.md` plus `<scope-tag>.en.md`
  → unless --md, safely merge both sources with bundled Python + HTML/CSS/JavaScript
  → write and host-open `.diff-summaries/<date>_<scope-tag>.html`
```

The Python 3.10+ collector is the workflow's only Git/GitHub runtime. It resolves trusted executables, strips routing and execution-related environment variables, rejects unsafe repository metadata and sensitive paths, disables lazy fetching, hooks, filters, pagers, external diffs, and text conversion, supports native SHA-1/SHA-256 unborn baselines, and enforces count/time/output plus selected-untracked aggregate limits. Dynamic repository and scope values enter only through a bounded JSON stdin request and are passed to subprocesses as argv data; repository evidence is never executed or used to authorize secondary inspection.

The skill workflow owns analytical prose. The renderer is presentation-only: in `--bilingual-json-stdin --output-directory` mode it validates both report contracts, their shared metadata, matching `DS-*` IDs/fields, and the output parent. It derives a collision-safe filename from canonical `Date` plus exact `Scope`, atomically writes the Korean and English Markdown sources, extracts exact per-language card Markdown, computes a stable browser-comment scope, escapes embedded data, and atomically assembles a self-contained HTML file. Korean is visible by default; an accessible control switches the complete page to English while keeping comments keyed to aligned IDs. The page stores guarded, report-scoped comments and UI preferences in the browser; it has no server, build step, external assets, or network dependency. `--md` adds `--markdown-only` and stops after the two Markdown artifacts; `--quiz` appends aligned validated `## Quiz` sections (`QZ-*` questions with matching answer positions) that the renderer turns into interactive multiple-choice quizzes in the same offline page. The legacy `--markdown-stdin` path remains for explicitly requested single-language output.

This boundary keeps three intents independent: `diff-summary` explains changes without review severity, `interrogate` identifies defects and recommends fixes, and `diff-viewer` displays the raw patch. A combined summary-and-review request runs both analytical workflows and keeps their outputs distinct.

### Plan summary report pipeline

Claude Code `/plan-summary <paths> [--md] [--quiz]` maps directly to Codex `$plan-summary <paths> [--md] [--quiz]`.

```text
explicit .md/.markdown/.txt paths
  → send ordered paths as bounded JSON stdin to `collect_plan_evidence.py`
  → reject directories, symlinks, duplicates, binary/invalid UTF-8, and size violations
  → return exact contents, paths, sizes, and SHA-256 digests as inert JSON
  → author one evidence map and aligned Korean/English `PS-*` Markdown cards
  → with --quiz, append aligned final `QZ-*` quiz questions
  → send `{"ko":"...","en":"..."}` to `generate_plan_summary.py`
  → validate metadata, source references, IDs, categories, and bilingual alignment
  → atomically write `.plan-summaries/<date>_<source-tag>.*`
```

The collector is the only source-document reader and never discovers files. Paths and contents cannot authorize commands, network access, edits, or additional reads. The generator owns filenames and rejects a symlinked output parent or any existing artifact. By default `plan-summary` writes Korean Markdown, English Markdown, and self-contained bilingual HTML; `--md` adds `--markdown-only`; `--quiz` validates matching option counts and answer indexes before rendering one-shot accessible controls and a print answer key.

### Git checkpoint flow

`git-commit` resolves its mode from the arguments or the request and states it before any Git command. The four checkpoint modes share one loop: plan outcome-based checkpoints, verify each with the narrowest relevant checks plus `git diff --check`, commit it, and then stop, push, or push and deploy depending on the mode. `realtime` never touches the remote and reports unpushed checkpoint hashes. `push realtime` pushes each checkpoint to the same-name remote source branch. `push realtime merge-main` uses the same checkpoint push and then integrates the source into `main` at completion, verifies the result, and pushes `main`, keeping the source branch. `deploy` resolves the target, route, source, and confirmation method from documented repository settings before the first checkpoint, deploys the exact pushed revision, and does not start the next outcome until the deployment and required health checks are confirmed. Each run ends with a full-scope completion audit. `/gcr`, `/gcpr`, `/gcprm`, and `/gcpd` (and `$gcr`, `$gcpr`, `$gcprm`, `$gcpd`) only select the mode; the policy lives in `git-commit`.

### long-task autonomy loop

`/long-task` Phase 1 writes the working-memory files under `.agent/` (`goal.md`, `plans.md`, `standards.md`, `implement.md`, `progress.md`, `state.md`) and, on first run, `long_task.py` installs a `Stop` hook in `~/.claude/settings.json`. While `.agent/state.md` holds `status: active`, the Stop hook re-invokes Claude to continue Phase 2 orchestration — dispatching up to five parallel worktree subagents per milestone, verifying tests, merging, and running an architectural review — until Phase 3 runs the completion audit and sets `status: complete`. The hook is scoped to the project's working directory and bounded by a runaway counter (`LONG_TASK_MAX_STOP_CONTINUES`).

## Directory structure

Generated from the filesystem. Every skill directory also holds `agents/openai.yaml` and `evals/evals.json`; they are listed once in the layout above and omitted below.

```
skills/
├── chann-mode/                           # plugin (v0.4.0)
│   ├── .claude-plugin/plugin.json
│   ├── commands/chann.md
│   ├── skills/chann/
│   │   ├── SKILL.md
│   │   ├── worker.md
│   │   ├── playbooks/                    # 22 playbooks
│   │   ├── references/principles.md
│   │   └── references/decision-trail.md
│   ├── README.md
│   └── README.ko.md
├── understand/                           # plugin (v0.1.0)
│   ├── .claude-plugin/plugin.json
│   ├── commands/how.md
│   ├── commands/why.md
│   ├── skills/how/SKILL.md
│   ├── skills/why/SKILL.md
│   ├── README.md
│   └── README.ko.md
├── research-brief/                       # plugin (v0.1.0)
│   ├── .claude-plugin/plugin.json
│   ├── commands/research-brief.md
│   ├── skills/research-brief/SKILL.md
│   ├── README.md
│   └── README.ko.md
├── recall/                               # plugin (v2.0.0)
│   ├── .claude-plugin/plugin.json
│   ├── commands/recall.md
│   ├── commands/catchup.md
│   ├── skills/recall/SKILL.md
│   ├── skills/recall/references/agent-history-stores.md
│   ├── skills/catchup/SKILL.md
│   ├── README.md
│   └── README.ko.md
├── diff-summary/                         # plugin (v3.0.0)
│   ├── .claude-plugin/plugin.json
│   ├── commands/diff-summary.md
│   ├── commands/diff-viewer.md
│   ├── skills/diff-summary/SKILL.md
│   ├── skills/diff-summary/scripts/collect_diff_evidence.py
│   ├── skills/diff-summary/scripts/generate_summary_report.py
│   ├── skills/diff-summary/assets/summary-template.html
│   ├── skills/diff-viewer/SKILL.md
│   ├── skills/diff-viewer/scripts/generate_diff_report.py
│   ├── skills/diff-viewer/assets/diff-template.html
│   ├── README.md
│   └── README.ko.md
├── plan-summary/                         # plugin (v2.0.0)
│   ├── .claude-plugin/plugin.json
│   ├── commands/plan-summary.md
│   ├── skills/plan-summary/SKILL.md
│   ├── skills/plan-summary/scripts/collect_plan_evidence.py
│   ├── skills/plan-summary/scripts/generate_plan_summary.py
│   ├── skills/plan-summary/assets/summary-template.html
│   ├── README.md
│   └── README.ko.md
├── review-me/                            # plugin (v0.1.1)
│   ├── .claude-plugin/plugin.json
│   ├── commands/review-me.md
│   ├── skills/review-me/SKILL.md
│   ├── skills/review-me/references/review-lenses.md
│   ├── README.md
│   └── README.ko.md
├── swarm/                                # plugin (v1.0.0)
│   ├── .claude-plugin/plugin.json
│   ├── commands/swarm.md
│   ├── commands/arena.md
│   ├── skills/swarm/SKILL.md
│   ├── skills/swarm/scripts/swarm.py
│   ├── skills/swarm/references/routes.md
│   ├── skills/swarm/references/selection.md
│   ├── skills/swarm/references/execution.md
│   ├── skills/swarm/assets/prompts/common.md
│   ├── skills/arena/SKILL.md
│   ├── README.md
│   └── README.ko.md
├── bug-hunt/                             # plugin (v0.1.1)
│   ├── .claude-plugin/plugin.json
│   ├── commands/bug-hunt.md
│   ├── skills/bug-hunt/SKILL.md
│   ├── skills/bug-hunt/references/instrumentation-playbook.md
│   ├── README.md
│   └── README.ko.md
├── doc-skill/                            # plugin (v0.2.1)
│   ├── .claude-plugin/plugin.json
│   ├── commands/gen-docs.md
│   ├── skills/gen-docs/SKILL.md
│   ├── skills/gen-docs/templates/README.md.tmpl
│   ├── skills/gen-docs/templates/README.ko.md.tmpl
│   ├── skills/gen-docs/templates/ARCHITECTURE.md.tmpl
│   ├── skills/gen-docs/templates/USAGE.md.tmpl
│   ├── README.md
│   └── README.ko.md
├── unslop/                               # plugin (v1.0.0)
│   ├── .claude-plugin/plugin.json
│   ├── commands/unslop.md
│   ├── skills/unslop/SKILL.md
│   ├── skills/unslop/references/slop-lexicon.md
│   ├── skills/unslop/references/style-rules.md
│   ├── skills/unslop/references/english-rules.md
│   ├── README.md
│   └── README.ko.md
├── no-comments/                          # plugin (v0.1.0)
│   ├── .claude-plugin/plugin.json
│   ├── commands/no-comments.md
│   ├── skills/no-comments/SKILL.md
│   ├── skills/no-comments/references/comment-review.md
│   ├── README.md
│   └── README.ko.md
├── make-bot-ui/                          # plugin (v0.1.0)
│   ├── .claude-plugin/plugin.json
│   ├── commands/make-bot-ui.md
│   ├── skills/make-bot-ui/SKILL.md
│   ├── skills/make-bot-ui/scripts/webhook_post.py
│   ├── README.md
│   └── README.ko.md
├── build-reinstall/                      # plugin (v0.1.0)
│   ├── .claude-plugin/plugin.json
│   ├── commands/build-reinstall.md
│   ├── skills/build-reinstall/SKILL.md
│   ├── skills/build-reinstall/references/build-reinstall.example.yaml
│   ├── README.md
│   └── README.ko.md
├── interrogate/                          # plugin (v3.0.0)
│   ├── .claude-plugin/plugin.json
│   ├── commands/interrogate.md
│   ├── commands/blast-radius.md
│   ├── skills/interrogate/SKILL.md
│   ├── skills/interrogate/scripts/diff_stats.py
│   ├── skills/interrogate/scripts/generate_html_report.py
│   ├── skills/interrogate/references/review-criteria.md
│   ├── skills/interrogate/references/proof-and-panel.md
│   ├── skills/interrogate/references/common-vulnerabilities.md
│   ├── skills/interrogate/references/python.md
│   ├── skills/interrogate/references/javascript-typescript.md
│   ├── skills/interrogate/assets/report-template.html
│   ├── skills/blast-radius/SKILL.md
│   ├── .snyk
│   ├── README.md
│   └── README.ko.md
├── git-skill/                            # plugin (v1.1.0)
│   ├── .claude-plugin/plugin.json
│   ├── commands/git-commit.md
│   ├── commands/gcr.md
│   ├── commands/gcpr.md
│   ├── commands/gcprm.md
│   ├── commands/gcpd.md
│   ├── commands/git-merge.md
│   ├── commands/git-resolve-conflicts.md
│   ├── commands/git-cleanup.md
│   ├── skills/git-commit/SKILL.md
│   ├── skills/git-commit/references/checkpoints.md
│   ├── skills/git-commit/references/deploy.md
│   ├── skills/git-commit/references/rewrite.md
│   ├── skills/git-commit/scripts/rewrite_msg.py
│   ├── skills/gcr/SKILL.md
│   ├── skills/gcpr/SKILL.md
│   ├── skills/gcprm/SKILL.md
│   ├── skills/gcpd/SKILL.md
│   ├── skills/git-merge/SKILL.md
│   ├── skills/git-resolve-conflicts/SKILL.md
│   ├── skills/git-cleanup/SKILL.md
│   ├── README.md
│   └── README.ko.md
├── long-task/                            # plugin (v0.3.0)
│   ├── .claude-plugin/plugin.json
│   ├── commands/long-task.md
│   ├── skills/long-task/SKILL.md
│   ├── skills/long-task/scripts/long_task.py
│   ├── skills/long-task/references/completion-audit.md
│   ├── skills/long-task/references/project-templates.md
│   ├── README.md
│   └── README.ko.md
├── handoff/                              # plugin (v1.0.0)
│   ├── .claude-plugin/plugin.json
│   ├── commands/handoff.md
│   ├── skills/handoff/SKILL.md
│   ├── skills/handoff/references/frontend.md
│   ├── skills/handoff/references/backend.md
│   ├── skills/handoff/references/session.md
│   ├── README.md
│   └── README.ko.md
├── skill-forge/                          # plugin (v0.2.0)
│   ├── .claude-plugin/plugin.json
│   ├── commands/skill-forge.md
│   ├── commands/skill-audit.md
│   ├── commands/reflect.md
│   ├── skills/skill-forge/SKILL.md
│   ├── skills/skill-forge/references/skill-package-contract.md
│   ├── skills/skill-forge/references/description-grammar.md
│   ├── skills/skill-audit/SKILL.md
│   ├── skills/skill-audit/scripts/audit_skills.py
│   ├── skills/reflect/SKILL.md
│   ├── README.md
│   └── README.ko.md
├── website/                              # interactive catalog, deployed to GitHub Pages
├── samples/code-review/                  # intentionally vulnerable demo fixtures (outside plugin artifacts)
├── tests/                                # pytest: package tests + diff_viewer/, diff_summary/, plan_summary/, swarm/ unit tests
├── docs/                                 # design / planning notes
├── .github/workflows/pages.yml           # GitHub Pages deploy
├── AGENTS.md
├── CLAUDE.md
├── VERSION                               # head.yymmdd.patch
├── LICENSE                               # MIT
├── README.md
├── README.ko.md
├── USAGE.md
├── ARCHITECTURE.md
├── .snyk
└── .gitignore
```

## Design decisions

- **Portable `SKILL.md` is the unit of work.** Skill bodies avoid Claude-Code-only tools, so the same files run on other agent platforms. The Claude Code plugin wrapper (`.claude-plugin` + `commands` + `npx skills`) is additive, not required.
- **One plugin per workflow domain.** The 19 plugins are versioned and installable independently, so users adopt only what they need. A plugin groups skills that share a question or a runtime: `understand` holds `how` and `why`, `recall` holds `recall` and `catchup`, `interrogate` holds `interrogate` and `blast-radius`.
- **One router skill, with playbooks and principles.** A catalog of 29 workflows is hard to remember, so `chann` is the single entry point. It matches the task to one of 22 playbooks, and each playbook step names the skill that owns it. The playbooks and principles live in files the skill loads on demand, so `SKILL.md` stays short and a principle is cited only after it was read. It routes to a skill only when that skill is installed and carries inline steps otherwise, so it works alone. It is `Use only when` explicitly invoked, so it never takes over a request that a specific skill should handle.
- **Variants are arguments of one canonical skill; no synchronized copies remain.** `diff-summary`, `plan-summary`, `interrogate`, `git-commit`, `git-merge`, and `handoff` each used to ship their variants as separate packages that carried byte-synchronized copies of the same workflow and runtime, kept equal by parity tests. Each variant is now an argument (`--md`, `--quiz`, `push realtime`, `main`, `session`) of one skill with one workflow, one runtime, and one set of evals. A bug is fixed in one place, and an installed skill cannot drift from a sibling. The old names are listed in the migration tables in [README.md](README.md#migrating-from-the-previous-lineup) and [USAGE.md](USAGE.md#migrating-from-the-previous-lineup).
- **One evidence vocabulary across skills.** Verdicts are `VERIFIED`, `NOT VERIFIED`, or `INCONCLUSIVE`, and inconclusive is never a pass. A claim without direct evidence is labelled `measured`, `inferred`, or `guess`. Where a skill grades how well a finding is proven, it uses one proof ladder, weakest first: `said` < `cited` (a real `file:line`) < `traced` (the failing path walked step by step) < `ran` (a command or test whose output shows it) < `reproduced` (seen in the running product). A reader who learns the words once can read the output of `interrogate`, `blast-radius`, `how`, `why`, `bug-hunt`, `handoff`, and the `chann` reply the same way.
- **Thin aliases only for the four checkpoint modes of `git-commit`.** `/gcr`, `/gcpr`, `/gcprm`, and `/gcpd` exist because those modes are typed constantly while work continues, and Codex has no alias metadata. `$gcr`, `$gcpr`, `$gcprm`, and `$gcpd` are thin, explicit-only selector skills that load `git-commit` with a fixed mode and refuse when it is missing. They add no policy and no catalog workflow. No other variant gets an alias, so the 33 selectors are the 29 workflows plus these four.
- **Each skill works when installed alone.** A reference to a sibling is an optional enhancement: when `swarm` is installed `interrogate` can seat an adversary panel, and when `unslop` is installed `handoff` can use it as a wording pass. Otherwise the skill does the steps itself. The aliases are the one exception, because they exist only to select a mode of `git-commit`.
- **One skill contract with an executable audit.** Nine rules cover naming, description grammar, invocation mode, the Codex descriptor, the slash command, evals, catalog and locale parity, the plugin manifest, and published counts. `skill-audit` is their executable form and `tests/test_skill_contract.py` runs it, so a half-published skill fails the suite instead of shipping.
- **Local reinstall is explicit and evidence-based.** `build-reinstall` never runs as a completion hook. It chooses commands from optional versioned YAML or project-owned instructions, stops before installation when the build or target is unresolved, and reports success only after installed-result verification.
- **Natural prose is an optional enhancement, not a dependency.** Document-generating skills carry a compact built-in Korean writing contract. They may use `unslop` when the runtime already exposes it, but never install, fetch, or require it; missing support cannot block or reduce output.
- **Work reporting is read-only and local.** `recall` mines the machine's own agent history stores, never mutates them, keeps history content off the network, and leaves generated reports out of version control (`.work-summaries/` is ignored here). `catchup` is read-only toward everything.
- **Leaf-complete decision review is distinct from code review.** `review-me` resolves plans, designs, and choices conversationally; `interrogate` evaluates concrete Git changes for defects. The former runs only on its selector and stays read-only through confirmation, while the latter may trigger naturally from a diff-review request and writes reports.
- **Code, history, and the outside world are three different sources of truth.** `how` reads the code, `why` reads the record, and `research-brief` reads primary sources. Splitting them stops an answer about motivation from being inferred from the shape of the code.
- **Platform names are explicit and paired.** Every skill directory name matches
  its `SKILL.md` frontmatter name, every Claude Code command wrapper uses
  `/name`, and every `agents/openai.yaml` publishes a Codex display name plus a
  `$name` default prompt. Package tests enforce all three surfaces. The alias
  commands `commands/gcr.md`, `commands/gcpr.md`, `commands/gcprm.md`, and `commands/gcpd.md` publish
  `/gcr`, `/gcpr`, `/gcprm`, and `/gcpd` for the `git-commit realtime`, `git-commit push realtime`,
  `git-commit push realtime merge-main`, and `git-commit deploy` modes.
- **Evidence, analysis, and presentation are separate boundaries.** `collect_diff_evidence.py` is the only Git/GitHub runtime and emits bounded JSON; `diff-summary/SKILL.md` treats it as inert evidence and authors the Markdown contract; the bundled renderer never invokes Git or invents analytical prose. This keeps the exact scope and verified/unverified boundary visible in the source report.
- **Report interfaces are shared by test, not by import.** The HTML templates of `diff-summary`, `plan-summary`, `diff-viewer`, and `interrogate` deliberately duplicate the shared design tokens, icon geometry, and accessibility shell so each skill stays independently installable; `tests/test_html_report_style_contract.py` is what keeps those copies consistent rather than a runtime import.
- **Generated reports stay local.** `.reviews/`, `.diff-summaries/`, `.plan-summaries/`, and `.diffs/` are ignored in this repository. Skills may suggest an ignore entry in target repositories, but do not mutate their `.gitignore` automatically.
- **Sample vulnerabilities live outside the plugins.** Demo fixtures sit in repo-root `samples/` and are excluded via `.snyk`, so a published plugin neither ships exploitable code nor trips SAST scanners.
- **Self-contained stdlib Python.** Helper scripts, including the `diff-summary` and `plan-summary` collectors, the `swarm` runner, and parser/renderers, import only the Python 3.10+ standard library, so there is no dependency install step.
- **Bounded autonomy for `long-task`.** Auto-continuation is gated on a per-directory `.agent/state.md` flag and a runaway cap (`LONG_TASK_MAX_STOP_CONTINUES`, default 500), so a runaway loop is contained and easy to pause.
- **Date-stamped versioning.** `VERSION` uses the `head.yymmdd.patch` scheme. Plugins carry their own semver: a renamed or consolidated plugin takes the next major version, a brand-new plugin starts at `0.1.0`, and a reference-only edit is a patch bump.
