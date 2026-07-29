---
name: git-commit-realtime
description: Use when the user wants an implementation committed continuously at meaningful checkpoints while pushing stays a separate, explicit step. Trigger on phrases like "commit as you work", "keep committing without pushing", "작업 중간중간 커밋만", "푸시 없이 의미 단위마다 커밋", "/git-commit-realtime", "$git-commit-realtime", or the short aliases "/gcr" and "$gcr". Runs verified, outcome-based Conventional Commit checkpoints and keeps every checkpoint local.
---

# Git Commit Realtime

## Overview

Turn a longer implementation into a sequence of reviewable, working checkpoints.
Each checkpoint represents one coherent outcome, passes the checks appropriate to
that outcome, and becomes one Conventional Commit that stays local.

This differs from `git-commit`, which groups changes that already exist, and from
`git-commit-push-realtime`, which publishes every checkpoint immediately. This
skill stays active while the requested work is being performed and creates
checkpoints as meaningful units become complete — without touching the remote.

The user's invocation pre-authorizes repeated local commits for the requested
task. It does not authorize pushes, history rewrites, unrelated changes,
releases, or new branches unless the user requested those separately.

**Announce at start:** "I'm using the git-commit-realtime skill to create
verified local checkpoints as I work."

## Required shared workflow

Before starting, read the shared skill:

1. `<plugin-root>/skills/git-commit/SKILL.md` for inspection, grouping,
   Conventional Commit formatting, secret checks, explicit staging, hook
   handling, and red flags.

Apply its safety rules throughout this workflow. Where this skill adds realtime
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

- Stop if `HEAD` is detached.
- Note whether an upstream exists so the completion report can state what
  remains unpushed, but do not fetch, pull, or push to reconcile it.
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
just to reduce the number of commits.

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
  record a broken or mislabeled checkpoint.
- Do not create `WIP`, `tmp`, or generic checkpoint commits. The commit subject
  must describe the completed outcome.

### 5. Record the checkpoint and stay local

After each checkpoint commit succeeds, record its hash and leave it local:

```bash
git log --oneline -1
git status --short --branch
```

- Do not run `git push`, set an upstream, or otherwise publish the checkpoint.
  Publication stays a separate, explicit user request such as
  `/git-commit-push` or `/gcpr`.
- If an upstream exists and advances while working, note the drift in the
  progress update; do not pull, merge, or rebase to chase it.
- Preserve the recorded commit hash in the progress update.

### 6. Repeat from the new baseline

After a recorded checkpoint, treat that commit as the baseline for the next
one. Re-check the working tree, continue the next planned outcome, and repeat
verification, explicit staging, commit, and hash recording.

If the user changes direction:

- fold the change into the current checkpoint only when it is required for that
  same outcome;
- otherwise add or replace a later checkpoint;
- do not rewrite a checkpoint that is already part of the recorded sequence;
  use a new corrective commit when necessary. History cleanup afterward belongs
  to `git-commit-rewrite`.

### 7. Finish with a completion audit

After the final checkpoint:

1. Re-read the full user request and verify every requirement.
2. Run the appropriate full test, lint, type, build, or package gates for the
   completed scope.
3. If final verification creates a fix, make it a new meaningful commit through
   the same workflow.
4. Confirm the worktree contains only known pre-existing changes, if any.
5. Show the checkpoint history and the unpushed state:

```bash
git log --oneline <starting-commit>..HEAD
git status --short --branch
```

Report each commit hash and its verification evidence, and state explicitly
that no checkpoint has been pushed. When an upstream exists, state how many
commits are ahead of it and leave publication to the user. Do not describe the
task as complete while any requested outcome remains unverified.

## Failure handling

| Situation | Action |
|---|---|
| Relevant test or build fails | Fix the checkpoint or report the blocker; do not commit it as complete |
| Pre-commit hook fails | Fix the cause; never bypass the hook |
| User asks to publish mid-run | Treat it as an explicit handoff to `git-commit-push` or `git-commit-push-realtime`; this workflow itself never pushes |
| Upstream advances while working | Note the drift in the progress update; do not pull, merge, or rebase to chase it |
| User-owned changes overlap the checkpoint | Ask before including or modifying them |
| A task has no green intermediate boundary | Continue working and communicate progress; do not manufacture a commit |
| A recorded checkpoint needs correction | Create a new corrective commit; leave history cleanup to `git-commit-rewrite` |

## Red flags

In addition to every red flag from `git-commit`:

- Never create time-based, token-based, or file-count-based commits.
- Never commit a knowingly broken intermediate state.
- Never include unrelated user changes to make a checkpoint look complete.
- Never push, pull, merge, rebase, or rewrite history from this workflow.
- Always keep each commit independently reviewable and truthfully verified.
- Always preserve exact commit hashes and check results in progress updates.

## Integration

**Pairs with:** `code-review` or `code-review-md` for checkpoint review, and
task planning tools for maintaining outcome boundaries during long work.

**Use instead of:** `git-commit` when the user explicitly wants commits during
implementation instead of one grouping pass at the end. Use
`git-commit-push-realtime` when each checkpoint should also be pushed
immediately.

**Called by:** Manual user invocation only. Do not enable recurring commits
implicitly from another skill.
