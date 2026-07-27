---
name: git-commit-push-realtime
description: Use when the user wants an implementation committed and pushed continuously at meaningful checkpoints instead of only once at the end. Trigger on phrases like "commit and push as you work", "keep committing and pushing", "작업 중간중간 커밋 푸시", "의미 있는 단위마다 푸시", "/git-commit-push-realtime", "$git-commit-push-realtime", or the short aliases "/gcpr" and "$gcpr". Runs verified, outcome-based Conventional Commit checkpoints and pushes each one immediately without force.
---

# Git Commit + Push Realtime

## Overview

Turn a longer implementation into a sequence of reviewable, working checkpoints.
Each checkpoint represents one coherent outcome, passes the checks appropriate to
that outcome, becomes one Conventional Commit, and is pushed immediately.

This differs from `git-commit-push`, which groups changes that already exist.
This skill stays active while the requested work is being performed and creates
checkpoints as meaningful units become complete.

The user's invocation pre-authorizes repeated commits and ordinary pushes for the
requested task. It does not authorize history rewrites, force pushes, unrelated
changes, releases, or new branches unless the user requested those separately.

**Announce at start:** "I'm using the git-commit-push-realtime skill to create and
push verified checkpoints as I work."

## Required shared workflow

Before starting, read both shared skills:

1. `<plugin-root>/skills/git-commit/SKILL.md` for inspection, grouping,
   Conventional Commit formatting, secret checks, explicit staging, hook
   handling, and red flags.
2. `<plugin-root>/skills/git-commit-push/SKILL.md` for ordinary push behavior
   and non-fast-forward failure handling.

Apply their safety rules throughout this workflow. Where this skill adds realtime
behavior, the rules below define when a unit is ready to commit and when work
continues without a commit.

## Workflow

### 1. Establish a safe baseline

Inspect the repository before changing files:

```bash
git status --short
git diff
git diff --cached
git log --oneline -20
git branch --show-current
git rev-parse --abbrev-ref --symbolic-full-name '@{u}' 2>/dev/null || true
```

When an upstream exists, fetch and compare it before the first checkpoint:

```bash
git fetch
git status --short --branch
git rev-list --left-right --count HEAD...@{u}
```

- Stop if `HEAD` is detached.
- If the branch is behind or diverged from its upstream, surface the exact
  state and stop. Do not pull, merge, rebase, or force-push automatically.
- If local commits are already ahead, explain that the first push will publish
  them and confirm they belong in scope before continuing.
- If no upstream exists, state that the first push will configure one.
- Record pre-existing staged, unstaged, and untracked changes. Preserve changes
  outside the requested task. If ownership overlaps or is unclear, ask before
  editing or committing those paths.
- Apply the shared secret check. The exact basename `.env.example` remains the
  public-template exception defined by `git-commit`.

### 2. Plan outcome-based checkpoints

Break the requested work into the smallest sequence of independently reviewable
outcomes. Show the initial checkpoint plan before the first commit so the user
can object. The realtime invocation authorizes proceeding through that plan without
pausing for approval at every checkpoint unless the user asks for interactive
approval.

A meaningful checkpoint:

- completes one user-visible behavior, internal contract, fix, refactor, or
  documentation outcome;
- leaves the repository in a usable state;
- includes tightly coupled tests, migrations, types, and consumers needed to
  keep that outcome valid;
- can be reverted without undoing an unrelated outcome; and
- has a clear Conventional Commit type and subject.

Good checkpoint examples:

- a bug fix together with its regression test;
- a backward-compatible schema change together with the model and migration
  checks required to use it safely;
- one service capability together with its unit tests;
- a complete refactor that preserves behavior and passes the affected tests;
- documentation for an already completed behavior as a separate `docs` unit.

Keep working without committing when the current state is only:

- scaffolding, placeholders, or TODO-only wiring;
- half of a rename or refactor;
- a producer without required consumers, or the reverse;
- a migration without its safe application path;
- known to fail compilation, tests, lint, or repository-required checks; or
- merely large, old, or time-consuming.

Do not split work by file count, elapsed time, token pressure, or a desire to
produce activity. Accumulate dependent edits until they form one green outcome.
Do not combine unrelated `feat`, `fix`, `docs`, `refactor`, build, or CI work
just to reduce the number of pushes.

### 3. Work through one checkpoint

Focus on the current planned outcome. Keep the task plan current when scope or
dependencies change, and tell the user when a checkpoint boundary moves.

Before declaring the checkpoint ready:

1. Review the complete diff for that outcome.
2. Run the narrowest relevant tests and repository-required checks.
3. Run `git diff --check`.
4. Confirm failures are not being hidden by skipped hooks, disabled checks, or
   generated output that should not be committed.
5. Confirm the diff contains no unrelated pre-existing user changes.

A checkpoint is green only when its own acceptance criteria are proven. A
passing narrow test does not justify a broad commit whose other behavior was not
verified.

### 4. Create the checkpoint commit

Re-inspect the working tree and present a compact checkpoint plan:

```text
Checkpoint 2/4: feat(api): add cursor pagination
Paths:
- src/api/pagination.ts
- src/api/pagination.test.ts
Checks:
- pnpm test pagination
- pnpm typecheck
```

Then use the shared `git-commit` workflow:

```bash
git status --short
git diff -- path/one path/two
git diff --cached
git add path/one path/two
git diff --cached --check
git commit -m "type(scope): description"
git status --short
```

- Stage explicit paths only. Never use `git add .` or `git add -A`.
- Include only the current checkpoint.
- Do not bypass hooks with `--no-verify` or `--no-gpg-sign`.
- If a hook fails, fix the cause and re-run the relevant verification. Do not
  publish a broken or mislabeled checkpoint.
- Do not create `WIP`, `tmp`, or generic checkpoint commits. The commit subject
  must describe the completed outcome.

### 5. Push immediately

After each checkpoint commit succeeds, push it before starting the next unit:

```bash
git push
```

If the branch has no upstream:

```bash
git push -u origin "$(git branch --show-current)"
```

Then prove that the checkpoint reached the configured upstream:

```bash
git status --short --branch
git rev-list --left-right --count HEAD...@{u}
```

The expected result after a successful push is `0 0`. Preserve the pushed
commit hash in the progress update.

If the push is rejected or the upstream moved:

- stop before starting another checkpoint;
- surface the exact error and ahead/behind state;
- do not retry through `pull`, merge, rebase, `--force`, or
  `--force-with-lease`; and
- ask the user how to reconcile the branch.

### 6. Repeat from the new baseline

After a successful push, treat that commit as the baseline for the next
checkpoint. Re-check the working tree, continue the next planned outcome, and
repeat verification, explicit staging, commit, push, and parity proof.

If the user changes direction:

- fold the change into the current checkpoint only when it is required for that
  same outcome;
- otherwise add or replace a later checkpoint;
- do not rewrite a checkpoint that was already pushed; use a new corrective
  commit when necessary.

### 7. Finish with a completion audit

After the final checkpoint:

1. Re-read the full user request and verify every requirement.
2. Run the appropriate full test, lint, type, build, or package gates for the
   completed scope.
3. If final verification creates a fix, make it a new meaningful commit and
   push it through the same workflow.
4. Confirm the worktree contains only known pre-existing changes, if any.
5. Show the checkpoint history and final remote parity:

```bash
git log --oneline <starting-commit>..HEAD
git status --short --branch
git rev-list --left-right --count HEAD...@{u}
```

Report each pushed commit hash, its verification evidence, and the final
upstream parity. Do not describe the task as complete while any requested
outcome or remote push remains unverified.

## Failure handling

| Situation | Action |
|---|---|
| Relevant test or build fails | Fix the checkpoint or report the blocker; do not commit it as complete |
| Pre-commit hook fails | Fix the cause; never bypass the hook |
| Push is rejected | Stop and surface the error; never auto-reconcile or force |
| Upstream advances between checkpoints | Stop before editing the next unit and ask how to reconcile |
| User-owned changes overlap the checkpoint | Ask before including or modifying them |
| A task has no green intermediate boundary | Continue working and communicate progress; do not manufacture a commit |
| A pushed checkpoint needs correction | Create and push a new fix or revert; do not rewrite published history |

## Red flags

In addition to every red flag from `git-commit` and `git-commit-push`:

- Never create time-based, token-based, or file-count-based commits.
- Never push a knowingly broken intermediate state.
- Never include unrelated user changes to make a checkpoint look complete.
- Never begin the next checkpoint until the previous push and upstream parity
  are confirmed.
- Always keep each commit independently reviewable and truthfully verified.
- Always preserve exact commit hashes and check results in progress updates.

## Integration

**Pairs with:** `code-review` or `code-review-md` for checkpoint review, and
task planning tools for maintaining outcome boundaries during long work.

**Use instead of:** `git-commit-push` when the user explicitly wants commits
and pushes during implementation. Use `git-commit-push` when the work is already
complete and only the current changes need grouping and publication.

**Called by:** Manual user invocation only. Do not enable recurring commits and
pushes implicitly from another skill.
