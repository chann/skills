# skills

[🇰🇷 Korean](README.ko.md)

31 practical agent workflows and 32 installable Codex selectors, packaged across 13 plugins.

## Website

The [live interactive catalog](https://chann.github.io/skills/) explains every
skill, shows the exact Claude Code and Codex selectors, and provides copyable
install and usage examples. Its source and maintenance notes live in
[`website/`](website/README.md).

```bash
npm --prefix website ci
npm --prefix website run dev
```

Pushes to `main` deploy the `website/dist/` bundle to GitHub Pages.

## Skills


| Skill                                    | What it does                                                                                                   |
| ---------------------------------------- | -------------------------------------------------------------------------------------------------------------- |
| **[code-review](code-review/README.md)** | Analyze Git changes with explanatory diff summaries, severity-based reviews, and a raw HTML diff viewer     |
| **[review-me](review-me/README.md)**     | Review every important plan or design decision, one at a time, until nothing is left unresolved             |
| **[bug-hunt](bug-hunt/README.md)**       | Diagnose a broken behavior by reproducing it, falsifying hypotheses in a ledger, and pinning the fix with a failing check |
| **[research-brief](research-brief/README.md)** | Answer a technical question from primary sources and leave a cited brief with tiered, version-pinned claims |
| **[doc-skill](doc-skill/README.md)**     | Generate or update README, Korean README, architecture, and usage docs while preserving existing prose      |
| **[git-skill](git-skill/README.md)**     | Conventional Commits, validated work-unit commits or pushes, history rewrite, main/dev merges, conflict resolution, and local branch cleanup |
| **[handoff](handoff/README.md)**         | Generate frontend/client, backend/server, and session-to-session handoff docs from git diffs, ranges, and session context |
| **[long-task](long-task/README.md)**     | Run multi-milestone projects autonomously with parallel worktree subagents and milestone reviews             |
| **[build-reinstall](build-reinstall/README.md)** | Build a local project, reinstall the new result with project-owned commands, and verify the installed copy |
| **[work-summary](work-summary/README.md)** | Date-ranged Markdown reports of coding-agent work mined from local Claude Code, Codex, opencode, and agy history |
| **[plan-summary](plan-summary/README.md)** | Bilingual summaries of explicit plans, PRDs, specifications, and designs, with Markdown-only and quiz variants |
| **[human-friendly-writing](human-friendly-writing/README.md)** | Rewrite AI-written Korean into natural prose by removing awkward jargon and smoothing the style without changing meaning |
| **[skill-forge](skill-forge/README.md)** | Author skill packages against one contract and audit every packaged skill against it |


## Installation

Install all skills globally for Claude Code, Codex, Antigravity CLI, Gemini
CLI, GitHub Copilot CLI, and OpenCode with the installer's symlink mode
(recommended):

```bash
npx skills add chann/skills \
  --skill '*' \
  --agent claude-code codex antigravity-cli gemini-cli \
    github-copilot opencode \
  --global \
  --yes
```

The explicit agent list is intentional. With `skills@1.5.19`, using `--global
--yes` without `--agent` can add the project-only PromptScript adapter. Every
skill then reports one misleading failure even though installation succeeded
for the supported targets.

The command above selects every skill and excludes PromptScript. It also keeps
the default symlink mode because it does not use `--copy`. Add other agent IDs
that support global installation if needed, but continue to list the targets
explicitly until
[the upstream fix](https://github.com/vercel-labs/skills/pull/1561) lands. This
prevents this CLI version from falling back to copy mode.

Per-skill or non-global installs (and manual setup) are documented in each skill's README:

- [code-review installation](code-review/README.md#installation)
- [review-me installation](review-me/README.md#installation)
- [bug-hunt installation](bug-hunt/README.md#installation)
- [research-brief installation](research-brief/README.md#installation)
- [doc-skill installation](doc-skill/README.md#installation)
- [git-skill installation](git-skill/README.md#installation)
- [handoff installation](handoff/README.md#installation)
- [long-task installation](long-task/README.md#installation)
- [build-reinstall installation](build-reinstall/README.md#installation)
- [work-summary installation](work-summary/README.md#installation)
- [plan-summary installation](plan-summary/README.md#installation)
- [human-friendly-writing installation](human-friendly-writing/README.md#installation)
- [skill-forge installation](skill-forge/README.md#installation)

- Handoff only: `npx skills add chann/skills --skill gen-frontend-handoff --skill gen-backend-handoff --skill gen-session-handoff`
- Backend handoff only: `npx skills add chann/skills --skill gen-backend-handoff`
- Diff summary only: `npx skills add chann/skills --skill diff-summary`
- Review-me only: `npx skills add chann/skills --skill review-me`
- Work summary only: `npx skills add chann/skills --skill work-summary`
- Build-reinstall only: `npx skills add chann/skills --skill build-reinstall`
- Plan-summary family: `npx skills add chann/skills --skill plan-summary --skill plan-summary-md --skill plan-summary-quiz`
- Human-friendly-writing only: `npx skills add chann/skills --skill human-friendly-writing`
- Codex `$gcpr`: `npx skills add chann/skills --skill gcpr --skill git-commit-push-realtime --skill git-commit --skill git-commit-push`

## Quick reference

Use `/skill-name` in Claude Code and `$skill-name` in Codex. Every row below
spells out both explicit selectors.

### code-review → [details](code-review/README.md)


| Claude Code                      | Codex                       | Output                                                                                          |
| -------------------------------- | --------------------------- | ----------------------------------------------------------------------------------------------- |
| `/code-review [scope]`           | `$code-review [scope]`      | Write markdown + bilingual HTML review reports to `.reviews/`                                    |
| `/code-review-md [scope]`        | `$code-review-md [scope]`   | Write a markdown-only review to `.reviews/`                                                       |
| `/diff-summary [scope]`          | `$diff-summary [scope]`     | Explain changes in Korean + English Markdown and one bilingual interactive HTML under `.diff-summaries/` |
| `/diff-summary-md [scope]`       | `$diff-summary-md [scope]`  | Explain changes in Korean + English Markdown only under `.diff-summaries/` (no HTML, no browser) |
| `/diff-summary-quiz [scope]`     | `$diff-summary-quiz [scope]` | Same as `/diff-summary`, plus matching interactive comprehension quizzes                         |
| `/diff-viewer`                   | `$diff-viewer`              | Render the raw working-tree diff to `.diffs/`                                                    |

`diff-summary` also activates from requests such as “summarize the code changes,” “summarize the last commit,” and “main..dev summary.” By default, it produces matching Korean and English reports with Korean shown first. Request one language explicitly for single-language mode. Ask for “Markdown only” to use `diff-summary-md`, or “quiz me on this diff” to use `diff-summary-quiz`. All three preserve explicit `..` and `...` ranges exactly. Use `code-review` to find defects and `diff-viewer` to inspect the raw patch.

Every HTML report — review, summary, quiz, and raw diff — uses the same interface. It includes a Korean/English toggle, light/dark/system themes with a light print palette, status colors that meet WCAG AA in both themes, Korean-aware line breaks at 어절 boundaries, and keyboard support with a skip link and live region. Each report is a self-contained file that works without a server or network connection.


### review-me → [details](review-me/README.md)


| Claude Code | Codex | Action |
| ----------- | ----- | ------ |
| `/review-me [topic]` | `$review-me [topic]` | Follow every important plan or design decision and confirm that none remain unresolved |

`review-me` asks about one decision at a time and recommends a concrete answer.
When an answer creates more choices, it follows those too. It checks available
evidence for facts and keeps the review read-only until every decision is
recorded and confirmed.


### doc-skill → [details](doc-skill/README.md)


| Claude Code | Codex       | Action                                                                 |
| ----------- | ----------- | ---------------------------------------------------------------------- |
| `/gen-docs` | `$gen-docs` | Generate or update README, Korean README, architecture, and usage docs |


### git-skill → [details](git-skill/README.md)


| Claude Code                      | Codex                       | Action                                                                                |
| -------------------------------- | --------------------------- | ------------------------------------------------------------------------------------- |
| `/git-commit`                    | `$git-commit`               | Group working-tree changes into Conventional Commits                                  |
| `/git-commit-push`               | `$git-commit-push`          | Same, then `git push` (no `--force`)                                                   |
| `/git-commit-push-realtime` · `/gcpr` | `$git-commit-push-realtime` · `$gcpr` | Commit and push each verified, meaningful outcome while implementation continues |
| `/git-commit-realtime` · `/gcr` | `$git-commit-realtime` | Commit each verified, meaningful outcome locally while implementation continues — no push |
| `/git-commit-rewrite`            | `$git-commit-rewrite`       | Rewrite recent non-Conventional commit subjects                                       |
| `/git-merge-to-main`             | `$git-merge-to-main`        | Merge current branch into `main`, then `git branch -d` the source                     |
| `/git-merge-to-dev`              | `$git-merge-to-dev`         | Merge current branch into `dev` (fallback `develop`), then `git branch -d` the source |
| `/git-branch-cleanup`            | `$git-branch-cleanup`       | Delete every local branch already merged into a protected branch                      |
| `/git-resolve-conflicts`         | `$git-resolve-conflicts`    | Finish a conflicted merge, rebase, cherry-pick, or revert without aborting it          |


### long-task → [details](long-task/README.md)


| Claude Code  | Codex        | Action                                                                                       |
| ------------ | ------------ | -------------------------------------------------------------------------------------------- |
| `/long-task` | `$long-task` | Autonomously build a project end-to-end with parallel worktree subagents + milestone reviews |


Also triggers on phrases like *"build this whole project"*, *"do this autonomously"*, *"run a long task"*.

### build-reinstall → [details](build-reinstall/README.md)

| Claude Code | Codex | Action |
| --- | --- | --- |
| `/build-reinstall [project-root]` | `$build-reinstall [project-root]` | Build, reinstall, and verify the installed local result |

`build-reinstall` runs only when explicitly requested. It reads project-owned
instructions or optional `.build-reinstall.yaml`, shows the exact commands and
targets, builds before changing the installed copy, then runs smoke checks and
compares declared built/installed files with SHA-256.

### handoff → [details](handoff/README.md)


| Claude Code               | Codex                    | Action                                                                            |
| ------------------------- | ------------------------ | --------------------------------------------------------------------------------- |
| `/gen-frontend-handoff`   | `$gen-frontend-handoff`  | Write a frontend/client handoff from backend API diffs, ranges, or session context |
| `/gen-backend-handoff`    | `$gen-backend-handoff`   | Write a backend/server handoff from code, API, DB, job, or rollout changes         |
| `/gen-session-handoff`    | `$gen-session-handoff`   | Hand this session to a fresh agent: proven vs unproven state, decisions, traps, next actions, resume prompt |

### work-summary → [details](work-summary/README.md)


| Claude Code | Codex | Action |
| ----------- | ----- | ------ |
| `/work-summary [range]` | `$work-summary [range]` | Generate a Markdown work report for a day, week, month, quarter, year, or custom date span |

`work-summary` reads the local session history of Claude Code, Codex, opencode,
and agy without modifying it. It groups activity in your local timezone and
reports what was requested and completed — a summary by default, or a detailed
report with a timeline and request log. It also triggers on phrases like
*"오늘 작업 요약해줘"* and *"what did I work on this week"*. Saved reports
are grouped under `.work-summaries/daily`, `weekly`, `monthly`, `quarterly`,
`yearly`, or `custom` unless an explicit path is supplied.

### plan-summary → [details](plan-summary/README.md)

| Claude Code | Codex | Output |
| --- | --- | --- |
| `/plan-summary [source-path ...]` | `$plan-summary [source-path ...]` | Matching Korean/English Markdown plus bilingual HTML under `.plan-summaries/` |
| `/plan-summary-md [source-path ...]` | `$plan-summary-md [source-path ...]` | Matching Korean/English Markdown only |
| `/plan-summary-quiz [source-path ...]` | `$plan-summary-quiz [source-path ...]` | The bilingual report plus corresponding `QZ-*` comprehension quizzes |

The three selectors read only explicit `.md`, `.markdown`, or `.txt` UTF-8 files. They never auto-discover documents. Reports share ordered source digests and `PS-*` evidence cards; the Markdown-only selector emits no HTML, while the quiz selector adds accessible offline interaction.

### bug-hunt → [details](bug-hunt/README.md)

| Claude Code | Codex | Action |
| ----------- | ----- | ------ |
| `/bug-hunt [symptom-or-failing-command]` | `$bug-hunt [symptom-or-failing-command]` | Reproduce, falsify hypotheses, pin the fix, and leave a diagnosis record |

`bug-hunt` keeps the trail most debugging throws away. Every hypothesis is
written with the observation that would falsify it, falsified hypotheses stay in
the record so the next session does not retry them, and three failures inside one
layer force the search to widen. The fix lands only after a check fails for the
defect's own reason, and the record goes to `.bug-hunts/`. Reports a
non-reproduction rather than guessing at a fix.

### research-brief → [details](research-brief/README.md)

| Claude Code | Codex | Action |
| ----------- | ----- | ------ |
| `/research-brief [question]` | `$research-brief [question]` | Answer a technical question from primary sources and write a cited brief |

Every claim carries its source, that source's tier, and the version or date it
was verified against. T1 is the spec or the first-party source code; T3 community
material is a lead to T1, never an answer. Disagreeing sources both stay, with the
resolution and its reason. The bottom line and its confidence sit at the top, and
the open-questions section is mandatory even when empty.

### skill-forge → [details](skill-forge/README.md)

| Claude Code | Codex | Action |
| ----------- | ----- | ------ |
| `/skill-forge [skill-name-or-request]` | `$skill-forge [skill-name-or-request]` | Author or repair a skill package and publish every surface it needs |
| `/skill-audit [skill-or-path]` | `$skill-audit [skill-or-path]` | Report every packaged skill that violates the skill contract |

Every skill in this repository satisfies the same nine rules — name parity,
description grammar, invocation mode, Codex descriptor, slash command, evals,
catalog and locale parity, plugin manifest, and published counts. `skill-forge`
writes a package that satisfies them; `skill-audit` proves an existing one still
does, and exits non-zero so it works as a merge gate.

### human-friendly-writing → [details](human-friendly-writing/README.md)

| Claude Code | Codex | Action |
| ----------- | ----- | ------ |
| `/human-friendly-writing [text-or-file]` | `$human-friendly-writing [text-or-file]` | Rewrite AI-written Korean text into natural prose without changing meaning |

`human-friendly-writing` replaces AI-flavored jargon — 계약(contract),
엔벨로프(envelope), 패리티(parity), leaked framework vocabulary — and smooths
translation-ese style while preserving facts, numbers, and established
technical terms. Also triggers on phrases like *"AI 용어 없애줘"* and *"사람답게
다듬어줘"*.

`gen-docs`, the plan-summary family, both handoff generators, and `work-summary`
include their own natural-Korean rules. When `human-friendly-writing` is already
available they may use it as an optional final pass, but every selector remains
fully functional when installed alone.

## Documentation

- [Usage](USAGE.md) — install, full command reference, configuration, examples, and troubleshooting
- [Architecture](ARCHITECTURE.md) — components, data flow, directory map, and design decisions

## Use on other agent platforms

All `SKILL.md` files in this repo follow the standard skill format and reference no Claude-Code-only tools, so they run on any agent platform that supports skills:


| Platform                                        | How to install                                                                                |
| ----------------------------------------------- | --------------------------------------------------------------------------------------------- |
| **[Claude Code](https://code.claude.com)**      | `npx skills add chann/skills` — installs the full plugin (skill + slash commands)             |
| **[Codex](https://github.com/openai/codex)**    | Symlink `<plugin>/skills/<name>/` into your Codex skills directory (e.g. `~/.agents/skills/`) |
| **[opencode](https://github.com/sst/opencode)** | Drop the skill directory into your opencode skills path                                       |
| **Copilot CLI / Gemini CLI / others**           | Point your platform's skill loader at `<plugin>/skills/<name>/SKILL.md` per its docs          |


What works across platforms and what is specific to Claude Code:

- **Portable** — every `SKILL.md` body and its `references/`. The skills trigger on natural-language phrases on any platform.
- **Claude Code only** — the `.claude-plugin/plugin.json` wrapper, the `npx skills` installer, and the slash commands (`/code-review`, `/git-commit`, `/long-task`, ...). Other platforms invoke the skill with natural language or their own calling convention.

## Requirements

- An agent platform that supports skills (Claude Code, Codex, opencode, Copilot CLI, Gemini CLI, etc.)
- Git repository
- Git 2.45+ for `diff-summary`, `diff-summary-md`, and `diff-summary-quiz`
- Python 3.10+ (for `code-review`, `diff-summary`, `diff-summary-md`, `diff-summary-quiz`, `diff-viewer`, `plan-summary`, `plan-summary-md`, `plan-summary-quiz`, and `git-commit-rewrite`)

## License

MIT
