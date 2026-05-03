# conventional-commit

[한국어](README.ko.md) · [← back to main](../README.md)

Splits current working-tree changes into meaningful units and creates one [Conventional Commits](https://www.conventionalcommits.org/)-formatted commit per unit. Optionally pushes after committing, or rewrites recent non-conformant commit history.

## What it does

- Groups staged + unstaged changes into logical commits (separates `feat`/`fix`/`docs`/etc. and never combines them)
- Creates each commit with explicit `git add <paths>` — never `git add .`
- Refuses to stage suspected secret files (`.env*`, `*_rsa`, `*.pem`, ...)
- Rewrites non-conformant commit subjects via `git filter-branch`, preserving the original body
- Refuses to rewrite commits already pushed to a remote (safety default; presents a 3-option menu instead)
- Never force-pushes, never bypasses hooks

## Installation

**Recommended (global, one shot):**

```bash
npx skills add -y -g chann/skills@conventional-commit
```

**Project-local:**

```bash
npx skills add chann/skills@conventional-commit
```

**Manual:**

```bash
git clone https://github.com/chann/skills.git
ln -s "$(pwd)/skills/conventional-commit" ~/.claude/skills/conventional-commit
```

## Usage

Triggers when you ask Claude Code to commit your changes, or via explicit commands:

| Command                        | Skill                          | Action                                                                                      |
| ------------------------------ | ------------------------------ | ------------------------------------------------------------------------------------------- |
| `/conventional-commit`         | `conventional-commit`          | Group staged + unstaged changes into logical units; create one Conventional Commit per unit |
| `/conventional-commit-push`    | `conventional-commit-push`     | Same as above, then `git push` (no force)                                                   |
| `/conventional-commit-rewrite` | `conventional-commit-rewrite`  | Rewrite recent non-conformant commit subjects to Conventional format                        |

**Examples:**

```
> commit my changes
> 변경사항 의미 단위로 커밋해줘
> /conventional-commit-push
> /conventional-commit-rewrite
```

## How it works

### `/conventional-commit` (default)

1. Inspect working tree (`git status --short`, `git diff`, `git diff --cached`)
2. Group staged + unstaged changes into logical units (one Conventional Commit per unit)
3. Show a commit plan and wait for user confirmation
4. Create commits one at a time with explicit `git add <paths>`
5. Show final summary via `git log --oneline`

### `/conventional-commit-push`

Runs the default workflow, then `git push`. Never `--force` or `--force-with-lease`. If the push is rejected, the skill stops and surfaces the error rather than auto-resolving.

### `/conventional-commit-rewrite`

1. Determine the rewrite range (default: from upstream / `main` / `master` merge-base to HEAD)
2. Run safety checks (working tree clean; HEAD attached; no commit in range pushed to a remote)
3. If any commit is pushed, present a 3-option menu (Cancel / Force-push / Branch-based) — defaults to Cancel
4. Identify non-conformant commits via the Conventional Commits regex (skips merges)
5. Generate new subjects using the mapping table; preserve each original body verbatim
6. Show old → new plan and wait for explicit confirmation
7. Apply via `git filter-branch --msg-filter` (in-place) or branch-based cherry-pick
8. Post-rewrite cleanup

## Conventional Commits format

```
<type>[optional scope][!]: <description>

[optional body]

[optional footer(s)]
```

**Allowed types:** `feat`, `fix`, `docs`, `style`, `refactor`, `perf`, `test`, `build`, `ci`, `chore`, `revert`

**Breaking changes** — append `!` after type/scope (e.g. `feat(api)!: drop v1 endpoints`) and/or include a `BREAKING CHANGE: ...` footer.

**Examples:**

```
feat(parser): add ability to parse arrays
fix(ui): correct button alignment
docs: update README with usage instructions
refactor(auth): extract token validation
chore: update dependencies
feat!: send email on registration

BREAKING CHANGE: email service is now required at boot
```

## Safety guarantees

The skill **never**:

- Uses `git add .` or `git add -A` (always explicit paths)
- Bypasses hooks with `--no-verify` or `--no-gpg-sign`
- Force-pushes (`--force-with-lease` only after explicit user consent)
- Commits suspected secret files (`.env*`, `credentials.*`, `*_rsa`, `*.pem`, `*.key`, `*.p12`) without explicit override
- Combines `feat` and `fix` in one commit
- Rewrites pushed commits without showing the 3-option menu first
- Uses `git filter-branch --root`
- Drops ticket references during rewrite (moves them to a `Refs:` footer)

## Project structure

```
conventional-commit/
├── .claude-plugin/
│   └── plugin.json                       # Plugin metadata
├── commands/
│   ├── conventional-commit.md            # /conventional-commit (default)
│   ├── conventional-commit-push.md       # /conventional-commit-push command
│   └── conventional-commit-rewrite.md    # /conventional-commit-rewrite command
└── skills/
    ├── conventional-commit/              # Main skill — full workflow + shared scripts
    │   ├── SKILL.md                      # Skill definition and workflow
    │   └── scripts/
    │       └── rewrite_msg.py            # filter-branch helper for rewrite
    ├── conventional-commit-push/
    │   └── SKILL.md                      # Push variant skill
    └── conventional-commit-rewrite/
        └── SKILL.md                      # Rewrite variant skill
```

## Requirements

- [Claude Code](https://code.claude.com) (CLI, desktop app, or IDE extension)
- Git repository
- Python 3.10+ (for `rewrite_msg.py` used by `/conventional-commit-rewrite`)

## License

MIT
