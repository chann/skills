# skills

[🇰🇷 Korean](README.ko.md)

29 practical agent workflows and 33 installable Codex selectors, packaged across 19 plugins.

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

## Start here

`chann` is the one entry point. Give it a task, and it restates the goal
and the least change that satisfies it, picks a playbook, hands each step to the
skill that owns it when that skill is installed, and replies with labelled
evidence. It runs only on its own selector. Every other skill is situational:
the mode routes to it, and you can call it directly.

```text
/chann 로그인하면 가끔 500 에러가 나, 원인 찾아서 고쳐줘
$chann this endpoint got slow, find out why and fix it
/chann 자러 간다, 이 마이그레이션 테스트 전부 통과할 때까지 해줘
```

## Skills

Eight stages, one row per workflow. Each name links to its plugin README.

| Stage | Skill | What it does |
| --- | --- | --- |
| mode | **[chann](chann-mode/README.md)** | Explicit-only entry point: restate the goal, match one of 22 playbooks, route each step to the skill that owns it, and reply with labelled evidence |
| understand | **[how](understand/README.md)** | Explain how part of the codebase works from the code, with `file:line` citations and no edits |
| understand | **[why](understand/README.md)** | Explain why code is built this way from commits, blame, pull-request and issue threads, and design notes, quoting the authors |
| understand | **[research-brief](research-brief/README.md)** | Answer a technical question from primary sources and leave a cited brief with tiered, version-pinned claims |
| understand | **[recall](recall/README.md)** | Report past coding-agent work from local Claude Code, Codex, opencode, and agy history, or brief the current state of a topic |
| understand | **[catchup](recall/README.md)** | Catch you up on this conversation: what waits on you, what happened, and each decision you must make |
| understand | **[diff-summary](diff-summary/README.md)** | Explain a diff, branch, commit, or PR as aligned Korean and English Markdown plus interactive HTML; `--md` for Markdown only, `--quiz` to add a quiz |
| understand | **[plan-summary](plan-summary/README.md)** | Summarize explicit plans, PRDs, specifications, and designs the same way, with `--md` and `--quiz` |
| understand | **[diff-viewer](diff-summary/README.md)** | Render the raw working-tree diff as a browser-readable HTML report, without analysis |
| design | **[review-me](review-me/README.md)** | Review a plan or design one decision at a time until nothing is left unresolved; explicit-only |
| design | **[arena](swarm/README.md)** | Race several attempts at one artifact, have a judge from another vendor score them, and graft the best parts onto one base |
| build | **[bug-hunt](bug-hunt/README.md)** | Diagnose a broken behavior by reproducing it, falsifying hypotheses in a ledger, and pinning the fix with a check that fails first |
| build | **[gen-docs](doc-skill/README.md)** | Generate or update README, Korean README, architecture, and usage docs while preserving existing prose |
| build | **[unslop](unslop/README.md)** | Rewrite AI-written Korean or English text so it reads like a person wrote it, without changing its meaning |
| build | **[no-comments](no-comments/README.md)** | Remove comments that only narrate the code, keep an outside-rule comment that cannot be checked, and encode a real constraint in a type, test, or lint |
| build | **[make-bot-ui](make-bot-ui/README.md)** | Build a page whose controls wake a bot through a webhook you supply, with the sender key kept in server-side config |
| build | **[build-reinstall](build-reinstall/README.md)** | Build a local project, reinstall the result with project-owned commands, and verify the installed copy |
| verify | **[interrogate](interrogate/README.md)** | Try to break a diff and report severity-tagged findings, each with its proof level, as Markdown plus bilingual HTML |
| verify | **[blast-radius](interrogate/README.md)** | Show what a change could break outside its own diff, and prove the fact its safety rests on |
| ship | **[git-commit](git-skill/README.md)** | Conventional Commits once, with a push, as verified checkpoints, with final integration into `main`, with per-checkpoint deploys, or a subject rewrite; aliases `gcr`, `gcpr`, `gcprm`, `gcpd` |
| ship | **[git-merge](git-skill/README.md)** | Merge the current branch into `main`, `dev`, or another local branch, then delete the source with `git branch -d` unless it is protected |
| ship | **[git-resolve-conflicts](git-skill/README.md)** | Finish a stopped merge, rebase, cherry-pick, or revert without aborting it |
| ship | **[git-cleanup](git-skill/README.md)** | Remove finished worktrees and delete local branches already merged into a protected branch |
| delegate | **[swarm](swarm/README.md)** | Fan a job out to subagents or other installed coding agents and return one report with the route rationale and a call tree |
| delegate | **[long-task](long-task/README.md)** | Run a multi-milestone project autonomously with parallel worktree subagents and milestone reviews |
| delegate | **[handoff](handoff/README.md)** | Write a frontend, backend, or session handoff that separates proven state from unproven |
| meta | **[skill-forge](skill-forge/README.md)** | Author or repair a skill package against one contract and publish every surface it needs |
| meta | **[skill-audit](skill-forge/README.md)** | Report every packaged skill that violates the contract, with a non-zero exit for merge gates |
| meta | **[reflect](skill-forge/README.md)** | Turn what a session or repository taught into enforcement, after your approval |

## Installation

Install all skills globally for Claude Code, Codex, Antigravity CLI, Grok
Build, Pi, Gemini CLI, GitHub Copilot CLI, and OpenCode (recommended):

```bash
npx skills add chann/skills \
  --skill '*' \
  --agent claude-code codex antigravity-cli grok pi gemini-cli \
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

Verified with `skills@1.9.0` in a clean temporary `HOME`. The installer writes
one copy to `~/.agents/skills/<name>/`, which Codex, Pi, Gemini CLI, GitHub
Copilot CLI, and OpenCode read from directly. It then symlinks that copy into
the agents that use their own directory:

| Agent | `--agent` ID | Global path |
|---|---|---|
| Claude Code | `claude-code` | `~/.claude/skills/<name>` (symlink) |
| Codex | `codex` | `~/.agents/skills/<name>` |
| Antigravity CLI | `antigravity-cli` | `~/.gemini/config/skills/<name>` (symlink) |
| Grok Build | `grok` | `~/.grok/skills/<name>` (symlink) |
| Pi | `pi` | `~/.agents/skills/<name>` |
| Gemini CLI | `gemini-cli` | `~/.agents/skills/<name>` |
| GitHub Copilot CLI | `github-copilot` | `~/.agents/skills/<name>` |
| OpenCode | `opencode` | `~/.agents/skills/<name>` |

Drop `--global` to install into the current project instead. The agent IDs and
paths come from the installer's
[supported-agents list](https://github.com/vercel-labs/skills/blob/main/docs/agents.md),
which can change between releases; `npx skills --help` shows the current set.

Install only what you need with `--skill <name>`. Every skill works when
installed alone; the thin aliases `gcr`, `gcpr`, `gcprm`, and `gcpd` are the one
exception and need `git-commit` beside them.

- Entry point only: `npx skills add chann/skills --skill chann`
- Understand a codebase: `npx skills add chann/skills --skill how --skill why`
- Review a change: `npx skills add chann/skills --skill interrogate --skill blast-radius`
- Explain a change: `npx skills add chann/skills --skill diff-summary --skill diff-viewer`
- Git workflow with the short aliases: `npx skills add chann/skills --skill git-commit --skill gcr --skill gcpr --skill gcprm --skill gcpd --skill git-merge --skill git-resolve-conflicts --skill git-cleanup`
- Handoff only: `npx skills add chann/skills --skill handoff`
- Subagents and competing attempts: `npx skills add chann/skills --skill swarm --skill arena`
- Past work and catch-up: `npx skills add chann/skills --skill recall --skill catchup`
- Natural prose: `npx skills add chann/skills --skill unslop`
- Comment cleanup: `npx skills add chann/skills --skill no-comments`
- A page that wakes a bot: `npx skills add chann/skills --skill make-bot-ui`
- Skill authoring: `npx skills add chann/skills --skill skill-forge --skill skill-audit --skill reflect`

To inspect the available names first, run `npx skills add chann/skills -l --full-depth`.
Each plugin README documents its own global and project-local install.

## Quick reference

Use `/skill-name` in Claude Code and `$skill-name` in Codex. In Pi, use `/skill:skill-name`, for example `/skill:diff-summary --md`. Every row below
spells out both explicit selectors with their arguments. Former variant
commands are arguments now: `/diff-summary --md`, `/git-commit push realtime`,
`/handoff session`.

### chann-mode → [details](chann-mode/README.md)

| Claude Code | Codex | Action |
| --- | --- | --- |
| `/chann <task>` | `$chann <task>` | Run the task through a playbook, routed skills, and an evidence-labelled reply |

### understand → [details](understand/README.md)

| Claude Code | Codex | Action |
| --- | --- | --- |
| `/how <question>` | `$how <question>` | Explain how the code works, with `file:line` citations |
| `/why <question>` | `$why <question>` | Explain why it is built this way, as a quoted decision timeline |

### research-brief → [details](research-brief/README.md)

| Claude Code | Codex | Action |
| --- | --- | --- |
| `/research-brief [question]` | `$research-brief [question]` | Answer a technical question from primary sources and write a cited brief under `.research/` |

### recall → [details](recall/README.md)

| Claude Code | Codex | Action |
| --- | --- | --- |
| `/recall [topic \| date-range]` | `$recall [topic \| date-range]` | A Markdown work report for a date range, or a brief on where a topic stands |
| `/catchup` | `$catchup` | What changed in this conversation since your last message |

### diff-summary → [details](diff-summary/README.md)

| Claude Code | Codex | Output |
| --- | --- | --- |
| `/diff-summary [scope]` | `$diff-summary [scope]` | Korean + English Markdown and one bilingual interactive HTML under `.diff-summaries/` |
| `/diff-summary [scope] --md` | `$diff-summary [scope] --md` | Korean + English Markdown only; no HTML, no browser |
| `/diff-summary [scope] --quiz` | `$diff-summary [scope] --quiz` | The same artifacts plus aligned comprehension quizzes |
| `/diff-viewer` | `$diff-viewer` | Render the raw working-tree diff to `.diffs/` |

An explicit `..` or `...` range is preserved exactly. Use `interrogate` to find
defects and `diff-viewer` to inspect the raw patch.

### plan-summary → [details](plan-summary/README.md)

| Claude Code | Codex | Output |
| --- | --- | --- |
| `/plan-summary <path ...>` | `$plan-summary <path ...>` | Matching Korean/English Markdown plus bilingual HTML under `.plan-summaries/` |
| `/plan-summary <path ...> --md` | `$plan-summary <path ...> --md` | Matching Korean/English Markdown only |
| `/plan-summary <path ...> --quiz` | `$plan-summary <path ...> --quiz` | The bilingual report plus corresponding `QZ-*` comprehension quizzes |

Only explicit `.md`, `.markdown`, or `.txt` UTF-8 files are read. Nothing is
auto-discovered.

### review-me → [details](review-me/README.md)

| Claude Code | Codex | Action |
| --- | --- | --- |
| `/review-me [topic]` | `$review-me [topic]` | Follow every consequential plan or design decision until none remain unresolved |

`review-me` runs only on its selector. It asks one question at a time with a
recommended answer, and stays read-only until every decision is recorded and
confirmed.

### swarm → [details](swarm/README.md)

| Claude Code | Codex | Action |
| --- | --- | --- |
| `/swarm <task>` | `$swarm <task>` | Fan the task out to subagents or other coding agents and report with a call tree |
| `/arena <task>` | `$arena <task>` | Run competing attempts at one artifact, cross-judge them, and graft the best parts |

### bug-hunt → [details](bug-hunt/README.md)

| Claude Code | Codex | Action |
| --- | --- | --- |
| `/bug-hunt [symptom-or-failing-command]` | `$bug-hunt [symptom-or-failing-command]` | Reproduce, falsify hypotheses, pin the fix, and leave a record under `.bug-hunts/` |

### doc-skill → [details](doc-skill/README.md)

| Claude Code | Codex | Action |
| --- | --- | --- |
| `/gen-docs [project-root]` | `$gen-docs [project-root]` | Generate or update README, Korean README, architecture, and usage docs |

### unslop → [details](unslop/README.md)

| Claude Code | Codex | Action |
| --- | --- | --- |
| `/unslop [text-or-file]` | `$unslop [text-or-file]` | Rewrite AI-written Korean or English text into natural prose without changing meaning |

### no-comments → [details](no-comments/README.md)

| Claude Code | Codex | Action |
| --- | --- | --- |
| `/no-comments [files or diff]` | `$no-comments [files or diff]` | Strip narration comments and encode a real constraint when you agree |

The reviewer prompt reports. Accepted deletions are applied afterwards. A rejected review does not abort accepted findings. A comment about an outside rule that cannot be checked is kept and marked for review.

### make-bot-ui → [details](make-bot-ui/README.md)

| Claude Code | Codex | Action |
| --- | --- | --- |
| `/make-bot-ui [webhook url]` | `$make-bot-ui [webhook url]` | Build a page whose controls wake a bot through your webhook |

The webhook URL comes from you. The sender key stays in server-side config. A key pasted in chat is refused. The local server, not the browser, sends the POST.

### build-reinstall → [details](build-reinstall/README.md)

| Claude Code | Codex | Action |
| --- | --- | --- |
| `/build-reinstall [project-root]` | `$build-reinstall [project-root]` | Build, reinstall, and verify the installed local result |

`build-reinstall` runs only when explicitly requested.

### interrogate → [details](interrogate/README.md)

| Claude Code | Codex | Output |
| --- | --- | --- |
| `/interrogate [scope]` | `$interrogate [scope]` | Korean + English Markdown and one bilingual HTML under `.reviews/` |
| `/interrogate [scope] --md` | `$interrogate [scope] --md` | One Markdown report under `.reviews/`; no HTML, no browser |
| `/blast-radius [scope]` | `$blast-radius [scope]` | A reply: the safety fact with its proof, risks, what was cleared, and the cheapest pre-merge check |

Every finding carries its proof level, weakest first: `said`, `cited`,
`traced`, `ran`, `reproduced`. Findings that never reach `cited` are dropped
and counted. The review reports; it never applies fixes.

### git-skill → [details](git-skill/README.md)

| Claude Code | Codex | Action |
| --- | --- | --- |
| `/git-commit` | `$git-commit` | Group working-tree changes into Conventional Commits, once |
| `/git-commit push` | `$git-commit push` | The same, then an ordinary `git push` (never `--force`) |
| `/git-commit realtime` · `/gcr` | `$git-commit realtime` · `$gcr` | Commit each verified outcome while working; every checkpoint stays local |
| `/git-commit push realtime` · `/gcpr` | `$git-commit push realtime` · `$gcpr` | Commit each verified checkpoint and push it to the same-name remote source branch |
| `/git-commit push realtime merge-main` · `/gcprm` | `$git-commit push realtime merge-main` · `$gcprm` | Push checkpoints the same way. At completion, integrate the source into `main`, run checks, and push `main`. Keep the source branch. |
| `/git-commit deploy` · `/gcpd` | `$git-commit deploy` · `$gcpd` | Commit, push, deploy, and confirm each outcome using documented repository settings |
| `/git-commit rewrite [range] [force]` | `$git-commit rewrite [range] [force]` | Rewrite recent non-conformant commit subjects |
| `/git-merge [main \| dev \| <branch>]` | `$git-merge [main \| dev \| <branch>]` | Merge the current branch into the target, then delete the source unless protected |
| `/git-resolve-conflicts` | `$git-resolve-conflicts` | Finish a conflicted merge, rebase, cherry-pick, or revert without aborting it |
| `/git-cleanup` | `$git-cleanup` | Remove finished worktrees and delete local branches already merged into a protected branch |

`/gcr`, `/gcpr`, `/gcprm`, `/gcpd` and their `$` forms are explicit-only aliases of the
four checkpoint modes. They need `git-commit` installed and refuse without it.

### long-task → [details](long-task/README.md)

| Claude Code | Codex | Action |
| --- | --- | --- |
| `/long-task [status\|pause\|resume\|clear\|complete] <objective>` | `$long-task [status\|pause\|resume\|clear\|complete] <objective>` | Autonomously build a project end to end with parallel worktree subagents and milestone reviews |

### handoff → [details](handoff/README.md)

| Claude Code | Codex | Action |
| --- | --- | --- |
| `/handoff frontend [scope]` | `$handoff frontend [scope]` | Write a client handoff from backend API diffs, ranges, or session context |
| `/handoff backend [scope]` | `$handoff backend [scope]` | Write a server handoff from code, API, database, job, or rollout changes |
| `/handoff session [note]` | `$handoff session [note]` | Hand this session to a fresh agent: proven vs unproven state, decisions, next actions, resume prompt |
| `/handoff [scope]` | `$handoff [scope]` | Resolve the audience from the wording or the diff |

### skill-forge → [details](skill-forge/README.md)

| Claude Code | Codex | Action |
| --- | --- | --- |
| `/skill-forge [skill-name-or-request]` | `$skill-forge [skill-name-or-request]` | Author or repair a skill package and publish every surface it needs |
| `/skill-audit [skill-or-path]` | `$skill-audit [skill-or-path]` | Report every packaged skill that violates the skill contract |
| `/reflect [session \| repo]` | `$reflect [session \| repo]` | Turn lessons into a script, test, hook, or skill edit, after your approval |

Every skill here satisfies the same nine rules: name parity, description
grammar, invocation mode, Codex descriptor, slash command, evals, catalog and
locale parity, plugin manifest, and published counts. `skill-audit` exits
non-zero on a violation, so it works as a merge gate.

## Migrating from the previous lineup

Variant selectors became arguments of one canonical skill. The same mapping
applies to the `$name` selectors in Codex.

| Old | New |
| --- | --- |
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

### Remove the retired skills

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

## Documentation

- [Usage](USAGE.md) — install, full command reference, configuration, examples, and troubleshooting
- [Architecture](ARCHITECTURE.md) — components, data flow, directory map, and design decisions

## Use on other agent platforms

All `SKILL.md` files in this repo follow the standard skill format and reference no Claude-Code-only tools, so they run on any agent platform that supports skills:


| Platform | How to install |
|---|---|
| **[Claude Code](https://code.claude.com)**, **[Codex](https://github.com/openai/codex)**, Antigravity CLI, Grok Build, Pi, Gemini CLI, GitHub Copilot CLI, **[OpenCode](https://github.com/sst/opencode)** | The `npx skills add` command in [Installation](#installation); it handles each agent's global directory |
| Any other agent in the [installer's list](https://github.com/vercel-labs/skills/blob/main/docs/agents.md) | Add its `--agent` ID to that command |
| An agent the installer does not list | Point its skill loader at `<plugin>/skills/<name>/` (the folder that holds `SKILL.md`) per its docs |

The agents share the same `SKILL.md` files and bundled resources. Each host
provides its own discovery and invocation UI. For example, Antigravity CLI
exposes skills as `/name`, while Pi uses `/skill:name`. Use an explicit
command for workflows marked `disable-model-invocation: true`.
[Antigravity skills](https://antigravity.google/docs/skills) · [Pi skills](https://docs.pi.dev/latest/skills)

## Requirements

- An agent platform that supports skills (Claude Code, Codex, Antigravity CLI, Grok Build, Pi, Gemini CLI, GitHub Copilot CLI, OpenCode, etc.)
- Git repository
- Git 2.45+ for `diff-summary`
- Python 3.10+ (for `interrogate`, `diff-summary`, `diff-viewer`, `plan-summary`, `git-commit rewrite`, `swarm`, `long-task`, `skill-audit`, and `make-bot-ui`; standard library only)

## License

MIT
