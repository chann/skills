---
description: Commit, push, deploy, and confirm each meaningful outcome using documented repository deployment settings
---

Use the **git-commit-push-deploy** skill for the requested implementation.

Read the canonical skill and its required shared workflows before any Git command
or deployment. Resolve the deployment command/trigger, working directory, target,
eligible branch, and confirmation method from AGENTS.md or referenced repository
instructions before editing or pushing. Stop and ask for specific missing or
ambiguous settings rather than inventing a provider or target.

Plan meaningful, independently deployable outcome checkpoints. Verify one complete
unit, stage explicit paths, create a Conventional Commit, push it normally, prove
upstream parity, and deploy that exact pushed revision. Observe CI triggered by
the push instead of starting a duplicate deployment. Confirm deployment success
and required health/smoke checks before starting the next unit.

The request authorizes repeated deployments to the documented target without
repeated confirmation, subject to existing mandatory approval gates. Preserve
unrelated changes and keep them out of deployment inputs. Never create broken or
time-based commits, bypass hooks, auto-reconcile upstream drift, force-push, switch
targets, merge branches, create release tags, or perform an undocumented rollback.
On push or deployment failure, report the commit and evidence and stop before
the next planned outcome. A source correction within the authorized task is a
recovery checkpoint and must pass the same commit, push, deploy, and confirmation
gates. Apply an explicit user change to sequencing while preserving truthful
deployment evidence. Never treat push success alone as a verified deployment.
