---
name: git-commit-push-deploy
description: Use when the user wants an implementation committed, pushed, and deployed at meaningful checkpoints while work continues, including "commit push and deploy as you work", "keep committing pushing and deploying", "작업 중간중간 커밋 푸시 배포", "의미 있는 단위마다 배포", "/git-commit-push-deploy", "$git-commit-push-deploy", "/gcpd", or "$gcpd". Produces verified Conventional Commits, remote parity, and confirmed deployments using settings already documented in AGENTS.md or repository deployment instructions. Use git-commit-push-realtime for checkpoints that require commit and push only.
---

# Git Commit + Push + Deploy

## Overview

Complete each meaningful implementation outcome through verification, a
Conventional Commit, an ordinary push, and the repository's configured deployment.
Record the commit hash, upstream parity, deployment identity, target, and check
results for every checkpoint before moving on.

This extends `git-commit-push-realtime` with a deployment gate after every push.
Assume deployment settings already exist in `AGENTS.md` or its referenced
repository instructions; read and use them instead of creating a deployment
setup or choosing a provider.

The user's invocation authorizes repeated commits, ordinary pushes, and deployments
to the documented target for the requested task. Show that target and the
checkpoint plan once, then proceed without asking again at every checkpoint.
Honor an explicit per-deployment approval requirement in the repository or hosting
service. The invocation does not authorize unrelated changes, history rewrites,
force pushes, branch merges, release tags, or a different deployment target.

**Announce at start:** "I'm using the git-commit-push-deploy skill to commit, push,
and verify deployments at meaningful checkpoints using this repository's settings."

## Required shared workflow

Before any Git command, locate and read these installed skills completely:

1. `<plugin-root>/skills/git-commit-push-realtime/SKILL.md` for the baseline,
   outcome boundaries, verification, commit, push, and upstream-parity proof.
2. `<plugin-root>/skills/git-commit/SKILL.md` for Conventional Commits, secret
   checks, explicit staging, hooks, and every shared commit safety rule.
3. `<plugin-root>/skills/git-commit-push/SKILL.md` for ordinary pushes and
   rejection handling.

Resolve them from the owning plugin or installed skill locations. If any required
skill is missing, stop before any Git command and report the missing dependency;
do not reconstruct its workflow from memory.

Apply the realtime workflow through its commit and push steps for each outcome.
Insert the deployment and confirmation gates below before its repeat or finish
steps. A successful push alone never completes a deployment checkpoint.

## Workflow

### 1. Read the deployment settings and establish the baseline

Read applicable `AGENTS.md` instructions, including parent and scoped files, and
the deployment documents they reference. Follow the repository's instruction
precedence and explicit user overrides. Inspect referenced package scripts, CI
workflows, or hosting configuration only as needed to resolve the documented
route. Treat a command named `deploy` as supporting evidence, not as permission to
choose its environment.

Resolve and record:

| Setting | Evidence needed |
|---|---|
| Target | Environment, project/service, and URL when applicable |
| Route | Direct command with working directory, or CI/provider trigger |
| Source | Eligible branch and how the pushed commit or its artifact is selected |
| Prerequisites | Required build, credentials by name, migrations, and checks |
| Confirmation | Deployment status method and any documented health/smoke checks |
| Recovery | Documented timeout, retry, and rollback rules when present |

When these settings identify one usable route, proceed with that route without
requesting repeated confirmation. Use existing credentials without printing their
values or committing them. Keep mandatory migrations and build prerequisites in
the documented order; do not infer destructive migration or reset commands.

If the command/trigger, target, source selection, or confirmation method is
missing, contradictory, or ambiguous, stop before editing, committing, or pushing
and ask for the specific missing setting. Never guess production versus staging,
silently fall back to push-only, configure a new deployment provider, or switch
branches to satisfy a deployment filter.

Then follow the realtime skill's safe-baseline step: inspect all existing changes,
the branch, local commits, and the fetched upstream. Stop on detached HEAD,
behind/diverged history, unclear ownership, or an unresolved ahead-commit scope.
Confirm that the current branch is eligible for the configured deployment route
before the first checkpoint; ask when it is not.

### 2. Plan outcomes that can be deployed independently

Use the realtime skill's outcome-based boundaries. Each checkpoint must be usable
and independently deployable, including coupled tests, consumers, schema changes,
and required generated artifacts. Accumulate dependent edits until that is true.
Do not split work by file count, elapsed time, or token pressure. Never publish
scaffolding, `WIP`, half a rename, or a knowingly broken intermediate state.

Show each planned outcome with its relevant checks and the shared deployment
target/route. Account for schema compatibility with the running service when
migrations are part of an outcome. Keep documenting an already completed behavior
separate when repository publishing rules allow it.

### 3. Verify, commit, and push one complete outcome

Follow the realtime skill's work, commit, and immediate-push steps exactly:

1. Review the full checkpoint diff, exclude unrelated changes, and run relevant
   tests plus repository-required build and other checks.
2. Run `git diff --check`; stage explicit paths only and create a truthful
   Conventional Commit without bypassing hooks.
3. Capture the full checkpoint SHA and push it normally.
4. Confirm `git rev-list --left-right --count HEAD...@{u}` returns `0 0`.

On a hook failure, rejected push, or moved upstream, stop as the shared workflow
requires. Never deploy a checkpoint whose push and parity are unconfirmed. Since
a push can trigger CI deployment immediately, resolve deployment settings and
complete required pre-deployment checks before that push.

### 4. Deploy the pushed checkpoint through the configured route

Use exactly the resolved environment, project, branch, working directory, and
command/trigger. Keep deployment inputs tied to the recorded checkpoint SHA.

**Direct deployment:** run documented build prerequisites and the deployment
command in their specified order. Use an artifact built from the pushed SHA or
an isolated clean checkout of that SHA when the command packages local files.
Verify that this checkout selects the same documented target and uses the required
environment. Preserve unrelated user files; never include uncommitted or untracked
content, secrets, or a stale artifact in the deployment. Record the deployment or
artifact identity returned by the command.

**CI/provider deployment:** if the push already triggers deployment, observe that
deployment rather than launching a duplicate command or dispatch. Locate the run
by checkpoint SHA, eligible branch, and intended workflow/environment. If the
documented route instead requires a manual trigger, trigger it once and verify
that its selected ref/source resolves to the checkpoint SHA. Record the run ID
and deployment job/status URL. A build job completing does not prove the deploy
job completed.

Never substitute the latest run on a branch for evidence about this checkpoint.
If a manual trigger can deploy only a moving ref, prove which SHA the run selected;
stop if it differs. Do not merge to `main`, create a tag, or broaden deployment
permissions as a shortcut.

### 5. Confirm deployment before starting the next checkpoint

Wait for a terminal deployment result for the recorded identity and target.
Use the documented timeout; if none exists, state a finite wait limit before
waiting and stop when it is exceeded. Poll in bounded intervals and keep progress
updates flowing while a remote job runs.

Require both:

1. Successful deployment status tied to the checkpoint SHA or a traceable artifact
   built from it. For direct deployments without a separate status API, use the
   documented successful command result and artifact/revision evidence.
2. Passing documented health/smoke checks for the intended target. A healthy old
   revision or a build-only CI success cannot substitute for deployment evidence.

A deployment command exiting zero is insufficient when a required smoke check
fails. A queued, pending, cancelled, timed-out, or failed deployment remains
unverified. If another deployment supersedes this checkpoint before it can be
confirmed, surface the mismatch and stop instead of claiming success.

Record a compact checkpoint report:

```text
Checkpoint 1/3: feat(api): add cursor pagination
Commit: <full pushed SHA>
Checks: <commands and observed results>
Upstream parity: 0 0
Target: <documented environment/service>
Deployment: <run/deployment ID, source SHA or artifact, status URL>
Confirmation: <deployment result and required smoke-check results>
```

Under the default sequence, do not begin the next planned outcome, including local
implementation work, until the previous push, upstream parity, deployment, and
required checks are confirmed.
On success, re-check the working tree and upstream before the next outcome and
repeat from step 3.

If the user explicitly changes the sequencing during the task, state the changed
order and apply it within the authorized scope. Keep incomplete deployment results
visible and never report an unmet gate as passed. Urgency alone does not change
the sequence; an instruction to start local work early does not by itself
authorize skipping deployment checks or deploying a different target.

### 6. Finish with a completion audit

Run the realtime skill's full-scope completion audit. Any corrective source change
is a new meaningful checkpoint and goes through commit, push, deployment, and
confirmation again. Do not rewrite already published commits.

Confirm the final commit matches its upstream and the final verified deployment.
Report checkpoint hashes, check results, targets, and deployment evidence; preserve
known pre-existing changes. Do not claim completion while any requested outcome,
push, deployment, or required runtime check remains unverified.

## Failure handling

| Situation | Action |
|---|---|
| Missing/ambiguous deployment settings or ineligible branch | Stop before the first checkpoint; request the exact missing decision |
| Missing credentials or provider approval | Report the blocker without exposing secrets; honor the existing approval gate |
| Test, build, hook, push, or parity failure | Follow the shared workflow; do not proceed to deployment |
| Deployment failure, cancellation, timeout, or failed smoke check | Stop before the next checkpoint and report the pushed SHA plus deployment evidence |
| Artifact or CI source differs from the checkpoint | Stop; do not deploy or verify a different revision as this outcome |
| Recovery is documented | Follow that recovery for this checkpoint and re-run deployment confirmation |
| Recovery is unspecified or unsafe to repeat | Ask for recovery guidance; never retry, rollback, or switch targets blindly |

If the failure requires a source correction within the authorized task, work on
that same outcome as a recovery checkpoint. Verify the correction, create a new
commit, push it, and deploy and confirm it through steps 3–5. Record the failed
SHA and its corrective SHA separately; never relabel the failed deployment as
successful. This repair is part of the current outcome, not permission to begin
the next unrelated outcome. Resume the planned sequence only after the repaired
outcome is confirmed. Provider retries, rollbacks, or destructive changes still
require the documented recovery policy or explicit user authorization.

Keep the pushed commit when deployment fails. Do not rewrite history, automatically
revert, or force-push to conceal a deployment problem. A rollback requires explicit
user authorization or an applicable documented recovery policy. Report partial
success truthfully: committed/pushed, deployment failed or unverified.

## Integration

**Pairs with:** `code-review` or `code-review-md` for checkpoint review and the
repository's documented deployment and runtime checks.

**Use instead of:** `git-commit-push-realtime` when the user requests deployment
at each implementation checkpoint. Use `git-commit-push` to publish already
completed working-tree changes, or `git-commit-realtime` for local-only checkpoints.

**Called by:** Explicit user intent to commit, push, and deploy while working,
including `/gcpd` and `$gcpd`. Never add this workflow as an automatic
post-completion hook or reinterpret `/gcpr` as a deployment request.
