# Checkpoint cadence (`realtime`, `push realtime`, `push realtime merge-main`, `deploy`)

The checkpoint modes turn a longer implementation into a sequence of reviewable,
working commits. Each checkpoint is one coherent outcome that passes the checks
appropriate to it and becomes one Conventional Commit. Unlike the default mode,
which groups changes that already exist, a checkpoint mode stays active while the
requested work is performed.

Everything in `SKILL.md` still applies. This file adds when a unit is ready and
what happens after each commit. `push realtime` adds the push step;
`push realtime merge-main` adds the final merge in `references/merge-main.md`;
`deploy` adds that merge plus `references/deploy.md`.

## What the invocation authorizes

| Mode | Authorizes | Does not authorize |
|---|---|---|
| `realtime` | Repeated local commits for the requested task | Pushes, history rewrites, unrelated changes, releases, new branches |
| `push realtime` | Repeated commits and ordinary pushes to the same-named remote branch (create it on first push) | History rewrites, force pushes, unrelated changes, releases, local branch creation |
| `deploy` | Everything `push realtime merge-main` authorizes, then one deployment of the pushed default branch to the documented target | Per-checkpoint deployments, merges into any other branch, release tags, or a different deployment target |

`push realtime merge-main` runs every `push realtime` step, then
`references/merge-main.md` once after the completion audit. `deploy` runs the
same steps and then deploys the pushed default branch once through
`references/deploy.md`.

Anything outside the authorized column needs its own explicit request.

## 1. Establish a safe baseline

Before changing files:

```bash
git status --short
git diff
git diff --cached
git log --oneline -20
git branch --show-current
git rev-parse --abbrev-ref --symbolic-full-name '@{u}' 2>/dev/null || true
```

- Stop if `HEAD` is detached.
- Record pre-existing staged, unstaged, and untracked changes. Preserve changes
  outside the requested task. If ownership overlaps or is unclear, ask before
  editing or committing those paths.
- Apply the secret check from `SKILL.md`, including the `.env.example`
  exception.
- **`realtime`:** note whether an upstream exists so the final report can state
  what remains unpushed, but do not fetch, pull, or push to reconcile it.
- **`push realtime`, `push realtime merge-main`, and `deploy`:** record the
  attached branch name and the intended remote before editing. Use the
  requested remote, otherwise the configured push remote
  (`branch.<name>.pushRemote`, `remote.pushDefault`, then the branch remote), or
  origin when unambiguous. Confirm the effective push URL is the intended
  repository. Use `refs/heads/<recorded-branch>` even when the branch tracks
  another ref. Fetch and compare that exact destination if it exists. Review
  the outgoing range, including existing commits, before publishing. If the
  branch is behind or diverged, surface the exact state and stop; do not pull,
  merge, rebase, or force-push. A missing same-name ref is created by the first
  authorized push. A clean worktree can still have commits to push.
- **`push realtime merge-main` and `deploy`:** also resolve the default branch
  as `references/merge-main.md` describes. **`deploy`:** also resolve the
  deployment settings in `references/deploy.md` step 1 before editing.

## 2. Plan outcome-based checkpoints

Break the work into the smallest sequence of independently reviewable outcomes
and show that plan before the first commit so the user can object. The
invocation then authorizes proceeding through the plan without pausing at every
checkpoint, unless the user asks for interactive approval.

A meaningful checkpoint:

- completes one user-visible behavior, internal contract, fix, refactor, or
  documentation outcome;
- leaves the repository in a usable state;
- includes the tightly coupled tests, migrations, types, and consumers needed to
  keep that outcome valid;
- can be reverted without undoing an unrelated outcome; and
- has a clear Conventional Commit type and subject.

Keep working without committing while the current state is only scaffolding or
TODO wiring, half of a rename or refactor, a producer without its consumers (or
the reverse), a migration without its safe application path, known to fail
compilation, tests, lint, or required checks, or merely large or old.

Do not split work by file count, elapsed time, token pressure, or a desire to
show activity. Accumulate dependent edits until they form one green outcome. Do
not merge unrelated `feat`, `fix`, `docs`, `refactor`, build, or CI work just to
reduce the number of commits.

## 3. Verify one checkpoint

Focus on the current outcome. Keep the plan current and tell the user when a
checkpoint boundary moves. Before declaring the checkpoint ready:

1. Review the complete diff for that outcome.
2. Run the narrowest relevant tests and repository-required checks.
3. Run `git diff --check`.
4. Confirm no failure is hidden by a skipped hook, a disabled check, or
   generated output that should not be committed.
5. Confirm the diff holds no unrelated pre-existing user changes.

A checkpoint is green only when its own acceptance criteria are proven. A
passing narrow test does not justify a broad commit whose other behavior was not
verified.

## 4. Commit the checkpoint

Show a compact checkpoint plan, then commit through the `SKILL.md` rules:

```text
Checkpoint 2/4: feat(api): add cursor pagination
Paths: src/api/pagination.ts, src/api/pagination.test.ts
Checks: pnpm test pagination; pnpm typecheck
```

```bash
git --literal-pathspecs add -- path/one path/two
git diff --cached --check
git commit -m "type(scope): description"
git status --short
```

Include only the current checkpoint. Do not create `WIP`, `tmp`, or generic
checkpoint commits; the subject describes the completed outcome. If a hook
fails, fix the cause and re-run the relevant verification rather than recording
a broken or mislabeled checkpoint.

## 5. After the commit, by mode

- **`realtime`:** After each checkpoint commit succeeds, record its hash and
  leave it local (`git log --oneline -1`, `git status --short --branch`). Do not
  run `git push`, set an upstream, or publish the checkpoint in any other way.
  Publication stays a separate, explicit user request (`/git-commit push` or
  `/gcpr`). If the upstream advances meanwhile, note the drift in the progress
  update; do not pull, merge, or rebase to chase it.
- **Every push mode** (`push realtime`, `push realtime merge-main`, `deploy`):
  After each checkpoint commit succeeds,
  push it before starting the next unit, using the push step in `SKILL.md`.
  Execute the bundled helper after reviewing the outgoing commits. Resolve its path from the installed git-commit skill directory:

  ```sh
  sh "$skill_dir/scripts/push-checkpoint.sh" "$remote" "$source_branch" "$commit"
  ```

  Record its remote, full ref and verified SHA. A local commit, a push on
  another branch, or a matching local tracking ref cannot finish a checkpoint.
  If there was no upstream, configure the same-name tracking branch after
  successful publication. Preserve an existing differently named upstream.
  For parity, fetch the verified destination and compare HEAD with that tip.
  Use `git rev-list --left-right --count HEAD...@{u}` only when the upstream
  is that destination. The expected result is `0 0`. Stop on rejection or
  failed verification before starting the next unit.
- **`deploy`:** checkpoints are never deployed. The one deployment happens
  after the completion audit and the final merge (`references/deploy.md`).

Keep the exact commit hash and check results in every progress update.

## 6. Repeat from the new baseline

The recorded (and, where applicable, pushed) commit is the baseline
for the next checkpoint. Re-check the working tree, continue the next outcome,
and repeat steps 3–5.

When the user changes direction, fold the change into the current checkpoint
only when that same outcome requires it; otherwise add or replace a later
checkpoint. Never rewrite a checkpoint that is already recorded or pushed;
correct it with a new commit. Cleaning up unpushed local history afterwards is
the `rewrite` mode's job.

## 7. Completion audit

1. Re-read the full request and verify every requirement.
2. Run the full test, lint, type, build, or package gates for the completed scope.
3. A fix found here becomes a new meaningful checkpoint through the same mode
   (committed, and pushed where the mode does that).
4. Confirm the worktree holds only known pre-existing changes, if any.
5. Show the history and state:

   ```bash
   git log --oneline <starting-commit>..HEAD
   git status --short --branch
   git rev-list --left-right --count HEAD..."$verified_remote_tip"   # push modes only
   ```

6. In `push realtime merge-main` and `deploy`, continue with
   `references/merge-main.md`; in `deploy`, finish with `references/deploy.md`.

Report each commit hash with its verification evidence. In `realtime`, state that
no checkpoint was pushed and, when an upstream exists, how many commits are ahead
of it. In push modes, report the final parity. Do not call the task complete
while any requested outcome, push, or deployment remains unverified.

## Failure handling

| Situation | Action |
|---|---|
| Relevant test or build fails | Fix the checkpoint or report the blocker; do not commit it as complete |
| Pre-commit hook fails | Fix the cause; never bypass the hook |
| Push rejected (push modes) | Stop and surface the error; never auto-reconcile or force |
| Upstream advances (push modes) | Stop before editing the next unit and ask how to reconcile |
| Upstream advances (`realtime`) | Note the drift; never pull, merge, or rebase |
| User asks to publish during `realtime` | Treat it as a new explicit request for a push mode; `realtime` itself never pushes |
| User-owned changes overlap the checkpoint | Ask before including or modifying them |
| No green intermediate boundary exists | Keep working and report progress; do not manufacture a commit |
| A recorded or pushed checkpoint needs correction | Make a new corrective commit (or revert); never rewrite published history |

## Checkpoint red flags

- Never create time-based, token-based, or file-count-based commits.
- Never commit or push a knowingly broken intermediate state.
- Never include unrelated user changes to make a checkpoint look complete.
- In push modes, never begin the next checkpoint until the previous push and upstream parity are confirmed.
- In `realtime`, never push, pull, merge, rebase, or rewrite history from this workflow.
- Always keep each commit independently reviewable and truthfully verified.
