---
name: conventional-commit
description: Use when the user asks to commit changes, organize commits, write commit messages, or split working-tree changes into Conventional Commits. Trigger on phrases like "commit my changes", "커밋해줘", "커밋 분리", "make commits", "/conventional-commit", or whenever the user wants to turn current changes into Conventional Commit-style commits. For commit + push use `conventional-commit-push`; for rewriting non-Conventional commit history use `conventional-commit-rewrite`.
---

# Conventional Commit Skill

## Overview

Group working-tree changes into [Conventional Commits 1.0.0](https://www.conventionalcommits.org/en/v1.0.0/) units (one commit per logical unit), or rewrite recent non-conformant commit subjects in place.

**Core principle:** Match user intent to the right workflow — new commits vs. history rewrite — and never bypass safety with destructive flags.

**Announce at start:** "I'm using the conventional-commit skill to <commit / push / rewrite> these changes."

## Commands

| Command | Skill | Action | Operates on |
|---|---|---|---|
| `/conventional-commit` | `conventional-commit` | Group working-tree changes into Conventional Commits | Uncommitted (staged + unstaged) changes |
| `/conventional-commit-push` | `conventional-commit-push` | Same as above, then `git push` (no `--force`) | Uncommitted changes + remote |
| `/conventional-commit-rewrite` | `conventional-commit-rewrite` | Rewrite recent non-Conformant commit subjects | Existing local history |

## Choosing the Right Command

Run this check before doing anything:

```bash
git status --short        # Are there working-tree changes?
git log --oneline -10     # Are recent messages already Conventional?
```

| Situation | Command |
|---|---|
| Working tree has changes, history is fine | `/conventional-commit` |
| Working tree has changes + want to push | `/conventional-commit-push` |
| Working tree clean, recent history is messy ("Added X", "WIP", "Fixed bug") | `/conventional-commit-rewrite` |
| Both: working tree dirty AND history messy | First commit (`/conventional-commit`), then `/conventional-commit-rewrite` separately |

**Auto-routing:** If the user runs bare `/conventional-commit` but the working tree is clean, look at recent history. If recent commits are non-conformant, surface this and ask: "No working changes to commit. Recent history has N non-Conformant subjects — do you want to rewrite them with `/conventional-commit-rewrite`?"

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

## Workflow: `/conventional-commit` (default)

### Step 1: Inspect the working tree

```bash
git status --short
git diff
git diff --cached
```

If there are no changes → tell the user, run the auto-routing check (above), and stop.

### Step 2: Group changes into logical units

Read each modified file's diff and group by intent. Each group maps to **one** Conventional Commit. **Ignore the existing staging state** — staged + unstaged changes are merged and re-grouped from scratch.

Grouping rules:

- Separate `feat` from `fix` — never combine
- Separate `docs` from code changes (unless the doc is a docstring inside the same change)
- Tests for a new feature/fix may go with that commit, or stand alone if unrelated
- Separate `build` / `ci` / dependency updates from feature work
- Separate `refactor` from `feat`
- Fixes in unrelated modules → separate commits per module
- Trivial whitespace inside a feature file can fold into the feature commit

Don't over-split (a one-line trivial cleanup with the feature is fine) and don't over-combine (a `feat` and `fix` must be separate commits).

**Secrets check** — flag any of these and exclude by default unless the user explicitly confirms: `.env*`, `credentials.*`, `*_rsa`, `*.pem`, `*.key`, `*.p12`, files containing the word `secret` in the path. Warn the user; they should not be committed.

### Step 3: Show the commit plan

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

### Step 4: Create commits one at a time

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
- After each commit, run `git status --short` to confirm only the intended files moved

If a pre-commit hook fails: do **not** retry with `--no-verify`. Investigate, fix the underlying issue (or report it), and create a fresh commit.

### Step 5: Final summary

```bash
git log --oneline -<N>
```

(where `N` is the number of commits made) and show it to the user.

### Worked Example

```
User: 변경사항 의미 단위로 커밋해줘

git status --short →
 M src/auth/oauth.ts
 M src/auth/index.ts
 M src/api/users.ts
 M README.md
?? src/api/.env

→ Detect .env (secret) — exclude, warn
→ Group:
   1. feat(auth): add OAuth login flow  (oauth.ts, auth/index.ts)
   2. fix(api): handle null response in user fetch  (users.ts)
   3. docs: update README with auth setup  (README.md)
→ Show plan, wait for confirmation
→ For each: git add <paths> && git commit -m "..."
→ git log --oneline -3
```

## Workflow: `/conventional-commit-push`

Run the default workflow above. After every commit succeeds:

```bash
git push
```

If the current branch has no upstream configured:

```bash
git push -u origin "$(git branch --show-current)"
```

**Never** use `--force` or `--force-with-lease`. If the push is rejected (non-fast-forward), stop and report — do not auto-resolve. If the push fails for any reason, surface the error and let the user decide.

### Worked Example

```
User: /conventional-commit-push

(Same workflow as default, then:)
→ git push
   error: failed to push some refs (non-fast-forward)
→ STOP. Report:
   "Push rejected: branch is behind origin. Run `git pull --rebase`
    first, then re-push manually. I will not auto-resolve."
```

## Workflow: `/conventional-commit-rewrite`

Rewrites non-Conformant commit messages in recent history. **This is destructive** — it changes commit SHAs. The default policy refuses to touch any commit that already exists on a remote.

### Step 1: Determine the rewrite range

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

### Step 2: Safety checks

Three checks must pass before rewriting in place:

**Check A — Working tree clean:**
```bash
[ -z "$(git status --porcelain)" ]
```
Fail → tell user to commit/stash first; stop.

**Check B — HEAD attached:**
```bash
git symbolic-ref -q HEAD >/dev/null
```
Fail → tell user to checkout a branch; stop.

**Check C — No commit in range is on a remote:**
```bash
for sha in $(git rev-list "$base..HEAD"); do
  if [ -n "$(git branch -r --contains "$sha")" ]; then
    pushed_commits+=("$sha")
  fi
done
```

If `pushed_commits` is non-empty: **do not silently refuse.** Show the user this menu:

```
Found N commits in <base>..HEAD whose subjects are non-Conformant.
M of them are already pushed to a remote:

  abc1234  origin/main  "Added User-Agent Parser"
  def5678  origin/main  "Fixed bug"
  ...

Rewriting published history breaks pulls for collaborators. Options:

  1. Cancel — keep history as-is
  2. Rewrite locally + force-push (destructive; coordinate with team first)
  3. Cherry-pick onto a NEW branch with rewritten messages (safe; original branch untouched)

Which option? (default: 1)
```

- Option 1 → exit cleanly
- Option 2 → require explicit phrase like "yes force push" before continuing; after rewrite, run `git push --force-with-lease` (NEVER `--force`)
- Option 3 → see "Branch-based rewrite" below

### Step 3: Identify non-conformant commits

For each commit in `<base>..HEAD`, check the subject against:

```
^(feat|fix|docs|style|refactor|perf|test|build|ci|chore|revert)(\([^)]+\))?!?: .+
```

Skip commits that already match. Skip merge commits (use `git rev-list --no-merges`).

### Step 4: Generate new messages

For each non-conformant commit:

1. Inspect: `git show --stat <sha>` and the diff body if needed
2. Pick a `type` from the table above based on the change content
3. Pick an optional `scope` (module / file area) — omit if unsure
4. Write a new subject: imperative mood, lowercase, ≤72 chars, no trailing period
5. **Preserve the original commit body verbatim.** Only the subject line is rewritten. If the original body is empty, leave it empty.

See the "Mapping Common Non-Conformant Patterns" section below for typical translations.

### Step 5: Show old → new plan

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

### Step 6: Apply the rewrites (in-place)

Build the mapping file at `/tmp/cc-rewrite-map.tsv`. Each non-conformant commit gets one line:

```
<full-40-char-sha>\t<new full message including preserved body>
```

The new full message is `<new subject>\n\n<original body>` (or just `<new subject>` if there is no body). Newlines inside the message are escaped as `\n` in the TSV; `rewrite_msg.py` un-escapes them.

Then run (use absolute path to the script):

```bash
script="$HOME/.claude/skills/conventional-commit/scripts/rewrite_msg.py"
# Plugin install path may differ; resolve via:
#   script=$(find ~/.claude -name rewrite_msg.py -path '*conventional-commit*' | head -1)
FILTER_BRANCH_SQUELCH_WARNING=1 git filter-branch -f \
  --msg-filter "python3 '$script'" \
  "$base..HEAD"
```

The script reads `$GIT_COMMIT`, looks it up in `/tmp/cc-rewrite-map.tsv`, and prints the new message. Commits not in the map pass through unchanged.

**If `git filter-repo` is available** (preferred over `filter-branch`, which is deprecated): use it instead. But the bundled mapping flow currently relies on `filter-branch`; only switch if the user has `filter-repo` and prefers it.

### Step 7: Branch-based rewrite (Option 3 from Step 2)

When commits are pushed and the user picks Option 3, do this instead of in-place rewrite:

```bash
# 1. Note current branch
src=$(git branch --show-current)

# 2. Create a fresh branch off the upstream/base
git checkout -b "${src}-cc" "$base"

# 3. Cherry-pick each commit, rewriting message as you go
for sha in $(git rev-list --reverse --no-merges "$base..$src"); do
  new_msg=$(lookup_in_map "$sha")   # from Step 4 plan; or compose interactively
  git cherry-pick "$sha"
  git commit --amend -m "$new_msg"  # only the cherry-pick we just made
done

# 4. Verify, then push the new branch
git log --oneline "$base..HEAD"
git push -u origin "${src}-cc"
```

The original branch is untouched. The user can open a PR from `${src}-cc` and abandon the original branch when ready. **No force push, no destruction.**

### Step 8: Post-rewrite cleanup

After in-place rewrite (Step 6):

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

After branch-based rewrite (Step 7):

- Tell the user how to switch back if they change their mind:
  ```bash
  git checkout <original-branch>
  git branch -D <branch>-cc
  ```

### Worked Example: messy history

```
User: 커밋 메시지 다시 써줘
       (User shares git log:)
       96b6be8  gnhf #43: Added User-Agent Parser ...
       eda73c5  gnhf #42: Added JSON Schema Generator ...
       e943794  gnhf #41: Added IPv4 Subnet Calculator ...
       0a7e01e  gnhf #40: Added Markdown TOC Generator ...

Step 1 (range):
   upstream = origin/gnhf/prd-chann-tools-2026-8f2964
   base = $(git merge-base HEAD origin/main)

Step 2 (safety):
   ✓ working tree clean
   ✓ HEAD attached
   ✗ all 4 commits exist on origin/<branch>
   → Show menu (Cancel / Force-push / New branch). User picks 3.

Step 3 (regex): all 4 fail the regex (start with "gnhf #N:")

Step 4 (mapping):
   "gnhf #43: Added User-Agent Parser..."   → feat(api-network): add user-agent parser
   "gnhf #42: Added JSON Schema Generator"  → feat(data-format): add JSON schema generator
   "gnhf #41: Added IPv4 Subnet Calculator" → feat(api-network): add IPv4 subnet calculator
   "gnhf #40: Added Markdown TOC Generator" → feat(text): add Markdown TOC generator

   Drop the "gnhf #N" prefix (ticket-tracker noise; belongs in the body or a footer).
   To preserve the ticket reference, add a footer:
       Refs: gnhf#43

Step 5: show old → new plan, wait for confirmation.

Step 7 (branch-based):
   git checkout -b feature-tools-cc origin/main
   for sha in (cherry-pick each, --amend with new message)
   git push -u origin feature-tools-cc
```

## Mapping Common Non-Conformant Patterns

Use these translations when generating new subjects in Step 4.

| Original pattern | Likely Conventional rewrite |
|---|---|
| `Added X` / `Add X` | `feat: add X` (or `feat(scope): add X`) |
| `Fixed X` / `Fix X` / `Bugfix: X` | `fix: <imperative>` |
| `Updated X` (cosmetic/dep bump) | `chore: update X` or `build(deps): bump X` |
| `Updated X` (real refactor) | `refactor: <imperative>` |
| `Cleanup` / `Clean up X` | `refactor: <imperative>` or `chore: <imperative>` |
| `Renamed X to Y` | `refactor: rename X to Y` |
| `Removed X` / `Delete X` | `refactor: remove X` (or `feat!:` if breaking) |
| `WIP` / `wip` / `tmp` | `chore: work-in-progress checkpoint` |
| `Initial commit` | `chore: initial commit` |
| `Merge branch 'X'` | Skip (merge commits are excluded) |
| `[TICKET-123] Added X` | `feat: add X` + footer `Refs: TICKET-123` |
| `proj #N: Added X` | `feat(scope): add X` + footer `Refs: proj#N` |
| `Tests for X` | `test: add tests for X` |
| `Docs: <anything>` | `docs: <imperative>` |
| `Refactor X` (already imperative-ish) | `refactor: <imperative form>` |

**Rules of thumb:**

- Past tense → imperative ("Added" → "add", "Fixed" → "fix")
- Capitalized → lowercase
- Strip trailing periods
- Ticket-tracker prefixes → move to a `Refs:` footer (don't drop the linkage)
- If the type is genuinely ambiguous between `chore`, `refactor`, and `style`, prefer `chore` for tooling/config, `refactor` for code-shape changes, `style` only for whitespace/formatting

## Quick Reference

**When stuck, ask:**

| Symptom | Action |
|---|---|
| No working changes + messy history | Suggest `/conventional-commit-rewrite` |
| Working changes + messy history | Commit first, then `/conventional-commit-rewrite` |
| Pushed history + want to fix | Use Step 7 (branch-based rewrite) |
| Pre-commit hook fails | Fix the underlying issue; never `--no-verify` |
| Push rejected (non-FF) | Stop, surface error, never `--force` without explicit consent |
| `git filter-branch` warns about deprecation | `FILTER_BRANCH_SQUELCH_WARNING=1` is already set; ignore |

## Common Mistakes

**Combining feat + fix in one commit**
- **Problem:** `feat(auth): add OAuth and fix null response` mixes types
- **Fix:** Two separate commits, one feat one fix

**Past-tense subjects**
- **Problem:** "added login flow", "fixed bug"
- **Fix:** Imperative — "add login flow", "handle null response"

**`git add .` to stage everything**
- **Problem:** Accidentally stages secrets or unrelated changes
- **Fix:** Always `git add <explicit-paths>` per group

**Bypassing hooks with `--no-verify`**
- **Problem:** Hides real issues; commit "works" locally but fails CI
- **Fix:** Investigate the hook failure; fix root cause; create fresh commit

**Silently refusing rewrite of pushed history**
- **Problem:** Says "I can't" with no path forward
- **Fix:** Present the 3-option menu in Step 2 (cancel / force-push / branch-based)

**Dropping ticket references during rewrite**
- **Problem:** "gnhf #43: Added X" → "feat: add X" loses the `gnhf#43` linkage
- **Fix:** Move ticket to a `Refs: gnhf#43` footer; don't lose it

**Rewriting merge commits**
- **Problem:** Filter-branch on merges scrambles parent linkage
- **Fix:** `git rev-list --no-merges` always

## Red Flags

**Never:**
- `git add .` or `git add -A` (use explicit paths)
- `--no-verify`, `--no-gpg-sign`, `--amend` without explicit user consent
- `--force` push (`--force-with-lease` only after explicit consent)
- Commit `.env*`, `credentials.*`, `*_rsa`, `*.pem`, `*.key`, `*.p12` without explicit user override
- Combine `feat` and `fix` in one commit
- Rewrite pushed commits without showing the 3-option menu first
- Use `git filter-branch --root`
- Drop ticket references during rewrite (move them to `Refs:` footer)

**Always:**
- Show a commit plan before creating commits
- Run `git status --short` after each commit to verify
- Preserve the original commit body verbatim during rewrite
- Use `--no-merges` when listing commits to rewrite
- Default to "Cancel" when prompting on pushed commits
- Match the repo's existing scope conventions (`git log -20 --oneline` first)

## Behavior Notes

**Match the repo's existing style.** Inspect `git log -20 --oneline` first. If the repo uses Conventional Commits, mirror its scope conventions. If existing messages are mixed, default to lowercase descriptions and concise scopes.

**Narration vs. commit-message language.** Conversation updates: user's prompt language. Commit messages: language already dominant in `git log` (English when ambiguous).

**Be conservative with scopes.** A scope must name a real module/area. If unsure, omit the scope rather than invent one.

**Don't over-explain in bodies.** A body should add context the subject can't carry (the *why*, a tricky tradeoff, related issue). If the subject is self-explanatory, no body.

**Refuse, don't bypass.** If a safety check fails (pushed commits without consent, dirty tree, detached HEAD, suspected secret), report and stop. Do not work around with destructive flags.

**Trust explicit user override.** "Force push", "yes I know it's pushed, rewrite anyway", "include the .env this time" → proceed, but state the risk in one line first.

## Integration

**Pairs with:**
- **code-review** — Run `/code-review` before committing as a final quality gate
- Any plugin commit hooks (commitlint, husky) — fix violations rather than `--no-verify`

**Called by:** Manual user invocation only. Never auto-run during another skill's workflow.
