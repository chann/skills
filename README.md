# skills

[한국어](README.ko.md)

A collection of practical agent skills for software engineering workflows.

## Skills

| Skill                                              | What it does                                                                                  |
| -------------------------------------------------- | --------------------------------------------------------------------------------------------- |
| **[code-review](code-review/README.md)**           | Automated code review from git diffs — markdown / HTML reports with severity ratings          |
| **[conventional-commit](conventional-commit/README.md)** | Group changes into Conventional Commits, optionally push, or rewrite messy commit history |
| **[long-task](long-task/README.md)**               | Autonomous orchestrator for multi-milestone projects — parallel worktree subagents + reviews  |

## Installation

Install all skills globally with one command (recommended):

```bash
npx skills add -y -g chann/skills
```

Per-skill or non-global installs (and manual setup) are documented in each skill's README:

- [code-review installation](code-review/README.md#installation)
- [conventional-commit installation](conventional-commit/README.md#installation)
- [long-task installation](long-task/README.md#installation)

## Quick reference

### code-review → [details](code-review/README.md)

| Command             | Output                                       |
| ------------------- | -------------------------------------------- |
| `/code-review`      | Show findings in conversation (no file)      |
| `/code-review-md`   | Write markdown report to `.reviews/`         |
| `/code-review-html` | Write markdown + HTML reports to `.reviews/` |

### conventional-commit → [details](conventional-commit/README.md)

| Command                        | Action                                                            |
| ------------------------------ | ----------------------------------------------------------------- |
| `/conventional-commit`         | Group working-tree changes into Conventional Commits              |
| `/conventional-commit-push`    | Same, then `git push` (no `--force`)                              |
| `/conventional-commit-rewrite` | Rewrite recent non-Conventional commit subjects                   |

### long-task → [details](long-task/README.md)

| Command       | Action                                                                                       |
| ------------- | -------------------------------------------------------------------------------------------- |
| `/long-task`  | Autonomously build a project end-to-end with parallel worktree subagents + milestone reviews |

Also triggers on phrases like *"build this whole project"*, *"do this autonomously"*, *"run a long task"*.

## Use on other agent platforms

All `SKILL.md` files in this repo follow the standard skill format and reference no Claude-Code-only tools, so they run on any agent platform that supports skills:

| Platform                                                | How to install                                                                                 |
| ------------------------------------------------------- | ---------------------------------------------------------------------------------------------- |
| **[Claude Code](https://code.claude.com)**              | `npx skills add chann/skills` — installs the full plugin (skill + slash commands)              |
| **[Codex](https://github.com/openai/codex)**            | Symlink `<plugin>/skills/<name>/` into your Codex skills directory (e.g. `~/.agents/skills/`)  |
| **[opencode](https://github.com/sst/opencode)**         | Drop the skill directory into your opencode skills path                                        |
| **Copilot CLI / Gemini CLI / others**                   | Point your platform's skill loader at `<plugin>/skills/<name>/SKILL.md` per its docs           |

What is and isn't portable:

- **Portable** — every `SKILL.md` body and its `references/`. The skills trigger on natural-language phrases on any platform.
- **Claude Code only** — the `.claude-plugin/plugin.json` wrapper, the `npx skills` installer, and the slash commands (`/code-review`, `/conventional-commit`, `/long-task`). Other platforms invoke the skill via natural language or their own activation mechanism.

## Requirements

- An agent platform that supports skills (Claude Code, Codex, opencode, Copilot CLI, Gemini CLI, etc.)
- Git repository
- Python 3.10+ (for `code-review-html` and `conventional-commit-rewrite`)

## License

MIT
