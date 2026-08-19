---
name: git-resolve-conflicts
description: Use when a merge, rebase, cherry-pick, revert, or stash pop has stopped with conflicts and the working tree must be finished rather than abandoned, including "충돌 해결해줘", "머지 컨플릭트 정리해줘", "rebase 중에 멈췄어", "resolve these conflicts", "finish this merge", "fix the conflict markers", "/git-resolve-conflicts", or "$git-resolve-conflicts". Classifies every conflicted path, recovers both sides' intent before touching a hunk, records which intent survived, and runs the project's own checks. Never aborts and never invents behavior. For merging a clean branch use git-merge-to-main or git-merge-to-dev.
---

# Git Resolve Conflicts

Finish an in-progress merge, rebase, cherry-pick, revert, or stash pop. The
operation completes; it is never aborted to make the conflict go away.

Conflicts are resolved wrongly for one reason: someone edits the markers without
knowing why either side wrote that code. This workflow recovers both intents
first, resolves by class rather than by reflex, and records which intent survived
each hunk so the resolution can be reviewed.

## 1. See where the operation stopped

```bash
git status --short --branch
git rev-parse --git-dir
ls "$(git rev-parse --git-dir)" | grep -E 'MERGE_HEAD|REBASE|CHERRY_PICK_HEAD|REVERT_HEAD'
git diff --name-only --diff-filter=U -z | tr '\0' '\n'
git log --oneline --left-right --boundary HEAD...MERGE_HEAD 2>/dev/null | head -40
```

Establish, before anything else:

- **Which operation** is in progress. The continue command differs —
  `git merge --continue`, `git rebase --continue`, `git cherry-pick --continue`,
  `git revert --continue`. During a rebase, "ours" and "theirs" are swapped
  relative to a merge; getting this backwards is the most common wrong resolution.
- **The stated goal** of the operation. "Bring `feature` into `main`" and "replay
  my commits on top of `main`" resolve the same hunk differently.
- **Every conflicted path**, from `--diff-filter=U`, not from grepping for markers.
  A path can be conflicted with no markers in it — a delete/modify or a rename
  conflict has no text to mark.

Turn on the base view for the whole session so each hunk shows what both sides
changed *from*:

```bash
git checkout --conflict=zdiff3 -- .
```

Two sides without the base is a guess; three sides is a decision. If
`git rerere` is enabled, note which hunks it resolved automatically and review
them like any other — a replayed resolution can be stale.

## 2. Classify every conflicted path

Each class has a fixed policy. Assign one to every path before editing any of
them, and write the list down.

| Class | How to tell | Policy |
|---|---|---|
| **Source** | Hand-written code or config | Resolve hunk by hunk, per step 3 |
| **Lockfile** | `package-lock.json`, `pnpm-lock.yaml`, `poetry.lock`, `Cargo.lock`, `go.sum`, `Gemfile.lock` | Never hand-merge. Resolve the manifest first, then regenerate the lockfile with the project's own tool |
| **Generated** | Build output, compiled schemas, generated clients, `dist/`, snapshots | Never hand-merge. Resolve the source, then re-run the generator |
| **Binary** | Images, archives, fonts, anything Git reports as binary | Pick one side deliberately with `--ours` or `--theirs`, and record why. There is no merge |
| **Submodule** | Conflicted gitlink entry | Choose the commit that matches the operation's goal, verified in the submodule's own log. Never pick blind |
| **Delete/modify** | `git status` shows deleted by one side, modified by the other | A decision, not a merge: is the file gone or does the modification still apply? Recover the deleting commit's intent before answering |
| **Rename** | Git reports a rename/rename or rename/delete conflict | Resolve the path first, then apply both content changes to the surviving path |

Getting the class right is most of the work. A hand-merged lockfile is the single
most common way a resolved merge produces an unbuildable tree, and it looks
perfectly reasonable in review.

## 3. Recover both intents before touching a hunk

For each conflicted source path, find out why each side wrote what it wrote:

```bash
git log --oneline -5 HEAD -- <path>
git log --oneline -5 MERGE_HEAD -- <path>
git log -1 --format='%H%n%an%n%s%n%n%b' <commit>
```

Read the commit messages on both sides. Where the repository links to a tracker
or uses pull requests, follow the reference — the reason a line changed is
usually recorded outside the diff. `git log -L` on the conflicting range narrows
this quickly when the file is large.

A hunk you cannot explain from both sides is not ready to resolve. Say what you
could not determine rather than picking the side that looks newer.

## 4. Resolve each hunk, keeping both intents where possible

Work one path at a time, and for each hunk:

1. **Preserve both intents** when the changes are compatible. Two sides adding
   different fields, different cases, or different guards usually both belong.
   This is the common case and it is the one reflexive `--ours`/`--theirs` throws
   away.
2. **When they are incompatible**, keep the one that matches the operation's
   stated goal, and record the trade-off — what the other side wanted and what is
   now lost.
3. **Invent nothing.** No new behavior, no refactor, no drive-by improvement, no
   "while I'm in here" rename. A conflict resolution that introduces a third
   behavior neither side wrote is undetectable in review and impossible to
   attribute later.
4. **Remove every marker.** `<<<<<<<`, `=======`, `>>>>>>>`, and `|||||||`.

Wholesale `git checkout --ours <path>` or `--theirs <path>` on a **source** file
discards one side's work in one command. It is allowed only with a recorded
reason naming what was discarded — and during a rebase, remember the labels are
swapped.

Record each resolution in a ledger as you go:

```markdown
| Path | Hunk | Ours wanted | Theirs wanted | Resolution |
|---|---|---|---|---|
| src/auth/session.ts | expiry check | 30-minute idle timeout | absolute 24-hour cap | Both kept; whichever fires first ends the session |
| pnpm-lock.yaml | — | — | — | Regenerated from the merged package.json |
```

Then stage the path and confirm nothing is left:

```bash
git add -- <path>
git diff --check
git grep -nE '^(<{7}|={7}|>{7}|\|{7})' -- . || true
```

## 5. Prove the tree still works

Discover the project's own checks rather than assuming a command — look at
`package.json` scripts, `Makefile`, `pyproject.toml`, `Cargo.toml`, or the CI
workflow. Run them in the cheap-to-expensive order the project implies:
typecheck, tests, lint, format.

Fix what the merge broke. A test that fails because both intents are now present
is real information: usually the two changes need a small integration that
neither side wrote alone, and that integration belongs in this commit.

A check that was already failing before the operation started is not yours to
fix — say so and leave it.

## 6. Complete the operation

```bash
git merge --continue      # or rebase / cherry-pick / revert --continue
git status --short --branch
git log --oneline -3
```

Report:

- the operation and its stated goal;
- every path with its class and resolution;
- each hunk where one intent was dropped, and what was lost;
- the checks that ran and their results;
- anything unresolved, named explicitly.

Do not push. Publication is a separate, explicit request — `git-commit-push` or
`/gcpr`.

## Refusals

- Never run `--abort` or `--skip` to make a conflict disappear. If the operation
  genuinely should not proceed, say so and stop; the user decides to abort.
- Never hand-merge a lockfile or a generated file. Regenerate it.
- Never resolve a submodule conflict without checking that submodule's log.
- Never use `--ours` or `--theirs` on a source file without recording what was
  discarded.
- Never invent behavior neither side wrote.
- Never leave a conflict marker, and never stage a path that still has one.
- Never force-push, rewrite history, or push at all from this workflow.
- Never claim the tree is green without having run the project's own checks.

## Integration

**Pairs with:** `git-merge-to-main` and `git-merge-to-dev`, which route here when a
merge stops; `bug-hunt` when a check fails after the resolution and the cause is
not obvious; `git-commit-push` to publish afterwards.

**Use instead of:** editing conflict markers directly, which loses both intents
and the record of the trade-off.
