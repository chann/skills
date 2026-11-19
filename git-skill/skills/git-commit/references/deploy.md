# Deploy mode

`deploy` is `push realtime` plus a deployment and a confirmation gate after every
push. It uses the deployment settings the repository already documents; it never
creates a deployment setup or chooses a provider. Follow
`references/checkpoints.md` for the baseline, planning, verification, commit,
push, and parity steps, and insert the steps below.

Show the documented target and the checkpoint plan once, then proceed without
asking again at every checkpoint. Honor any explicit per-deployment approval that
the repository or hosting service requires.

## 1. Resolve the deployment settings before the first checkpoint

Read the applicable `AGENTS.md` files (parent and scoped) and the deployment
documents they reference, following the repository's instruction precedence and
explicit user overrides. Inspect package scripts, CI workflows, or hosting
configuration only as needed to resolve the documented route. A command named
`deploy` is supporting evidence, not permission to choose its environment.

| Setting | Evidence needed |
|---|---|
| Target | Environment, project/service, and URL when applicable |
| Route | Direct command with working directory, or CI/provider trigger |
| Source | Eligible branch, and how the pushed commit or its artifact is selected |
| Prerequisites | Required build, credentials by name, migrations, and checks |
| Confirmation | Deployment status method and any documented health or smoke checks |
| Recovery | Documented timeout, retry, and rollback rules when present |

- With one usable route, proceed without repeated confirmation. Use existing
  credentials without printing or committing their values. Keep mandatory
  migrations and build prerequisites in the documented order; never infer a
  destructive migration or reset command.
- If the command or trigger, target, source selection, or confirmation method is
  missing, contradictory, or ambiguous, stop before editing, committing, or
  pushing and ask for the specific missing setting. Never guess production
  versus staging, silently fall back to push-only, configure a new provider, or
  switch branches to satisfy a deployment filter.
- Confirm the current branch is eligible for the route before the first
  checkpoint; ask when it is not. A deployment request does not authorize a
  merge, checkout, tag, or broader deployment permissions to make a branch
  eligible.

## 2. Plan independently deployable outcomes

Each checkpoint must be usable and deployable on its own, including coupled
tests, consumers, schema changes, and required generated artifacts. Account for
schema compatibility with the running service when an outcome includes a
migration. Show each outcome with its checks and the shared target and route.

Because a push can trigger a CI deployment at once, finish the required
pre-deployment checks before the push. Never deploy a checkpoint whose push and
parity are unconfirmed.

## 3. Deploy the pushed checkpoint

Use exactly the resolved environment, project, branch, working directory, and
command or trigger, and tie every input to the recorded checkpoint SHA.

- **Direct deployment:** run the documented prerequisites and command in order.
  When the command packages local files, deploy an artifact built from the pushed
  SHA or an isolated clean checkout of that SHA that selects the same target and
  environment. Never include uncommitted or untracked content, secrets, or a
  stale artifact, and never delete or reset user files to get a clean tree.
  Record the deployment or artifact identity the command returns.
- **CI or provider deployment:** when the push already triggers deployment,
  observe that run instead of launching a duplicate command or dispatch. Find it
  by checkpoint SHA, eligible branch, and intended workflow or environment. When
  the route requires a manual trigger, trigger it once and prove the selected
  ref resolves to the checkpoint SHA; stop if it differs. Record the run ID and
  the deploy job's status URL. A finished build job does not prove the deploy
  job finished.

Never substitute the latest run on a branch for this checkpoint's evidence.

## 4. Confirm before the next checkpoint

Wait for a terminal result for the recorded identity and target. Use the
documented timeout; without one, state a finite wait limit before waiting, poll
in bounded intervals, keep progress updates flowing, and stop when the limit
passes.

The deployment is `VERIFIED` only when both hold:

1. A successful status tied to the checkpoint SHA or a traceable artifact built
   from it (for a direct deployment without a status API, the documented
   successful command result plus artifact or revision evidence); and
2. The documented health or smoke checks pass on the intended target.

An exit code of zero with a failing smoke check, a healthy old revision, or a
build-only CI success is `NOT VERIFIED`. A queued, pending, cancelled, or
timed-out deployment, or one superseded before it could be confirmed, is
`INCONCLUSIVE`, and inconclusive is never a pass: surface it and stop.

```text
Checkpoint 1/3: feat(api): add cursor pagination
Commit: <full pushed SHA>
Checks: <commands and observed results>
Upstream parity: 0 0
Target: <documented environment/service>
Deployment: <run or deployment ID, source SHA or artifact, status URL>
Confirmation: VERIFIED | NOT VERIFIED | INCONCLUSIVE — <status and smoke results>
```

Do not begin the next outcome, including local implementation work, until the
previous push, parity, deployment, and required checks are confirmed. Push
success alone never completes a deploy checkpoint. If the user explicitly changes
the sequencing, state the new order and apply it within the authorized scope,
keeping incomplete results visible and never reporting an unmet gate as passed; urgency alone does not change the sequence,
and an instruction to start local work early does not authorize skipping checks
or deploying a different target.

## Failure and recovery

| Situation | Action |
|---|---|
| Missing or ambiguous settings, or an ineligible branch | Stop before the first checkpoint and ask for the exact missing decision |
| Missing credentials or provider approval | Report the blocker without exposing secrets; honor the existing approval gate |
| Test, build, hook, push, or parity failure | Follow `references/checkpoints.md`; do not deploy |
| Deployment failed, cancelled, timed out, or smoke check failed | Stop before the next checkpoint; report the pushed SHA and the deployment evidence |
| Artifact or CI source differs from the checkpoint | Stop; never deploy or verify a different revision as this outcome |
| Recovery is documented | Follow it for this checkpoint and re-run the confirmation |
| Recovery is unspecified or unsafe to repeat | Ask; never retry, roll back, or switch targets blindly |

A source defect inside the authorized outcome is repaired as a recovery
checkpoint: verify the fix, commit it, push it, and deploy and confirm it through
steps 3–4. Record the failed SHA and its corrective SHA separately and never
relabel the failed deployment as successful. Resume the planned sequence only
after the repaired outcome is confirmed.

Keep the pushed commit when a deployment fails. Never rewrite history,
automatically revert, or force-push to hide a deployment problem. A rollback,
provider retry, or other destructive change needs explicit user authorization or
an applicable documented recovery policy.
Report partial success truthfully: committed and pushed, deployment failed or
unverified.
