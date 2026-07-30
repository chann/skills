# skills

[🇰🇷 Korean](README.ko.md)

A collection of 18 practical agent skills for software engineering workflows.

## Website

The interactive catalog in [`website/`](website/README.md) explains every skill,
shows the exact Claude Code and Codex selectors, and provides copyable install
and usage examples.

```bash
npm --prefix website ci
npm --prefix website run dev
```

Run `npm --prefix website run build` for a deployable static bundle under
`website/dist/`.

## Skills


| Skill                                    | What it does                                                                                                   |
| ---------------------------------------- | -------------------------------------------------------------------------------------------------------------- |
| **[code-review](code-review/README.md)** | Git change intelligence — explanatory diff summaries, severity-based reviews, and a raw HTML diff viewer     |
| **[doc-skill](doc-skill/README.md)**     | Generate or update README, Korean README, architecture, and usage docs without clobbering prose                |
| **[git-skill](git-skill/README.md)**     | Conventional Commits, realtime checkpoint commits or pushes, history rewrite, merge to main/dev, and merged-branch cleanup    |
| **[handoff](handoff/README.md)**         | Generate frontend/client and backend/server handoff docs from git diffs, ranges, and session context           |
| **[long-task](long-task/README.md)**     | Autonomous orchestrator for multi-milestone projects — parallel worktree subagents + reviews                   |


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

The explicit agent list is intentional. `skills@1.5.19` can
implicitly add the project-only PromptScript adapter when `--global --yes` is
used without `--agent`, producing one misleading failure for every skill even
though the supported targets were installed. The command above selects all
skills, keeps the default symlink mode (do not add `--copy`), and avoids that
unsupported target. Append other globally supported agent IDs if needed, but
keep this explicit target list so this CLI version does not fall back to copy
mode while
[the upstream fix](https://github.com/vercel-labs/skills/pull/1561) is pending.

Per-skill or non-global installs (and manual setup) are documented in each skill's README:

- [code-review installation](code-review/README.md#installation)
- [doc-skill installation](doc-skill/README.md#installation)
- [git-skill installation](git-skill/README.md#installation)
- [handoff installation](handoff/README.md#installation)
- [long-task installation](long-task/README.md#installation)

Example handoff-only install: `npx skills add chann/skills --skill gen-frontend-handoff --skill gen-backend-handoff`
Backend-only handoff install: `npx skills add chann/skills --skill gen-backend-handoff`
Diff-summary-only install: `npx skills add chann/skills --skill diff-summary`

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
| `/diff-summary-quiz [scope]`     | `$diff-summary-quiz [scope]` | Same as `/diff-summary`, plus aligned interactive comprehension quizzes                          |
| `/diff-viewer`                   | `$diff-viewer`              | Render the raw working-tree diff to `.diffs/`                                                    |

`diff-summary` also activates from requests such as “summarize the code changes,” “summarize the last commit,” and “main..dev summary.” Its default output is an aligned Korean/English pair with Korean shown first; explicitly request one language for single-language mode. Ask for “Markdown only” to route to `diff-summary-md`, or “quiz me on this diff” to route to `diff-summary-quiz`. All three preserve explicit `..` and `...` ranges exactly. Use `code-review` to find defects and `diff-viewer` to inspect the raw patch.

Every HTML report — review, summary, quiz, and raw diff — shares one interface: a Korean/English toggle, light/dark/system themes with a light print palette, one semantic status palette held at WCAG AA in both themes, Korean-aware typography that breaks prose on 어절 boundaries, and a keyboard shell with a skip link and a live region. Each report stays a single self-contained file that works with no server and no network.


### doc-skill → [details](doc-skill/README.md)


| Claude Code | Codex       | Action                                                                 |
| ----------- | ----------- | ---------------------------------------------------------------------- |
| `/gen-docs` | `$gen-docs` | Generate or update README, Korean README, architecture, and usage docs |


### git-skill → [details](git-skill/README.md)


| Claude Code                      | Codex                       | Action                                                                                |
| -------------------------------- | --------------------------- | ------------------------------------------------------------------------------------- |
| `/git-commit`                    | `$git-commit`               | Group working-tree changes into Conventional Commits                                  |
| `/git-commit-push`               | `$git-commit-push`          | Same, then `git push` (no `--force`)                                                   |
| `/git-commit-push-realtime` · `/gcpr` | `$git-commit-push-realtime` | Commit and push each verified, meaningful outcome while implementation continues |
| `/git-commit-realtime` · `/gcr` | `$git-commit-realtime` | Commit each verified, meaningful outcome locally while implementation continues — no push |
| `/git-commit-rewrite`            | `$git-commit-rewrite`       | Rewrite recent non-Conventional commit subjects                                       |
| `/git-merge-to-main`             | `$git-merge-to-main`        | Merge current branch into `main`, then `git branch -d` the source                     |
| `/git-merge-to-dev`              | `$git-merge-to-dev`         | Merge current branch into `dev` (fallback `develop`), then `git branch -d` the source |
| `/git-branch-cleanup`            | `$git-branch-cleanup`       | Delete every local branch already merged into a protected branch                      |


### long-task → [details](long-task/README.md)


| Claude Code  | Codex        | Action                                                                                       |
| ------------ | ------------ | -------------------------------------------------------------------------------------------- |
| `/long-task` | `$long-task` | Autonomously build a project end-to-end with parallel worktree subagents + milestone reviews |


Also triggers on phrases like *"build this whole project"*, *"do this autonomously"*, *"run a long task"*.

### handoff → [details](handoff/README.md)


| Claude Code               | Codex                    | Action                                                                            |
| ------------------------- | ------------------------ | --------------------------------------------------------------------------------- |
| `/gen-frontend-handoff`   | `$gen-frontend-handoff`  | Write a frontend/client handoff from backend API diffs, ranges, or session context |
| `/gen-backend-handoff`    | `$gen-backend-handoff`   | Write a backend/server handoff from code, API, DB, job, or rollout changes         |

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


What is and isn't portable:

- **Portable** — every `SKILL.md` body and its `references/`. The skills trigger on natural-language phrases on any platform.
- **Claude Code only** — the `.claude-plugin/plugin.json` wrapper, the `npx skills` installer, and the slash commands (`/code-review`, `/git-commit`, `/long-task`, ...). Other platforms invoke the skill via natural language or their own activation mechanism.

## Requirements

- An agent platform that supports skills (Claude Code, Codex, opencode, Copilot CLI, Gemini CLI, etc.)
- Git repository
- Git 2.45+ for `diff-summary`, `diff-summary-md`, and `diff-summary-quiz`
- Python 3.10+ (for `code-review`, `diff-summary`, `diff-summary-md`, `diff-summary-quiz`, `diff-viewer`, and `git-commit-rewrite`)

## License

MIT
