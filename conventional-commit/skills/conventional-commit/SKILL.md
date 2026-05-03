---
name: conventional-commit
description: >
  Split current working changes into logical units and create one Conventional Commit
  per unit (https://www.conventionalcommits.org/). Also rewrite recent non-conformant
  commit messages. Use this skill when the user asks to commit changes, organize commits,
  write commit messages, push commits, or clean up commit history. Trigger on phrases
  like "commit my changes", "커밋해줘", "커밋 분리", "make commits", "rewrite commit
  history", "커밋 메시지 다시 써줘", "/conventional-commit", "/conventional-commit:rewrite",
  "/conventional-commit:push".
---

# Conventional Commit Skill

Group current working-tree changes into meaningful commits that follow the [Conventional Commits 1.0.0](https://www.conventionalcommits.org/en/v1.0.0/) spec, and optionally rewrite non-conformant history.

| Command | Action |
|---|---|
| `/conventional-commit` | Group staged + unstaged changes into logical units; create one commit per unit |
| `/conventional-commit:push` | Same as above, then `git push` (no force) |
| `/conventional-commit:rewrite` | Rewrite recent non-conformant commit subjects to Conventional format |

## Conventional Commits Format

```
<type>[optional scope][!]: <description>

[optional body]

[optional footer(s)]
```

**Allowed types**

| Type | Meaning |
|---|---|
| `feat` | New feature (MINOR semver bump) |
| `fix` | Bug fix (PATCH semver bump) |
| `docs` | Documentation only |
| `style` | Formatting / whitespace; no logic change |
| `refactor` | Code change that neither fixes a bug nor adds a feature |
| `perf` | Performance improvement |
| `test` | Adding or fixing tests |
| `build` | Build system or external dependencies |
| `ci` | CI configuration files and scripts |
| `chore` | Other changes that don't modify src or tests |
| `revert` | Reverts a previous commit |

**Breaking changes** — append `!` after type/scope (e.g. `feat(api)!: drop v1 endpoints`) and/or include a `BREAKING CHANGE: ...` footer.

**Subject rules**

- Imperative mood: "add", not "added" / "adds"
- Lowercase first word of description
- No trailing period
- Aim for ≤72 characters in the subject line
- Scope is optional but recommended when it scopes to a clear module/area

**Examples**

```
feat(parser): add ability to parse arrays
fix(ui): correct button alignment
docs: update README with usage instructions
refactor(auth): extract token validation
chore: update dependencies
feat!: send email on registration

BREAKING CHANGE: email service is now required at boot
```

## Default Workflow (`/conventional-commit`)

### 1. Inspect the working tree

```bash
git status --short
git diff
git diff --cached
```

If there are no changes (neither staged nor unstaged), tell the user and stop.

### 2. Group changes into logical units

Read each modified file's diff and group them by intent. Each group maps to **one** Conventional Commit. **Ignore the existing staging state** — staged + unstaged changes are merged and re-grouped from scratch.

Grouping rules:

- Separate `feat` from `fix` — never combine
- Separate `docs` from code changes (unless the doc is a docstring inside the same change)
- Tests for a new feature/fix may go with that commit, or stand alone if the test changes are unrelated
- Separate `build` / `ci` / dependency updates from feature work
- Separate `refactor` from `feat`
- Fixes in unrelated modules → separate commits per module
- Trivial whitespace inside a feature file can fold into the feature commit

Don't over-split (one-line trivial cleanup with the feature is fine) and don't over-combine (a `feat` and `fix` must be separate commits).

**Secrets check** — flag any of these and exclude by default unless the user explicitly confirms: `.env*`, `credentials.*`, `*_rsa`, `*.pem`, `*.key`, `*.p12`, files containing the word `secret` in the path. Warn the user and skip those files; they should not be committed.

### 3. Show the commit plan

Before creating any commit, print a plan and let the user object:

```
Plan: 3 commits

1. feat(auth): add OAuth login flow
   - src/auth/oauth.ts
   - src/auth/index.ts

2. fix(api): handle null response in user fetch
   - src/api/users.ts

3. docs: update README with auth setup
   - README.md
```

### 4. Create commits one at a time

For each unit, in plan order:

```bash
git add path/one path/two   # explicit paths only
git commit -m "$(cat <<'EOF'
type(scope): description

optional body explaining the why
EOF
)"
```

Rules:

- **Never** `git add .` or `git add -A` — always explicit paths
- **Never** `--no-verify`, `--no-gpg-sign`, `--amend` (unless the user explicitly asks)
- **Never** add emoji or `Co-Authored-By: Claude` unless requested
- HEREDOC for multi-line messages so quoting stays correct
- After each commit, run `git status --short` to confirm only the intended files moved out of the working tree

If a pre-commit hook fails: do **not** retry with `--no-verify`. Investigate, fix the underlying issue (or report it), and create a fresh commit.

### 5. Final summary

After all commits are created, run:

```bash
git log --oneline -<N>
```

(where `N` is the number of commits made) and show it to the user.

## Push Workflow (`/conventional-commit:push`)

Run the default workflow above. After every commit succeeds:

```bash
git push
```

If the current branch has no upstream configured:

```bash
git push -u origin "$(git branch --show-current)"
```

**Never** use `--force` or `--force-with-lease`. If push is rejected (non-fast-forward), stop and report — do not auto-resolve. If the push fails for any reason, surface the error and let the user decide.

## Rewrite Workflow (`/conventional-commit:rewrite`)

Rewrites non-conformant commit messages in recent history. **This is destructive** — it changes commit SHAs. The default policy refuses to touch any commit that already exists on a remote.

### 1. Determine the rewrite range

Default base:

```bash
upstream=$(git rev-parse --abbrev-ref --symbolic-full-name '@{u}' 2>/dev/null || true)
if [ -n "$upstream" ]; then
  base=$(git merge-base HEAD "$upstream")
elif git rev-parse --verify main >/dev/null 2>&1; then
  base=$(git merge-base HEAD main)
elif git rev-parse --verify master >/dev/null 2>&1; then
  base=$(git merge-base HEAD master)
else
  echo "Could not determine a base. Ask the user for an explicit range." >&2
  exit 1
fi
```

If the user specifies a count (e.g. "rewrite last 5"), use `HEAD~5` as the base instead. Never use `--root`.

### 2. Safety checks (all must pass)

- Working tree is clean: `[ -z "$(git status --porcelain)" ]`
- HEAD is not detached: `git symbolic-ref -q HEAD >/dev/null`
- **No commit in the range is on a remote.** For each commit:
  ```bash
  git branch -r --contains <sha>
  ```
  If the output is non-empty for *any* commit, **stop and refuse** with a clear message: rewriting published history breaks pulls for collaborators. The user must rebase manually if they really want to.

### 3. Identify non-conformant commits

For each commit in `<base>..HEAD`, check the subject against:

```
^(feat|fix|docs|style|refactor|perf|test|build|ci|chore|revert)(\([^)]+\))?!?: .+
```

Skip commits that already match. Skip merge commits (`git rev-list --no-merges`).

### 4. Generate new messages

For each non-conformant commit:

1. Inspect: `git show --stat <sha>` and the diff body if needed
2. Pick a `type` from the table above based on the change content
3. Pick an optional `scope` (module / file area)
4. Write a new subject in imperative mood, lowercase, ≤72 chars, no trailing period
5. **Preserve the original commit body verbatim.** Only the subject line is rewritten. If the original body is empty, leave it empty.

### 5. Show old → new plan

```
Rewrite plan: 3 commits

abc1234  added login feature
       → feat(auth): add login feature

def5678  Fixed bug
       → fix(api): handle null response in user fetch

ghi9012  WIP
       → chore: work-in-progress checkpoint
```

Wait for explicit confirmation before applying.

### 6. Apply the rewrites

Build the mapping file at `/tmp/cc-rewrite-map.tsv`. Each non-conformant commit gets one line:

```
<full-40-char-sha>\t<new full message including preserved body>
```

The `<new full message>` is `<new subject>\n\n<original body>` (or just `<new subject>` if there is no body). Newlines inside the message are escaped as `\n` in the TSV; `rewrite_msg.py` un-escapes them.

Then run:

```bash
FILTER_BRANCH_SQUELCH_WARNING=1 git filter-branch -f \
  --msg-filter 'python3 "$(git rev-parse --git-common-dir)/../<skill-path>/scripts/rewrite_msg.py"' \
  <base>..HEAD
```

Easier: pass an absolute path to the script — copy or compute the absolute path of `scripts/rewrite_msg.py` once and substitute it. Example:

```bash
script="$HOME/.claude/skills/conventional-commit/scripts/rewrite_msg.py"
FILTER_BRANCH_SQUELCH_WARNING=1 git filter-branch -f \
  --msg-filter "python3 '$script'" \
  "$base..HEAD"
```

The script reads `$GIT_COMMIT`, looks it up in `/tmp/cc-rewrite-map.tsv`, and prints the new message. Commits not in the map pass through unchanged.

### 7. Post-rewrite

- Run `git log --oneline "$base..HEAD"` and show the result.
- Tell the user a backup ref was kept at `refs/original/refs/heads/<branch>` and how to discard it once they're satisfied:
  ```bash
  git update-ref -d refs/original/refs/heads/<branch>
  ```
  Do not delete it automatically.
- Delete the temp file:
  ```bash
  rm -f /tmp/cc-rewrite-map.tsv
  ```

## Behavior Guidelines

**Match the repo's existing style.** Inspect `git log -20 --oneline` first. If the repo already uses Conventional Commits, mirror its scope conventions. If existing messages are mixed, default to lowercase descriptions and concise scopes.

**Narration language.** Write conversation updates in the user's prompt language. Commit messages themselves stay in the language already dominant in `git log` (default English when ambiguous).

**Be conservative with scopes.** A scope must name a real module/area in the repo. If unsure, omit the scope rather than invent one.

**Don't over-explain in bodies.** A body should add context the subject can't carry (the *why*, a tricky tradeoff, a related issue). If the subject is self-explanatory, no body.

**Refuse, don't bypass.** If a safety check fails (pushed commits, dirty tree, detached HEAD, suspected secret), report and stop. Do not work around with destructive flags.

**Trust the user override.** If the user explicitly says "force push", "yes I know it's pushed, rewrite anyway", or "include the .env this time", proceed — but state the risk in one line.
