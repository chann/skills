# skills

[한국어](README.ko.md)

A collection of practical agent skills for software engineering workflows.

## Skills

| Skill                                              | What it does                                                                                  |
| -------------------------------------------------- | --------------------------------------------------------------------------------------------- |
| **[code-review](code-review/README.md)**           | Automated code review from git diffs — markdown / HTML reports with severity ratings          |
| **[conventional-commit](conventional-commit/README.md)** | Group changes into Conventional Commits, optionally push, or rewrite messy commit history |

## Installation

Install all skills globally with one command (recommended):

```bash
npx skills add -y -g chann/skills
```

Per-skill or non-global installs (and manual setup) are documented in each skill's README:

- [code-review installation](code-review/README.md#installation)
- [conventional-commit installation](conventional-commit/README.md#installation)

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

## Requirements

- [Claude Code](https://code.claude.com) (CLI, desktop app, or IDE extension)
- Git repository
- Python 3.10+ (for `code-review-html` and `conventional-commit-rewrite`)

## License

MIT
