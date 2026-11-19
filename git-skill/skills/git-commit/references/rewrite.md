# Rewrite mode

`/git-commit rewrite [range] [force]` rewrites non-Conventional commit subjects
in recent history. It is destructive: commit SHAs change. Without `force`, it
refuses to touch commits already on a remote unless the user picks an option
from the pushed-commits menu.

## Force mode

The invocation is in force mode when it contains the standalone token `force` or
`--force` (case-insensitive), as in `/git-commit rewrite force` or "force로 다시
써줘". The Korean word `강제로` alone does not trigger it. The keyword is explicit,
pre-granted consent for a destructive in-place rewrite:

- Skip safety checks A and B. Git still enforces its own rules
  (`git filter-branch` refuses a dirty tree); surface its error verbatim and do
  not work around it.
- Skip the pushed-commits menu and rewrite in place even if commits are pushed.
- Still show the old → new plan, then apply without waiting.
- If any rewritten commit was already on the remote, finish with a bare
  `git push --force`. This is the only place bare `--force` is allowed. If
  nothing was pushed, the rewrite stays local.
- Keep the `refs/original/` backup and report it, as below.

Without the keyword, follow every step.

## 1. Determine the range

A count ("rewrite the last 5") uses `HEAD~5` as the base; an explicit range uses
that range. Otherwise:

```bash
upstream=$(git rev-parse --abbrev-ref --symbolic-full-name '@{u}' 2>/dev/null || true)
if [ -n "$upstream" ]; then base=$(git merge-base HEAD "$upstream")
elif git rev-parse --verify main >/dev/null 2>&1; then base=$(git merge-base HEAD main)
elif git rev-parse --verify master >/dev/null 2>&1; then base=$(git merge-base HEAD master)
else echo "No base found; ask the user for an explicit range." >&2; exit 1
fi
```

Never use `--root`.

## 2. Safety checks (skipped in force mode)

- **A — clean tree:** `[ -z "$(git status --porcelain)" ]`. Otherwise ask the
  user to commit or stash first, and stop.
- **B — attached HEAD:** `git symbolic-ref -q HEAD`. Otherwise ask the user to
  check out a branch, and stop.
- **C — pushed commits:** for each SHA in `git rev-list "$base..HEAD"`, check
  `git branch -r --contains "$sha"`.

When any commit is pushed, do not silently refuse. Show the pushed commits with
their remote branches and this menu, defaulting to Cancel:

1. **Cancel** — keep history as it is.
2. **Rewrite locally and force-push** — require an explicit phrase such as "yes
   force push"; afterwards push with `git push --force-with-lease`, never bare
   `--force`. A failing lease means the remote moved: stop and ask rather than
   overwrite it.
3. **Rewrite onto a new branch** — the safe option (step 7).

## 3. Find non-conformant commits

List with `git rev-list --no-merges "$base..HEAD"`; never rewrite merge commits.
A subject conforms when it matches:

```
^(feat|fix|docs|style|refactor|perf|test|build|ci|chore|revert)(\([^)]+\))?!?: .+
```

Leave conforming commits unchanged.

## 4. Write the new subjects

Inspect each commit (`git show --stat <sha>`, and the diff when needed), pick a
type and an optional real scope, and write an imperative, lowercase subject of
about 72 characters at most with no trailing period. Rewrite only the subject:
preserve the original body verbatim, and leave an empty body empty. Move a ticket
prefix into a `Refs:` footer instead of dropping it.

| Original | Likely rewrite |
|---|---|
| `Added X` / `Add X` | `feat: add X` |
| `Fixed X` / `Bugfix: X` | `fix: <imperative>` |
| `Updated X` (dependency or cosmetic) | `chore: update X` or `build(deps): bump X` |
| `Updated X` (real restructuring) | `refactor: <imperative>` |
| `Renamed X to Y` | `refactor: rename X to Y` |
| `Removed X` | `refactor: remove X` (or `feat!:` when breaking) |
| `WIP` / `tmp` | `chore: work-in-progress checkpoint` |
| `Initial commit` | `chore: initial commit` |
| `[TICKET-123] Added X` | `feat: add X` + footer `Refs: TICKET-123` |
| `proj #N: Added X` | `feat(scope): add X` + footer `Refs: proj#N` |
| `Tests for X` | `test: add tests for X` |

When the type is unclear, prefer `chore` for tooling and config, `refactor` for
code shape, and `style` only for whitespace or formatting.

## 5. Show the old → new plan

```
abc1234  added login feature
       → feat(auth): add login feature
```

Wait for explicit confirmation (force mode shows the plan and does not wait).

## 6. Apply in place

Write `/tmp/cc-rewrite-map.tsv` (or the path in `CC_REWRITE_MAP`), one line per
rewritten commit: `<full 40-char sha>\t<new message>`, with newlines inside the
message escaped as `\n`. Then run this skill's script, resolved from the
installed `git-commit` skill directory:

```bash
script="<git-commit skill dir>/scripts/rewrite_msg.py"
FILTER_BRANCH_SQUELCH_WARNING=1 git filter-branch -f \
  --msg-filter "python3 '$script'" "$base..HEAD"
```

Commits absent from the map pass through unchanged. Use `git filter-repo` only
when the user has it and prefers it.

## 7. Rewrite onto a new branch (menu option 3)

```bash
src=$(git branch --show-current)
git checkout -b "${src}-cc" "$base"
for sha in $(git rev-list --reverse --no-merges "$base..$src"); do
  git cherry-pick "$sha"
  git commit --amend -m "<new message for $sha>"   # only the commit just picked
done
git log --oneline "$base..HEAD"
git push -u origin "${src}-cc"
```

The original branch stays untouched; no force push happens.

## 8. Clean up

- After an in-place rewrite, show `git log --oneline "$base..HEAD"`, tell the
  user a backup was kept at `refs/original/refs/heads/<branch>` and that
  `git update-ref -d refs/original/refs/heads/<branch>` discards it once they are
  satisfied (never delete it automatically), and remove the map file.
- After a branch rewrite, tell the user they can return with
  `git checkout <original-branch>` and drop the new branch with
  `git branch -D <branch>-cc` themselves if they change their mind.
