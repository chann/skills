# git-skill

[한국어](README.ko.md) · [← back to main](../README.md)

Git workflow skills with conservative safety rules. One `git-commit` workflow
turns changes into [Conventional Commits](https://www.conventionalcommits.org/)
once, with a push, as verified checkpoints while you work (local, pushed, or
deployed), or rewrites messy commit subjects. `git-merge` merges into `main`,
`dev`, or any local branch; `git-resolve-conflicts` finishes a stopped merge or
rebase; `git-cleanup` removes finished worktrees and merged branches.

## What it does

- **Commit modes** — `git-commit` groups staged and unstaged changes into one Conventional Commit per logical unit; `push` adds an ordinary push; `realtime` commits each verified outcome while work continues; `push realtime` pushes each one and proves upstream parity; `deploy` also deploys each checkpoint through the settings already documented in `AGENTS.md` and confirms it before the next one; `rewrite` fixes non-conformant subjects
- Stages explicit paths only — never `git add .`
- Excludes suspected secret files (`.env*`, `*_rsa`, `*.pem`, ...), except the exact basename `.env.example`
- Rewrites commit subjects with `git filter-branch`, keeping each original body; published history can be rewritten on a new local branch
- **Merge** — merge the current branch into the resolved target, then `git branch -d` the source unless it is protected
- **Cleanup** — remove clean, unlocked, merged linked worktrees and delete local branches already merged into a protected branch
- Never force-pushes, never bypasses hooks, never `git branch -D`, never `git worktree remove --force`

## Installation

**Recommended (global, one shot):**

```bash
npx skills add -y -g chann/skills \
  --skill git-commit \
  --skill gcr \
  --skill gcpr \
  --skill gcpd \
  --skill git-merge \
  --skill git-resolve-conflicts \
  --skill git-cleanup
```

**Project-local:**

```bash
npx skills add chann/skills \
  --skill git-commit \
  --skill gcr \
  --skill gcpr \
  --skill gcpd \
  --skill git-merge \
  --skill git-resolve-conflicts \
  --skill git-cleanup
```

Use the skill names with `--skill`; `git-skill` is the plugin directory. Each
alias needs `git-commit` installed next to it and refuses to run without it:

```bash
npx skills add -y -g chann/skills --skill git-commit --skill gcpr
```

**Manual:**

```bash
git clone https://github.com/chann/skills.git
ln -s "$(pwd)/skills/git-skill" ~/.claude/skills/git-skill
```

## Usage

Natural-language requests select the matching workflow and mode. Explicit
invocation uses `/name` in Claude Code and `$name` in Codex.

| Claude Code | Codex | Action |
| --- | --- | --- |
| `/git-commit` | `$git-commit` | Group the current changes into Conventional Commits, once |
| `/git-commit push` | `$git-commit push` | The same, then an ordinary `git push` (never force) |
| `/git-commit realtime` · `/gcr` | `$git-commit realtime` · `$gcr` | Commit each verified outcome while working; every checkpoint stays local |
| `/git-commit push realtime` · `/gcpr` | `$git-commit push realtime` · `$gcpr` | Commit and immediately push each verified outcome, proving upstream parity |
| `/git-commit deploy` · `/gcpd` | `$git-commit deploy` · `$gcpd` | Commit, push, deploy, and confirm each outcome using documented repository settings |
| `/git-commit rewrite [range]` | `$git-commit rewrite [range]` | Rewrite recent non-conformant commit subjects |
| `/git-merge [main \| dev \| <branch>]` | `$git-merge` | Merge the current branch into the target, then delete the source unless protected |
| `/git-resolve-conflicts` | `$git-resolve-conflicts` | Finish a conflicted merge, rebase, cherry-pick, or revert without aborting it |
| `/git-cleanup` | `$git-cleanup` | Remove finished worktrees and delete local branches already merged into a protected branch |

`gcr`, `gcpr`, and `gcpd` are explicit-only aliases: they never start from
natural language, and they run the installed `git-commit` with a fixed mode.

**Examples:**

```
> commit my changes
> 변경사항 의미 단위로 커밋해줘
> 커밋하고 푸시해줘
> keep committing and pushing meaningful checkpoints as you work
> $gcpr
> 의미 있는 단위마다 배포해줘
> /git-commit rewrite HEAD~5
> dev에 머지해줘
> 머지된 브랜치랑 끝난 워크트리 정리해줘
```

### Migrating from 0.x

| Old selector | New invocation |
| --- | --- |
| `/git-commit-push` | `/git-commit push` |
| `/git-commit-realtime` | `/git-commit realtime` or `/gcr` |
| `/git-commit-push-realtime` | `/git-commit push realtime` or `/gcpr` |
| `/git-commit-push-deploy` | `/git-commit deploy` or `/gcpd` |
| `/git-commit-rewrite` | `/git-commit rewrite` |
| `/git-merge-to-main` | `/git-merge main` |
| `/git-merge-to-dev` | `/git-merge dev` |
| `/git-branch-cleanup` | `/git-cleanup` |

The same mapping applies to the `$name` selectors in Codex.

## How it works

### `git-commit`

1. Resolve the mode from the arguments or the request and state it before any Git command; an ambiguous request takes the less far-reaching mode, and `push` or `deploy` is never inferred from silence
2. Inspect the tree, group changes by intent, exclude suspected secrets, and show the commit plan
3. Stage explicit paths and create one Conventional Commit per unit; a failing hook is fixed, never bypassed
4. `push`: run `git push` (`-u` when no upstream exists); on rejection, stop and ask how to reconcile

**Checkpoint modes** (`realtime`, `push realtime`, `deploy`) plan outcome-based
checkpoints, never time- or file-count-based ones, verify each with the
narrowest relevant checks plus `git diff --check`, and commit it.
`realtime` keeps every checkpoint local. `push realtime` pushes each one and
proves `HEAD...@{u}` is `0 0` before the next. `deploy` resolves the target,
route, source, and confirmation method from the repository's documented settings
before the first checkpoint, deploys the exact pushed revision, and does not
start the next outcome until the deployment and required health checks are
confirmed. Each run ends with a full-scope completion audit.

**Rewrite** checks the exact range, requires a clean tree and attached HEAD,
and proposes subjects while preserving the bodies and ticket references.
After confirmation it can rewrite a private branch in place or create a new
local branch for published or protected history. All rewrites stay local.

### `git-merge`

1. Resolve the target: the argument wins; `dev` falls back to `develop`; with no argument, the default branch from `origin/HEAD`, otherwise `main`. The target must exist locally
2. Refuse a detached HEAD, a dirty tree, or a source equal to the target
3. Show the plan, including the resolved target, and wait for confirmation (default no)
4. Plain `git merge`; on conflicts, stop and report
5. `git branch -d` the source unless it is protected; never `-D`, never push

Protected branches: `main`, `master`, `dev`, `develop`, `development`, `stg`, `stage`, `staging`, `root`.

### `git-cleanup`

1. Find which protected branches exist locally (anchors)
2. Worktree pass: from `git worktree list --porcelain`, a linked worktree is removable only when it is not the main or current worktree, not locked, `git status --short` is empty, and its non-protected branch tip is reachable from an anchor
3. Branch pass: every non-protected, non-current branch whose tip is reachable from an anchor
4. Show one plan for both, with the proving anchor per item and every kept item's reason; wait for confirmation
5. `git worktree remove` (never `--force`), `git worktree prune`, `git branch -d` (never `-D`); a refusal is left in place and reported

### `git-resolve-conflicts`

1. Identify which operation stopped and its goal; a rebase swaps the ours/theirs labels
2. List conflicted paths with `--diff-filter=U` and turn on `--conflict=zdiff3`
3. Classify each path; regenerate lockfiles and generated files instead of hand-merging them
4. Recover both sides' intent before touching a hunk, keep both where compatible, and record what was dropped
5. Run the project's own checks, then `--continue`. Never `--abort`, never `--skip`, never push

## Safety guarantees

The skills **never**:

- Use `git add .` or `git add -A`
- Bypass hooks with `--no-verify` or `--no-gpg-sign`
- Force-push in any mode
- Commit suspected secret files (`.env*` except the exact basename `.env.example`, `credentials.*`, `*_rsa`, `*.pem`, `*.key`, `*.p12`) without explicit override
- Commit or push a knowingly broken, time-based, or placeholder checkpoint
- Deploy to a target the repository does not document, or report a checkpoint deployed before its deployment is confirmed
- Rewrite a published branch in place, use `git filter-branch --root`, or drop ticket references
- Use `git branch -D` or `git worktree remove --force`
- Auto-resolve conflicts, push after merging, or delete remote branches
- Delete protected branches: `main`, `master`, `dev`, `develop`, `development`, `stg`, `stage`, `staging`, `root`

## Project structure

```
git-skill/
├── .claude-plugin/plugin.json
├── commands/                    # one /name command per skill
└── skills/
    ├── git-commit/
    │   ├── SKILL.md             # modes, format, default workflow, safety rules
    │   ├── references/
    │   │   ├── checkpoints.md   # realtime, push realtime, deploy cadence
    │   │   ├── deploy.md        # documented settings, deploy route, confirmation gate
    │   │   └── rewrite.md       # local history rewrite
    │   └── scripts/rewrite_msg.py
    ├── gcr/ · gcpr/ · gcpd/     # explicit-only aliases with a fixed mode
    ├── git-merge/
    ├── git-resolve-conflicts/
    └── git-cleanup/
```

Every skill ships `agents/openai.yaml` and `evals/evals.json`.

## Requirements

- Claude Code or Codex
- Git repository
- Python 3.10+ (for `rewrite_msg.py` used by `/git-commit rewrite`)

## License

MIT
