# git-skill

[한국어](README.ko.md) · [← back to main](../README.md)

A bundle of Git workflow skills: split working-tree changes into [Conventional Commits](https://www.conventionalcommits.org/), push, rewrite messy commit history, merge a branch into `main` or `dev` (and delete the source unless protected), and bulk-delete local branches that are already merged.

## What it does

- **Commit / Push / Rewrite** — group staged + unstaged changes into logical Conventional Commits, optionally push, or rewrite non-conformant subjects in place
- Creates each commit with explicit `git add <paths>` — never `git add .`
- Refuses to stage suspected secret files (`.env*`, `*_rsa`, `*.pem`, ...)
- Rewrites non-conformant commit subjects via `git filter-branch`, preserving the original body
- Refuses to rewrite commits already pushed to a remote (3-option menu instead) — unless you opt in with the `force` keyword
- **Merge / Cleanup** — merge into `main` (or `dev`/`develop`) then `git branch -d` the source unless it is protected; bulk-delete every local branch already merged into a protected branch
- Never force-pushes (except the explicit `/git-commit-rewrite` `force` opt-in), never bypasses hooks, never `git branch -D`

## Installation

**Recommended (global, one shot):**

```bash
npx skills add -y -g chann/skills@git-skill
```

**Project-local:**

```bash
npx skills add chann/skills@git-skill
```

**Manual:**

```bash
git clone https://github.com/chann/skills.git
ln -s "$(pwd)/skills/git-skill" ~/.claude/skills/git-skill
```

## Usage

Triggers when you ask Claude Code to commit / merge / clean up your branches, or via explicit commands:

| Command                    | Skill                  | Action                                                                                      |
| -------------------------- | ---------------------- | ------------------------------------------------------------------------------------------- |
| `/git-commit`              | `git-commit`           | Group staged + unstaged changes into logical units; create one Conventional Commit per unit |
| `/git-commit-push`         | `git-commit-push`      | Same as above, then `git push` (no force)                                                   |
| `/git-commit-rewrite`      | `git-commit-rewrite`   | Rewrite recent non-conformant commit subjects to Conventional format                        |
| `/git-merge-to-main`       | `git-merge-to-main`    | Merge current branch into `main`, then delete the source unless protected                   |
| `/git-merge-to-dev`        | `git-merge-to-dev`     | Merge current branch into `dev` (fallback `develop`), then delete the source unless protected |
| `/git-branch-cleanup`      | `git-branch-cleanup`   | Delete every local branch already merged into a protected branch                            |

**Examples:**

```
> commit my changes
> 변경사항 의미 단위로 커밋해줘
> /git-commit-push
> /git-commit-rewrite
> dev에 머지해줘
> 머지된 브랜치 다 정리해줘
```

## How it works

### `/git-commit` (default)

1. Inspect working tree (`git status --short`, `git diff`, `git diff --cached`)
2. Group staged + unstaged changes into logical units (one Conventional Commit per unit)
3. Show a commit plan and wait for user confirmation
4. Create commits one at a time with explicit `git add <paths>`
5. Show final summary via `git log --oneline`

### `/git-commit-push`

Runs the default workflow, then `git push`. Never `--force` or `--force-with-lease`. If the push is rejected, the skill stops and surfaces the error rather than auto-resolving.

### `/git-commit-rewrite`

1. Determine the rewrite range (default: from upstream / `main` / `master` merge-base to HEAD)
2. Run safety checks (working tree clean; HEAD attached; no commit in range pushed to a remote)
3. If any commit is pushed, present a 3-option menu (Cancel / Force-push / Branch-based) — defaults to Cancel
4. Identify non-conformant commits via the Conventional Commits regex (skips merges)
5. Generate new subjects using the mapping table; preserve each original body verbatim
6. Show old → new plan and wait for explicit confirmation
7. Apply via `git filter-branch --msg-filter` (in-place) or branch-based cherry-pick
8. Post-rewrite cleanup

### `/git-merge-to-main`

1. Preconditions — git repo, attached HEAD, current branch ≠ `main`, working tree clean, `main` exists locally
2. Show plan (`main..$src` log + delete step) and wait for confirmation
3. Optional fetch + warn if local `main` is behind `origin/main` (no auto-pull)
4. Checkout `main` and `git merge "$src"` — fast-forward when possible. On conflict: stop; do NOT auto-resolve
5. Delete or keep source: run `git branch -d "$src"` for non-protected sources; for protected sources, skip the local delete
6. Show `git log --oneline -5`. User pushes manually

Protected source branches: `main`, `master`, `dev`, `develop`, `development`, `stg`, `stage`, `staging`, `root`.

### `/git-merge-to-dev`

Same as `/git-merge-to-main`, but the target is resolved as: `dev` if it exists locally, else `develop`, else abort.

### `/git-branch-cleanup`

1. Find which protected branches exist locally (anchors): `main`, `master`, `dev`, `develop`, `development`, `stg`, `stage`, `staging`, `root`
2. Identify candidates — every non-protected, non-current branch whose tip is `git merge-base --is-ancestor` of at least one anchor
3. Show the plan with the proving anchor per candidate, plus what's kept and why; wait for confirmation (default: no)
4. Delete each candidate with `git branch -d` (safe). On refusal: skip + report; never `-D`
5. Summary

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

The skills **never**:

- Use `git add .` or `git add -A` (always explicit paths)
- Bypass hooks with `--no-verify` or `--no-gpg-sign`
- Force-push (`--force-with-lease` only after explicit user consent)
- Commit suspected secret files (`.env*`, `credentials.*`, `*_rsa`, `*.pem`, `*.key`, `*.p12`) without explicit override
- Combine `feat` and `fix` in one commit
- Rewrite pushed commits without showing the 3-option menu first
- Use `git filter-branch --root`
- Drop ticket references during rewrite (moves them to a `Refs:` footer)
- Use `git branch -D` (force delete) — only `git branch -d` (safe delete)
- Auto-resolve merge conflicts; auto-push after merging; auto-delete remote branches
- Delete protected branches: `main`, `master`, `dev`, `develop`, `development`, `stg`, `stage`, `staging`, `root`

## Project structure

```
git-skill/
├── .claude-plugin/
│   └── plugin.json                       # Plugin metadata
├── commands/
│   ├── git-commit.md                     # /git-commit (default)
│   ├── git-commit-push.md                # /git-commit-push command
│   ├── git-commit-rewrite.md             # /git-commit-rewrite command
│   ├── git-merge-to-main.md              # /git-merge-to-main command
│   ├── git-merge-to-dev.md               # /git-merge-to-dev command
│   └── git-branch-cleanup.md             # /git-branch-cleanup command
└── skills/
    ├── git-commit/                       # Main commit skill — full workflow + shared scripts
    │   ├── SKILL.md
    │   └── scripts/
    │       └── rewrite_msg.py            # filter-branch helper for rewrite
    ├── git-commit-push/                  # Push variant
    │   └── SKILL.md
    ├── git-commit-rewrite/               # Rewrite variant
    │   └── SKILL.md
    ├── git-merge-to-main/                # Merge into main + delete source
    │   └── SKILL.md
    ├── git-merge-to-dev/                 # Merge into dev/develop + delete source
    │   └── SKILL.md
    └── git-branch-cleanup/               # Bulk-delete merged local branches
        └── SKILL.md
```

## Requirements

- [Claude Code](https://code.claude.com) (CLI, desktop app, or IDE extension)
- Git repository
- Python 3.10+ (for `rewrite_msg.py` used by `/git-commit-rewrite`)

## License

MIT
