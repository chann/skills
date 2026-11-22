# skills — Usage

This repository exposes 27 canonical workflows and 30 installable Codex selectors across 17 workflow plugins. The 30 selectors are the 27 workflows plus the three aliases `gcr`, `gcpr`, and `gcpd`.

## Installation

### All skills at once (recommended)

```bash
npx skills add chann/skills \
  --skill '*' \
  --agent claude-code codex antigravity-cli grok pi gemini-cli \
    github-copilot opencode \
  --global \
  --yes
```

`--global` installs for your user, `--yes` skips prompts, and omitting `--copy`
keeps the installer's default symlink mode. The explicit agent list avoids the
`skills@1.5.19` bugs that can implicitly target the project-only PromptScript
adapter or fall back to copy mode during non-interactive global installs.
Verified with `skills@1.9.0` in a clean temporary `HOME`: one copy lands in
`~/.agents/skills/<name>/`, read directly by Codex, Pi, Gemini CLI, GitHub
Copilot CLI, and OpenCode, with symlinks at `~/.claude/skills/` (Claude Code),
`~/.gemini/config/skills/` (Antigravity CLI), and `~/.grok/skills/` (Grok
Build). Drop `--global` to install into the current project.
[README.md](README.md#installation) has the per-agent table.

### A single skill

```bash
npx skills add -y -g chann/skills --skill gen-docs
```

Use `--skill <name>` with the actual skill name. The 30 names are `chann`, `how`, `why`, `research-brief`, `recall`, `catchup`, `diff-summary`, `diff-viewer`, `plan-summary`, `review-me`, `arena`, `bug-hunt`, `gen-docs`, `unslop`, `build-reinstall`, `interrogate`, `blast-radius`, `git-commit`, `gcr`, `gcpr`, `gcpd`, `git-merge`, `git-resolve-conflicts`, `git-cleanup`, `swarm`, `long-task`, `handoff`, `skill-forge`, `skill-audit`, and `reflect`. Plugin directories such as `git-skill` and `understand` are not names; pass the skill inside them.

Every skill works when installed alone. The three aliases are the one exception: each runs the installed `git-commit` with a fixed mode and refuses when `git-commit` is missing.

| Install | Command |
|---|---|
| Entry point only | `npx skills add chann/skills --skill chann` |
| Understand a codebase | `npx skills add chann/skills --skill how --skill why` |
| Review a change | `npx skills add chann/skills --skill interrogate --skill blast-radius` |
| Explain a change | `npx skills add chann/skills --skill diff-summary --skill diff-viewer` |
| Git workflow with the short aliases | `npx skills add chann/skills --skill git-commit --skill gcr --skill gcpr --skill gcpd --skill git-merge --skill git-resolve-conflicts --skill git-cleanup` |
| Codex `$gcpr` and its canonical workflow | `npx skills add chann/skills --skill gcpr --skill git-commit` |
| Handoff only | `npx skills add chann/skills --skill handoff` |
| Subagents and competing attempts | `npx skills add chann/skills --skill swarm --skill arena` |
| Past work and catch-up | `npx skills add chann/skills --skill recall --skill catchup` |
| Plan summaries | `npx skills add chann/skills --skill plan-summary` |
| Review-me only | `npx skills add chann/skills --skill review-me` |
| Build-reinstall only | `npx skills add chann/skills --skill build-reinstall` |
| Natural prose | `npx skills add chann/skills --skill unslop` |
| Bug hunting and research | `npx skills add chann/skills --skill bug-hunt --skill research-brief` |
| Skill authoring | `npx skills add chann/skills --skill skill-forge --skill skill-audit --skill reflect` |

To inspect the available names first, run `npx skills add chann/skills -l --full-depth`.

### Manual / other platforms

Any agent the installer lists works by adding its `--agent` ID to the command above. For an agent it does not list, clone the repo and point the agent's skill loader at the skill folder:

```bash
git clone https://github.com/chann/skills.git
cd skills
mkdir -p ~/.agents/skills
# Example: symlink one skill directory into a skills dir
ln -s "$(pwd)/understand/skills/how" ~/.agents/skills/how
```

A skill directory is `<plugin>/skills/<name>/`, the folder that holds `SKILL.md`; the plugin directory itself is not a skill.

| Platform | How to install |
|---|---|
| **Claude Code**, **Codex**, Antigravity CLI, Grok Build, Pi, Gemini CLI, GitHub Copilot CLI, **OpenCode** | `npx skills add` as above, with that platform's `--agent` ID |
| Other agents | Point the platform's skill loader at `<plugin>/skills/<name>/` |

For example, invoke the same skill with `/diff-summary --md` in Claude Code or Antigravity CLI, `$diff-summary --md` in Codex, or `/skill:diff-summary --md` in Pi.

For the deepest per-skill detail, see each plugin's own README: [chann-mode](chann-mode/README.md), [understand](understand/README.md), [research-brief](research-brief/README.md), [recall](recall/README.md), [diff-summary](diff-summary/README.md), [plan-summary](plan-summary/README.md), [review-me](review-me/README.md), [swarm](swarm/README.md), [bug-hunt](bug-hunt/README.md), [doc-skill](doc-skill/README.md), [unslop](unslop/README.md), [build-reinstall](build-reinstall/README.md), [interrogate](interrogate/README.md), [git-skill](git-skill/README.md), [long-task](long-task/README.md), [handoff](handoff/README.md), and [skill-forge](skill-forge/README.md).

## Quick start

```
> /chann login sometimes returns a 500, find the cause and fix it   # the one entry point
> /how does the job scheduler pick the next task                         # explain code from the code
> /why did we pick Postgres advisory locks over Redis                    # explain it from the record
> /interrogate review staged changes                                     # try to break the diff
> /blast-radius                                                          # what could this break elsewhere
> /diff-summary main..dev                  # Korean + English Markdown + bilingual HTML
> /diff-summary main..dev --md             # Korean + English Markdown only
> /diff-summary main..dev --quiz           # bilingual summary + aligned quiz
> /review-me the team invitation plan      # close every consequential decision leaf
> /git-commit                              # group changes into Conventional Commits
> /git-commit push realtime                # push each verified outcome while working
> /gcpr                                    # same workflow, short alias
> /git-commit deploy                       # commit, push, deploy, and confirm each outcome
> /gcpd                                    # same deployment workflow, short alias
> /git-commit realtime                     # commit each verified outcome locally, no push
> /gcr                                     # same local workflow, short alias
> /git-merge dev                           # merge this branch into dev
> /git-cleanup                             # remove finished worktrees and merged branches
> /git-resolve-conflicts                   # finish a conflicted merge or rebase
> /gen-docs                                # generate/update project docs
> /handoff frontend main...feature-api     # hand off backend API changes to client work
> /handoff backend HEAD~5..HEAD            # hand off recent backend/server work
> /handoff session                         # hand this session to a fresh agent
> /long-task build a CLI todo app end to end
> /swarm use subagents to review the auth diff
> /arena give me three attempts at the config loader API and pick the best
> /build-reinstall                         # build, reinstall, verify installed artifact
> /recall this week                        # Markdown report of the week's agent work
> /recall billing migration                # where does this topic stand
> /catchup                                 # what changed in this conversation
> /plan-summary docs/plan.md docs/design.md          # Korean + English plan summary + HTML
> /plan-summary docs/prd.md --md           # Korean + English Markdown only
> /plan-summary docs/spec.md --quiz        # bilingual summary + aligned quiz
> /unslop docs/note.ko.md                  # AI가 쓴 한국어를 사람 문장으로
> /bug-hunt the search endpoint got 10x slower   # reproduce, falsify, pin the fix
> /research-brief does this client retry by default?  # cited brief from primary sources
> /skill-forge add a CI triage skill       # author a package and publish every surface
> /skill-audit                             # report packages that break the skill contract
> /reflect repo                            # turn repeated mistakes into enforcement
```

### Explicit selectors

Claude Code uses slash commands; Codex uses dollar-prefixed skill selectors.
These are the exact names published by every package. Arguments are in the
command reference below.

| Workflow | Claude Code | Codex |
|---|---|---|
| Entry point | `/chann` | `$chann` |
| How code works | `/how` | `$how` |
| Why code is built this way | `/why` | `$why` |
| Primary-source research | `/research-brief` | `$research-brief` |
| Work-history report or topic brief | `/recall` | `$recall` |
| Conversation catch-up | `/catchup` | `$catchup` |
| Diff summary | `/diff-summary` | `$diff-summary` |
| Raw diff viewer | `/diff-viewer` | `$diff-viewer` |
| Plan document summary | `/plan-summary` | `$plan-summary` |
| Plan and design review | `/review-me` | `$review-me` |
| Competing attempts | `/arena` | `$arena` |
| Defect diagnosis | `/bug-hunt` | `$bug-hunt` |
| Project docs | `/gen-docs` | `$gen-docs` |
| Natural-prose rewrite | `/unslop` | `$unslop` |
| Build and reinstall | `/build-reinstall` | `$build-reinstall` |
| Adversarial code review | `/interrogate` | `$interrogate` |
| Change blast radius | `/blast-radius` | `$blast-radius` |
| Git commit (every mode) | `/git-commit` | `$git-commit` |
| Alias: local checkpoint commits | `/gcr` | `$gcr` |
| Alias: checkpoint commit and push | `/gcpr` | `$gcpr` |
| Alias: checkpoint commit, push, and deploy | `/gcpd` | `$gcpd` |
| Merge | `/git-merge` | `$git-merge` |
| Conflict resolution | `/git-resolve-conflicts` | `$git-resolve-conflicts` |
| Worktree and branch cleanup | `/git-cleanup` | `$git-cleanup` |
| Subagents and other coding agents | `/swarm` | `$swarm` |
| Autonomous long task | `/long-task` | `$long-task` |
| Handoff | `/handoff` | `$handoff` |
| Skill package authoring | `/skill-forge` | `$skill-forge` |
| Skill contract audit | `/skill-audit` | `$skill-audit` |
| Lessons into enforcement | `/reflect` | `$reflect` |

### Migrating from the previous lineup

Variant selectors became arguments of one canonical skill. The same mapping applies to the `$name` selectors in Codex.

| Old | New |
|---|---|
| `code-review`, `code-review-md` | `interrogate` (`--md` for Markdown only) |
| `diff-summary-md`, `diff-summary-quiz` | `diff-summary --md`, `diff-summary --quiz` |
| `plan-summary-md`, `plan-summary-quiz` | `plan-summary --md`, `plan-summary --quiz` |
| `human-friendly-writing` | `unslop` |
| `git-commit-push` | `git-commit push` |
| `git-commit-realtime` (`gcr`) | `git-commit realtime` (`gcr`) |
| `git-commit-push-realtime` (`gcpr`) | `git-commit push realtime` (`gcpr`) |
| `git-commit-push-deploy` (`gcpd`) | `git-commit deploy` (`gcpd`) |
| `git-commit-rewrite` | `git-commit rewrite` |
| `git-merge-to-main`, `git-merge-to-dev` | `git-merge main`, `git-merge dev` |
| `git-branch-cleanup` | `git-cleanup` |
| `gen-frontend-handoff`, `gen-backend-handoff`, `gen-session-handoff` | `handoff frontend`, `handoff backend`, `handoff session` |
| `all-subagents` | `swarm` |
| `work-summary` | `recall` |
| `chann-mode`, `ketchup` (short-lived names) | `chann`, `catchup` |

The output directories `.work-summaries/`, `.diff-summaries/`, `.plan-summaries/`, `.reviews/`, and `.handoffs/` keep their names, so existing ignore rules still work.

#### Remove the retired skills

Installing the new lineup does not remove the old names, so both sets stay
installed side by side. Remove every retired name with one command, then run
the install command again:

```bash
npx skills remove \
  code-review code-review-md \
  diff-summary-md diff-summary-quiz \
  plan-summary-md plan-summary-quiz \
  human-friendly-writing \
  git-commit-push git-commit-realtime git-commit-push-realtime \
  git-commit-push-deploy git-commit-rewrite \
  git-merge-to-main git-merge-to-dev git-branch-cleanup \
  gen-frontend-handoff gen-backend-handoff gen-session-handoff \
  all-subagents work-summary \
  chann-mode ketchup \
  --global --yes
```

- A name that is not installed is skipped, so the full list is safe to run.
- Without `--agent`, the command cleans the links of every agent. Drop
  `--global` when the skills were installed into one project.
- The command removes by name. If a skill with one of these names came from
  another source, leave that name out.

## Command reference

### chann

| Command | Action |
|---|---|
| `/chann <task>` | Run a non-trivial task in the owner's working style: restate the goal and the smallest change, match one of fourteen playbooks, route each step to the skill that owns it, and reply with labelled evidence |

Codex invokes the same workflow as `$chann <task>`. It runs only on its own selector. Without it, call the owning skill directly: `bug-hunt` for a defect, `interrogate` for a diff review, `swarm` for parallel slices, `long-task` for a multi-milestone build.

The playbooks are investigation, bug-fix, perf, feature, refactoring, prototype, plan, review, fan-out, autonomous-run, shipping, pause-and-pickup, docs, and authoring-a-skill. Each step names the skill that owns it. When that skill is installed, the mode loads it; when it is not, the playbook's inline steps apply and the mode never stops to ask for an install. A routed skill keeps its own gates and refusals, and of two safety rules the stricter wins.

Reversible work proceeds without asking. A force-push, a deploy outside the repository's documented settings, deleting data, or a message to anyone outside the session pauses. "자러 간다" or "don't stop" switches to an unattended run that asks nothing, skips and lists every irreversible action, and logs each decision in a decision trail. Work with two or more separable parts is split across delegates, each writer in its own worktree and branch; their branches are merged and the project's checks run on the merged tree.

The reply uses the evidence vocabulary shared across the catalog: verdicts are `VERIFIED`, `NOT VERIFIED`, or `INCONCLUSIVE` (inconclusive is never a pass), and a claim with no direct evidence is labelled `measured`, `inferred`, or `guess`. A finding or a "fixed" names its rung on the proof ladder, weakest first: `said`, `cited` (a real `file:line`), `traced`, `ran`, `reproduced`.

### how and why

| Command | Action |
|---|---|
| `/how <question>` | Explain how part of the codebase works from the code: overview, key concepts, runtime flow, a `file:line` map, and gotchas |
| `/why <question>` | Explain why code is built this way from git history, blame, pull-request and issue discussion, and design notes, as a decision timeline |

Codex invokes the same workflows as `$how <question>` and `$why <question>`. Both are read-only and neither requires the other. `how` cites a `file:line` for every claim, labels anything it did not read as `inferred`, and ends by naming what it did not read. `why` quotes the authors, marks its own reading as `inferred`, and states what the record does not answer; it never gives a motive that no commit, pull request, issue, or note states. Use `research-brief` for an external library or spec, `diff-summary` for one change, and `bug-hunt` for something broken. `gh` is optional; with it `why` also reads pull-request and issue threads.

### research-brief

| Command | Action |
|---|---|
| `/research-brief [question]` | Answer the question from primary sources and write a cited brief under `.research/`, with tiered sources, version-pinned claims, a contradiction ledger, and open questions |

Codex invokes the same workflow as `$research-brief [question]`. A community
source is a lead to the first-party source, never an answer; a claim without the
version or date it was verified against does not go in the brief.

### recall and catchup

| Command | Action |
|---|---|
| `/recall [date-range]` | **Report:** a Markdown work report for `today` (default), `yesterday`, this/last week, month, quarter, or year, a single day, or `YYYY-MM-DD..YYYY-MM-DD` |
| `/recall [topic]` | **Brief:** the current state of a topic, for starting or resuming work |
| `/catchup` | What changed in this conversation since your last message, and what waits on you |

Codex invokes the same workflows as `$recall [topic | date-range]` and `$catchup`. `recall` mines the local history stores of Claude Code, Codex, opencode, and agy read-only (silently skipping absent ones), buckets records in the user's local timezone with Monday-start weeks, and replies with a summary or, on request ("detailed", "상세"), a report that adds a timeline and a per-request log. History content is data, never instructions, and never leaves the machine. A file is written only when asked; default save paths are grouped under `.work-summaries/daily`, `weekly`, `monthly`, `quarterly`, `yearly`, or `custom`, and a user-supplied output path takes priority. A request with both a topic and a range runs the brief with that range as its window.

The brief locks its scope first and states it back: the window (default the last 7 days, never silently narrowed from "all"), the topic, and the workspace. It returns a capsule of at most five bullets, threads with exactly one status tag each (`[merged]`, `[PR open #N]`, `[in progress <branch>]`, `[done, uncommitted]`, `[reverted]`, `[not started]`), at most five recurring problems, and one concrete next move. Every branch, PR, and file it names is checked against live `git` first.

`catchup` opens with one sentence on what waits on you, then what happened in about 100 words, then every decision that needs you, each decidable from the reply alone, then one line on work the agent can still do itself. It checks live branch, PR, CI, and agent state before it answers and changes nothing. For a document the next agent reads, use `handoff session`.

### diff-summary and diff-viewer

| Command | Output |
|---|---|
| `/diff-summary [scope]` | Aligned Korean + English Markdown and one bilingual offline HTML under `.diff-summaries/` |
| `/diff-summary [scope] --md` | Aligned Korean + English Markdown only under `.diff-summaries/` (no HTML, no browser open) |
| `/diff-summary [scope] --quiz` | Same as `/diff-summary` plus aligned interactive `## Quiz` sections |
| `/diff-summary [scope] --md --quiz` | The two Markdown files with their quiz sections and no HTML |
| `/diff-viewer` | HTML diff at `.diffs/<YYYY-MM-DD>_<tag>.html` (view only — no analysis) |

Codex invokes `$diff-summary [scope] [--md] [--quiz]` and `$diff-viewer`. "markdown only" and "마크다운만" select `--md`; "퀴즈" and "quiz me" select `--quiz`. Scopes include the working tree, staged or unstaged changes, the last commit or last N commits, a specific commit, an exact commit range, a branch comparison, and PRs. `diff-summary` validates and preserves an explicit range verbatim: `main..dev` and `main...dev` retain their different Git semantics.

Choose the workflow by the result you need:

| Goal | Workflow | Output contract |
|---|---|---|
| Explain purpose, behavior, architecture, patterns, contracts, tests, and operational implications supported by the diff | `diff-summary` | Descriptive `DS-*` cards without defect severity |
| Save the same explanation as Markdown only, without HTML or a browser open | `diff-summary --md` | Validated Korean and English `.md` artifacts |
| Explain the change and test comprehension | `diff-summary --quiz` | Markdown answer key plus an interactive offline HTML quiz |
| Find correctness, security, or maintainability problems and recommend fixes | `interrogate` | Findings grouped by review severity |
| Find what a change breaks outside the diff | `blast-radius` | The safety fact, its proof, and risks |
| Inspect changed lines without analysis | `diff-viewer` | Unified/split raw patch |

Natural-language requests such as `summarize the code changes`, `코드를 요약해줘`, `main..dev 코드를 요약해줘`, `summarize the last commit`, and `summarize PR #42` select `diff-summary`. When summary and review are both requested, the explanatory cards and review findings remain separate.

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
/absolute/trusted/python3 -I diff-summary/skills/diff-summary/scripts/generate_summary_report.py \
  .diff-summaries/2026-07-13_main-dot2-dev-<hash12>.md \
  -o .diff-summaries/2026-07-13_main-dot2-dev-<hash12>.html \
  --theme auto
```

`--theme` accepts `auto`, `light`, or `dark`. The renderer does not collect a diff or write analytical prose; the skill workflow owns evidence collection and Markdown authoring. Optional `--open` uses a fixed system launcher with ambient `BROWSER` and Python startup variables removed, but host-controlled opening is preferred.

For the skill's default write path, invoke the same script with `--bilingual-json-stdin --output-directory .diff-summaries`, then provide the exact `{"ko":"...","en":"..."}` object through the process's standard-input API. This mode creates only the direct output directory, refuses a symlinked parent, derives collision-safe names itself, and writes two Markdown sources plus one HTML report without a shell redirection or repository-created helper. `--md` adds `--markdown-only` and writes only the two Markdown sources. Explicit single-language requests use the legacy `--markdown-stdin` mode.

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

### plan-summary

| Command | Output |
| --- | --- |
| `/plan-summary <source-path ...>` | Aligned Korean and English Markdown plus bilingual HTML under `.plan-summaries/` |
| `/plan-summary <source-path ...> --md` | The same aligned Markdown pair only; no HTML or browser open |
| `/plan-summary <source-path ...> --quiz` | The bilingual report plus aligned interactive `QZ-*` questions |

Codex uses `$plan-summary` with the same explicit paths and options. Supply only selected `.md`, `.markdown`, or `.txt` UTF-8 files. The workflow never scans a directory or repository, expands a glob, or fetches a URL.

The agent sends `{"paths":["docs/plan.md","docs/design.md"]}` through standard input to `collect_plan_evidence.py`. The collector returns ordered paths, sizes, SHA-256 digests, and exact content as inert JSON. One evidence map then produces Korean and English reports with aligned `PS-*` IDs, categories, and source references. `generate_plan_summary.py --bilingual-json-stdin --output-directory .plan-summaries` validates both sources before atomically writing the artifact set. `--md` adds `--markdown-only`; `--quiz` appends aligned final `## Quiz` sections whose `QZ-*` questions keep identical option counts and answer positions. To find weaknesses in a plan, use `review-me` instead.

### review-me

| Command | Action |
|---|---|
| `/review-me [topic]` | Review one consequential decision at a time until every applicable leaf passes choice, boundary, variant, consequence, and proof checks |

Codex invokes the same contract as `$review-me [topic]`. It runs only on its own selector. With no topic argument,
the skill reviews the plan, design, or decision already under discussion. It
inspects available evidence for discoverable facts, gives a recommended answer
with each question, and waits for one answer before following the next node.
When the decision frontier is empty, it audits every review lens and asks for
confirmation of the closure record; implementation remains outside the review
unless the surrounding request already authorized it. For defects in a Git diff, use `interrogate`.

### swarm and arena

| Command | Action |
|---|---|
| `/swarm <task>` | Fan the task out to subagents or other installed coding agents and write one report with the route rationale and a call tree |
| `/arena <task>` | Run one prompt on separate candidates, have a judge from another vendor score them against a hidden rubric, pick a base, graft the best parts of the others into it, and verify the result |

Codex invokes the same workflows as `$swarm <task>` and `$arena <task>`. `swarm` frames a done predicate and the single return, then picks a shape: `partition` (disjoint slices), `race` (one brief on different routes, under a selection rule fixed before the run), or a mix. It probes Codex, Claude Code, OpenCode 2.x, and Antigravity, keeps the route rationale with any quota transcript, and refuses a plan that invents a quota number or reuses one vendor for independent checks. It reads every `PASS`, `ISSUES`, or `BLOCKED` result itself, reruns an incomplete one once, and records a gap instead of a pass. For a read-only review that a silent edit would invalidate, `--guard` records file hashes, symlink targets, and `HEAD` before and after and fails the task when they differ. When only one usable route exists and the user did not name an agent or model, the work stays in the current session. A multi-milestone project stays with `/long-task`.

`arena` writes a hidden rubric of three to six criteria, gives every candidate the same prompt and its own output location, runs one read-only judge on neutral labels, reads every candidate before picking a base, grafts one or two things from each loser by hand, and verifies the result. It seats candidates through `swarm` when installed, so they land on different vendors. It refuses a mechanical task whose shape is already settled.

### bug-hunt

| Command | Action |
|---|---|
| `/bug-hunt [symptom or failing command]` | Reproduce the defect, falsify one hypothesis per round, pin the fix with a check that fails for the defect's reason, and leave a record under `.bug-hunts/` |

Codex invokes the same workflow as `$bug-hunt [symptom or failing command]`. The
skill reports a non-reproduction instead of fixing speculatively, widens the
search after three falsified hypotheses in one layer, and proves every `BUGHUNT`
probe is removed before it closes.

### gen-docs

| Command | Action |
|---|---|
| `/gen-docs [project-root]` | Generate or update `README.md`, `README.ko.md`, `ARCHITECTURE.md`, `USAGE.md` |

Codex invokes `$gen-docs [project-root]`. It merges by heading, preserves unknown prose (and any section marked `<!-- doc-skill:keep -->`), shows per-file diffs, and writes only after you confirm. With no argument it targets the current working directory.

### unslop

| Command | Action |
|---|---|
| `/unslop [text-or-file]` | Rewrite AI-written Korean or English text into natural, human-sounding prose without changing its meaning |

Codex invokes the same contract as `$unslop [text-or-file]`. In Korean the skill replaces AI-flavored jargon — 계약(contract), 엔벨로프(envelope), 패리티(parity) — and leaked framework vocabulary, then smooths translation-ese style. In English it removes filler openers, inflated vocabulary, "not just X but Y", forced lists of three, and dash and bold overuse, using numbered rules (`E1`–`E21`) whose ids stay stable. Language is detected per passage, so mixed text is handled sentence by sentence. Facts, numbers, proper nouns, code identifiers, quotes, links, and keep-list technical terms (API, 토큰, 프롬프트, 커밋, 멱등, …) never change; unlisted Korean terms are replaced only when a three-part judgment test passes, and doubt keeps the original. It never translates. File input is rewritten to a sibling file (`notes.md` becomes `notes.unslop.md`), never overwritten.

`gen-docs`, `plan-summary`, `handoff`, and `recall` have a self-contained natural-Korean fallback. They may use `unslop` as an optional wording-only pass when the runtime already exposes it, but never install or require it. Missing optional support does not change their output or completion behavior.

### build-reinstall

| Command | Action |
|---|---|
| `/build-reinstall [project-root]` | Build the project, reinstall the new local result, and verify the installed copy |

Codex invokes the same workflow as `$build-reinstall [project-root]`. The skill
runs only after explicit invocation. It prefers optional root
`.build-reinstall.yaml`, then project instructions and declared scripts. Before
execution it shows the exact build and reinstall commands, target paths, smoke
checks, and artifact comparisons. Build failure leaves the installed copy
untouched; full success requires the configured smoke checks and matching
SHA-256 values for declared built and installed files.

### interrogate and blast-radius

| Command | Output |
|---|---|
| `/interrogate [scope]` | Korean + English Markdown and one self-contained bilingual HTML report under `.reviews/`, opened in a browser |
| `/interrogate [scope] --md` | One Markdown report at `.reviews/<YYYY-MM-DD>_<short-sha>.md`; no HTML, no browser |
| `/blast-radius [scope]` | A reply: the safety fact with its proof level, risks with `file:line`, what was cleared, and the cheapest check before merging |

Codex invokes the same workflows as `$interrogate [scope] [--md]` and `$blast-radius [scope]`. "markdown only" and "마크다운만" select `--md`. Scopes are the same as for `diff-summary`: current, staged, or unstaged changes, the last commit or last N commits, a commit, an exact range, a branch comparison, and a PR. An explicit range is preserved exactly.

Every finding carries its proof level and the proof itself, on one ladder, weakest first: `said` (never reported as a finding), `cited` (a real changed `file:line`), `traced` (the failing path walked step by step), `ran` (a command or test printed the failure, pasted with its output), and `reproduced` (seen in the running product). Findings that never reach `cited` are dropped and counted under **Dropped**. CRITICAL and HIGH findings are pushed to `traced` or `ran`; one that stays at `cited` is labelled `cited, not traced`. Proof runs are read-only on the reviewed tree: the project's tests, or a repro script in a temporary directory outside the repository. The review reports; it never applies fixes.

Severity levels are CRITICAL (data loss, security breach, or crash in production), HIGH (bug, vulnerability, or serious design flaw), MEDIUM (code smell or moderate risk), LOW (style or naming), and INFO (verified context that affects a decision, with no code change required). Findings follow observed behavior → practical consequence → smallest justified correction. Ask for a multi-model or adversarial panel and, when `swarm` is installed, the review hands one brief to adversaries on different vendors, reruns every returned command itself, and keeps only findings whose output shows the failure; without `swarm` it reviews in the current session and says the panel was not run.

`blast-radius` reads the change including behavior it changes without saying so, names the one or two facts the change is safe because of, looks where a symbol search stops (the pinned library's own source, timing and teardown, serialized shapes, flags and config, code several hops downstream), and proves each fact as far down the ladder as is cheap, usually one script in a temporary directory. It never invents a caller; "searched, found nothing" is a valid result. Use `diff-summary` to explain a change and `review-me` for the decisions in a plan.

### Shared HTML report interface

`interrogate`, `diff-summary`, `plan-summary`, and `diff-viewer` render
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
| `/git-commit push` | Same, then `git push` (never `--force`) |
| `/git-commit realtime` · `/gcr` | During implementation, verify and commit each meaningful outcome locally — never push |
| `/git-commit push realtime` · `/gcpr` | During implementation, verify, commit, and immediately push each meaningful outcome |
| `/git-commit deploy` · `/gcpd` | Verify, commit, push, deploy, and confirm each outcome using documented repository settings |
| `/git-commit rewrite [range] [force]` | Rewrite recent non-Conventional commit subjects |
| `/git-merge [main \| dev \| <branch>]` | Merge the current branch into the target, then `git branch -d` the source unless protected |
| `/git-cleanup` | Remove finished worktrees and delete every local branch already merged into a protected branch |
| `/git-resolve-conflicts` | Finish a conflicted merge, rebase, cherry-pick, or revert; classify every path, keep both intents where compatible, run the project's checks, and never abort |

Codex invokes the same workflows as `$git-commit [push | deploy] [realtime]`, `$git-commit rewrite [range] [force]`, `$git-merge`, `$git-cleanup`, and `$git-resolve-conflicts`, plus the aliases `$gcr`, `$gcpr`, and `$gcpd`. `gcr`, `gcpr`, and `gcpd` are explicit-only: they never start from natural language, they run the installed `git-commit` with the mode fixed to `realtime`, `push realtime`, and `deploy`, and they refuse when `git-commit` is not installed. A natural-language request such as "commit and push as you work" goes to `git-commit` directly. An ambiguous request takes the less far-reaching mode; `push` and `deploy` are never inferred from silence.

Protected branches — never deleted, never force-anything — are `main`, `master`, `dev`, `develop`, `development`, `stg`, `stage`, `staging`, `root`. Every workflow shows a plan before any commit, merge, or delete; the checkpoint modes pre-authorize their displayed checkpoint sequence while the other mutating workflows wait for confirmation. None run `git add .`, `--no-verify`, or `git branch -D`.

**Checkpoint modes.** `realtime`, `push realtime`, and `deploy` plan outcome-based checkpoints, never time- or file-count-based ones, and commit only green checkpoints verified with the narrowest relevant checks plus `git diff --check`. `realtime` keeps every checkpoint local; publication stays a separate, explicit request. `push realtime` pushes each checkpoint before starting the next, proves `HEAD...@{u}` is `0 0`, and stops rather than auto-reconciling upstream drift.

`deploy` (aliases `/gcpd` and `$gcpd`) adds deployment confirmation to every push realtime checkpoint. It reads the
existing target, command or CI trigger, eligible branch, working directory,
source selection, and checks from `AGENTS.md` or referenced deployment documents
before editing or pushing. Its invocation authorizes repeated deployments to that
target without repeated confirmation, subject to mandatory approval gates. It
observes push-triggered CI once, verifies the exact checkpoint SHA or artifact,
and waits for successful deployment and required smoke checks before starting the
next outcome. Missing or ambiguous settings, failed deployment, timeout, or a
revision mismatch stop the next planned outcome. Source corrections within the
authorized task use a new recovery checkpoint with the same verification and
deployment gates. It preserves pushed history and follows only authorized
provider recovery rules. Deployment inputs exclude unrelated worktree files.

**Rewrite.** `rewrite` determines the range, checks for a clean tree, an attached HEAD, and pushed commits (a Cancel / force-with-lease / new-branch menu, default Cancel), proposes subjects while keeping bodies and moving ticket prefixes to `Refs:` footers, and applies after confirmation. A bare `--force` push happens only in its explicit `force` path.

**Merge.** `git-merge` resolves the target (the argument wins, `dev` falls back to `develop`, and no argument means the default branch from `origin/HEAD`, otherwise `main`; the target must exist locally), refuses a detached HEAD, a dirty tree, or a source equal to the target, shows the plan, and waits for confirmation. It never pushes.

**Cleanup.** `git-cleanup` removes a linked worktree only when it is not the main or current worktree, not locked, has an empty `git status --short`, and its non-protected branch tip is reachable from a protected branch. It then deletes merged branches with `git branch -d`, shows one plan for both, and leaves any refused item in place with the reason. Never `--force`, never `-D`.

### long-task

| Command | Action |
|---|---|
| `/long-task <objective>` | Start an autonomous multi-milestone build |
| `/long-task status` | Show phase, status, elapsed time, and recent progress |
| `/long-task pause` | Stop the Stop-hook auto-continue loop |
| `/long-task resume` | Resume the auto-continue loop |
| `/long-task clear` | Delete `.agent/state.md` (keeps the other `.agent/` files) |
| `/long-task complete` | Run the completion audit and finish the run |

Codex invokes `$long-task` with the same subcommands. `build-reinstall` is separate from `long-task`: completing an autonomous task
does not trigger a reinstall automatically.

### handoff

| Command | Action |
|---|---|
| `/handoff frontend [scope]` | Generate `.handoffs/<date>_<scope>_frontend.md` for frontend/mobile/SDK/client implementers |
| `/handoff backend [scope]` | Generate `.handoffs/<date>_<scope>_backend.md` for backend/server implementers |
| `/handoff session [note]` | Generate `.handoffs/<date>_<slug>_session.md` to hand this session to a fresh agent |
| `/handoff [scope]` | Resolve the audience from the wording, then the diff; both documents when a diff needs both |

Codex invokes `$handoff [frontend | backend | session] [scope]`. The audience is resolved from the argument, then the request's wording, then the diff, and the first line says which one was chosen and why. Scopes can be the current working tree, staged changes, a commit range such as `HEAD~5..HEAD`, a branch comparison such as `main...feature`, or user-provided session context; the user-specified scope is preserved and unverified tests, deploys, or runtime behavior are marked unverified. `frontend` says `client action 없음` when nothing client-visible changed. `session` hands off the session itself, so its scope is the conversation plus the repository state; every claim that something works names the command that proved it, everything else is recorded as unproven, and the document ends with a copyable resume prompt. Secrets are redacted from quoted commands and logs, and nothing is committed or pushed. To rebuild your own context from past work, use `recall`.

### skill-forge, skill-audit, and reflect

| Command | Action |
|---|---|
| `/skill-forge [skill name or request]` | Author or repair a skill package and publish its catalog entry, four locales, counts, and tests in the same change |
| `/skill-audit [skill or repository path]` | Report every packaged skill that violates a contract rule, with the rule, skill, and file |
| `/reflect [session \| repo]` | Keep the lessons that will still hold in six months, route each to the strongest enforcement that works, and stop at Accepted, Rejected, and Backlog lists before editing anything |

Codex invokes the same workflows as `$skill-forge`, `$skill-audit`, and `$reflect`. The audit is read-only unless the
user asks for the repairs, and neither authoring workflow relaxes a contract rule to make
a package pass. Run the auditor directly to use it as a merge gate:

```bash
python3 skill-forge/skills/skill-audit/scripts/audit_skills.py --root .
python3 skill-forge/skills/skill-audit/scripts/audit_skills.py --format markdown
```

`reflect` takes `session` (this conversation, the default) or `repo` (recent commits, reverts, review comments, and agent-instruction files). It prefers a script, lint, test, or hook, then an edit to the skill that owns the behavior, and the agent-instruction file last. Edits happen only after you approve.

## Configuration

### Environment variables

| Variable | Used by | Default | Purpose |
|---|---|---|---|
| `LONG_TASK_MAX_STOP_CONTINUES` | `long-task` | `500` | Cap on automatic Stop-hook continuations (runaway guard) |
| `CLAUDE_SETTINGS` | `long-task` | `~/.claude/settings.json` | Path to the settings file the Stop hook is written to |
| `CC_REWRITE_MAP` | `git-commit rewrite` | `/tmp/cc-rewrite-map.tsv` | Temp old→new message map used during `git filter-branch` |
| `XDG_CACHE_HOME` | `swarm` | `~/.cache` | Base directory for `swarm/runs/<run-id>/` |

### Generated paths

| Path | Written by | Notes |
|---|---|---|
| `.reviews/` | `interrogate` | Markdown / HTML reports; gitignored |
| `.diff-summaries/` | `diff-summary` | Korean + English Markdown sources, plus bilingual self-contained HTML unless `--md`; gitignored |
| `.plan-summaries/` | `plan-summary` | Korean + English Markdown sources, plus bilingual self-contained HTML unless `--md`; gitignored |
| `.diffs/` | `diff-viewer` | HTML diff reports; gitignored |
| `.handoffs/` | `handoff` | Markdown handoff documents |
| `.agent/` | `long-task` | Working-memory and lifecycle state for a run |
| `$XDG_CACHE_HOME/swarm/runs/<run-id>/` | `swarm` | Route rationale, each task result, and the call-tree report. Falls back to `~/.cache/swarm/runs/<run-id>/` |
| `.work-summaries/` | `recall` | Markdown work reports, written only on request; gitignored |
| `.bug-hunts/` | `bug-hunt` | Diagnosis records; gitignored |
| `.research/` | `research-brief` | Cited briefs; gitignored |
| `~/.claude/settings.json` | `long-task` | Stop hook installed under `hooks.Stop` on first run |

`.build-reinstall.yaml` is optional read-only project configuration. The skill
never creates or edits it automatically; copy the packaged
`references/build-reinstall.example.yaml` only when the project needs explicit
commands.

`.reviews/`, `.diff-summaries/`, `.plan-summaries/`, `.diffs/`, `.work-summaries/`, `.bug-hunts/`, and `.research/` are already in this repository's `.gitignore`. In another repository the skills may suggest the matching ignore entry, but never edit `.gitignore` automatically.

## Examples

```
# Run a task through the one entry point
> /chann this endpoint got slow, find out why and fix it

# Try to break a change and persist a bilingual HTML report for staged changes
> /interrogate review staged changes

# Review a plan one decision at a time through every consequential leaf
> /review-me our tenant-by-tenant billing migration

# Summarize current changes, an exact branch range, the last commit, or a PR
> summarize the code changes
> /diff-summary main..dev
> summarize the last commit
> summarize PR #42

# Turn a messy working tree into clean Conventional Commits, then push
> /git-commit push

# Build a longer change and publish each verified outcome as it completes
> /git-commit push realtime

# Deploy each completed outcome using the repository's documented settings
> $gcpd

# Rebuild a finished local project, reinstall it, and verify the installed copy
> /build-reinstall

# Refresh this repo's docs (root from cwd, or pass a path)
> /gen-docs
> /gen-docs ../my-other-project

# Generate role-specific handoffs from exact git scopes
> /handoff frontend main...feature-user-api
> /handoff backend HEAD~5..HEAD
> /handoff session

# Kick off an autonomous build, then check on it later
> /long-task build a REST API for a URL shortener with tests
> /long-task status

# Report what was worked on across coding agents
> /recall this week
> /recall last quarter detailed
> /recall 2026-07-01..2026-07-31 detailed

# Summarize explicit planning documents, optionally as Markdown only or with a quiz
> /plan-summary docs/plan.md docs/design.md
> /plan-summary docs/prd.md --md
> /plan-summary docs/spec.md --quiz
```

## Troubleshooting

| Symptom | Likely cause | Fix |
|---|---|---|
| "Not a git repository" | Skill run outside a git repo | `cd` into a repository |
| "Detached HEAD" | git-skill needs an attached branch | `git checkout <branch>` |
| "Working tree has uncommitted changes" | merge/rewrite needs a clean tree | commit or `git stash` first |
| `/git-merge main` aborts | `main` doesn't exist locally | create it, or merge into `dev` or another local branch |
| Commit rejected by a hook | a pre-commit hook failed | fix the root cause — the skills won't `--no-verify` |
| `/git-commit rewrite` stops on pushed commits | rewriting published history | pick the branch-based option, or pass `force` to accept the rewrite |
| `/gcr`, `/gcpr`, or `/gcpd` refuses to run | `git-commit` is not installed beside the alias | `npx skills add chann/skills --skill git-commit` |
| `/git-cleanup` leaves a worktree or branch | it has changes, is locked, or is not reachable from a protected branch | finish or merge it first; the skill never forces |
| No HTML report generated | Python 3.10+ missing | install Python 3.10 or newer |
| `/diff-summary` reports an invalid or empty scope | The requested ref/range is unresolved or contains no changes | Correct the exact scope; the skill will not silently fall back to the working tree |
| `/interrogate` wrote no file | Report generation did not complete | inspect the warning in the reply and rerun `/interrogate`; use `/interrogate --md` only when HTML is not wanted |
| `/plan-summary` asks for a source | No explicit file was supplied | pass one or more `.md`, `.markdown`, or `.txt` UTF-8 paths; the skill will not auto-discover documents |
| `/swarm` keeps the work in this session | Only one usable route exists and no agent was named | install or name another coding agent (`codex`, `claude`, `opencode` 2.0.0+, or `agy`) |
| `/build-reinstall` stops before install | Build, target, or verification evidence is ambiguous | add project instructions or copy and fill `references/build-reinstall.example.yaml` as `.build-reinstall.yaml` |
| Reinstall command exits zero but verification fails | Smoke check failed or installed SHA-256 differs from the built file | keep the result marked failed and inspect the exact command or artifact pair |
| `/chann` seems to do nothing for a plain request | It runs only on its own selector | type `/chann <task>` or `$chann <task>`, or call the owning skill directly |
| long-task won't auto-continue | `.agent/state.md` missing or not `active` | run `/long-task` to start, or `/long-task resume` |
| long-task stopped early | hit `LONG_TASK_MAX_STOP_CONTINUES` | raise it, e.g. `export LONG_TASK_MAX_STOP_CONTINUES=1000` |

## Requirements

- An agent platform that supports skills (Claude Code, Codex, Antigravity CLI, Grok Build, Pi, Gemini CLI, GitHub Copilot CLI, OpenCode, …)
- A Git repository
- Git 2.45+ for `diff-summary`
- Python 3.10+ for `interrogate`, `diff-summary`, `diff-viewer`, `plan-summary`, `git-commit rewrite`, `swarm`, `long-task`, and `skill-audit` (standard library only — nothing to install)
- `gh` is optional; `why` reads pull-request and issue threads through it, and a `recall` brief uses it for PR state
