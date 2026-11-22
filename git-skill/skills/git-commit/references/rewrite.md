# Rewrite mode

`/git-commit rewrite [range]` updates non-Conventional subjects in local
history. It changes commit IDs and requires confirmation of the exact branch,
range and message changes. A `force` argument or request to skip checks does
not authorize this workflow to overwrite published history.

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

## 2. Safety checks

- Require a clean working tree and attached HEAD. Resolve the base and tip
  to full commit IDs, verify the base is an ancestor, and reject invalid or
  empty ranges before showing the plan.
- Inspect remote-tracking refs for every commit that the rewrite could replace
  with `git branch -r --contains <oid>`. Include descendants whose IDs change
  even when their messages stay the same. Local tracking refs can be stale.
- For a protected branch, a branch with an upstream, or any commit reachable
  from a remote-tracking ref, offer **Cancel** (default) or **Rewrite on a new
  local branch**. The original branch and the remote are untouched.
- For a private local branch with no published commits, offer an in-place
  rewrite. Record the original tip for recovery. A rewrite never pushes.

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

Wait for explicit confirmation. Recheck the reviewed tip, clean worktree,
and destination branch immediately before rewriting. If the new local branch
was selected, create it at the original tip and switch to it before applying
the message map. This preserves merge topology and merge resolutions.

## 6. Apply the confirmed plan

Use a fresh private temporary directory and a JSON object whose keys are full
commit IDs and whose values are the reviewed messages. Write the file with
mode 0600 using a JSON encoder. Include only the planned commits. Resolve the
rewrite helper to its trusted installed absolute path and pass both file paths
as data through environment variables for this invocation. Do not construct
shell code from commit subjects, paths, or repository content.

```bash
rewrite_dir=$(mktemp -d)
(umask 077; touch "$rewrite_dir/messages.json")
# Write the reviewed JSON object to "$rewrite_dir/messages.json".
CC_REWRITE_HELPER="$installed_helper" CC_REWRITE_MAP="$rewrite_dir/messages.json" \
  FILTER_BRANCH_SQUELCH_WARNING=1 git filter-branch \
  --msg-filter 'python3 "$CC_REWRITE_HELPER" "$CC_REWRITE_MAP"' \
  "$base..refs/heads/$destination"
```

Do not overwrite Git's existing backup refs. A missing or invalid map must
stop the rewrite. Afterward, check that the original and new tip trees match
and inspect the resulting subjects and topology before reporting success.
Remove this invocation's temporary map and directory on success or failure.
Report the local branch and the backup under
`refs/original/refs/heads/<branch>`. Keep the backup until the user decides to
remove it.
