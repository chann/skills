---
name: gen-backend-handoff
description: Use when code changes, API changes, database changes, jobs, queues, auth behavior, git diffs, commit ranges, branch comparisons, or current session context need to be turned into a handoff for backend developers, platform engineers, or server-side coding agents
---

# Backend Handoff Generator

## Overview

Create evidence-based handoff documents for backend implementers. The handoff must make the server-side contract, data model, rollout risk, verification state, and remaining work clear enough for another developer or coding agent to continue.

**Core principle:** changed server behavior in, continuation-ready backend plan out.

**Announce at start:** "I'm using the gen-backend-handoff skill to create a backend handoff."

## Scope Resolution

Use the scope the user requested. Do not broaden it.

| User asks for | Use |
|---|---|
| Current changes / no explicit scope | `git diff --stat`, `git diff`, `git diff --staged --stat`, `git diff --staged` |
| Last commit | `git diff HEAD~1..HEAD` |
| Last N commits | `git diff HEAD~N..HEAD` |
| Exact range, including reversed ranges | The exact range first; if it looks wrong or empty, report that and suggest the likely intended range |
| Branch comparison such as `main...feature` | `git diff main...feature` exactly |
| PR number | `gh pr diff <number>` if `gh` is available |

Record the final command under **Evidence**. If the user supplied `main...feature`, `HEAD~5..HEAD`, or another range, the document must state that it used the user-specified scope.

## Evidence Collection

Gather only what is needed for the handoff:

```bash
git status --short
git log --oneline --decorate -n 10
git diff --stat [scope]
git diff [scope]
```

Also use current conversation notes, Codex/Claude session summaries, pasted review comments, test output, or deployment notes when the user provides them. Label them as "User-provided session context" unless verified from files or commands.

Never include secrets from `.env`, credentials, tokens, private keys, or local-only config values.

## Required Analysis

Extract the server-side continuation surface:

- **API contract:** routes, methods, request/response schemas, status codes, headers, auth, permissions, validation, rate limits.
- **Data model:** schema changes, database migrations, seed data, backfills, indexes, constraints, rollback risk.
- **Service behavior:** business logic, feature flags, config, environment variables, third-party integrations, caching.
- **Async work:** jobs, queues, and scheduled tasks, retry policy, idempotency, dead-letter handling, observability.
- **Compatibility:** backward compatibility, old client behavior, old server version behavior, rollout order.
- **Cross-team impact:** frontend/client action, SDK action, QA action, ops action, or "No external action found".
- **Verification evidence:** tests, type checks, migrations, manual checks, or "Not verified".

Do not claim unverified tests, deploys, or runtime behavior. If there is no command output proving it, write "Not verified in this handoff."

## Output

Write the handoff to:

```text
.handoffs/<YYYY-MM-DD>_<scope>_backend.md
```

Use `working` for unstaged/staged changes, the short SHA for a single commit, or a sanitized range/branch label for explicit scopes. Create `.handoffs/` if needed.

## Document Template

```markdown
# Backend Handoff

**Date:** YYYY-MM-DD
**Scope:** [working tree | staged changes | HEAD~N..HEAD | main...feature | PR #N]
**Audience:** Backend developer or server-side coding agent

## Summary

- What changed:
- Remaining backend work:
- Primary risk:

## Evidence

- Diff command:
- Files inspected:
- User-provided session context:
- Tests/deploys verified:

## API Contract

| Endpoint | Change | Compatibility impact |
|---|---|---|

## Data And Migrations

- Database migrations:
- Schema/index/constraint changes:
- Backfill/seed data:
- Rollback notes:

## Service Behavior

- Business logic:
- Auth/permissions:
- Feature flags/config:
- Caching/integration impact:

## Jobs And Async Work

- Jobs, queues, and scheduled tasks:
- Retry/idempotency:
- Observability:

## Cross-Team Impact

- frontend/client action:
- QA action:
- Ops/deploy action:
- SDK/API docs action:

## Rollout And Backward Compatibility

- Required order:
- backward compatibility:
- Fallback:
- Known risks:

## Verification

- Tests run:
- Migration checks:
- Manual checks:
- Not verified:

## Backend Implementation Checklist

- [ ] Complete remaining code changes
- [ ] Add or update tests
- [ ] Run migration/rollback checks if applicable
- [ ] Verify API contract and compatibility
- [ ] Update docs or downstream handoffs if needed

## Open Questions

- ...

## Continuation Prompt

Use the evidence above to continue the backend implementation. Preserve the stated scope, do not assume unverified tests or deploys, and resolve open questions before modifying ambiguous API, data, or rollout behavior.
```

## Baseline Failures

| Failure observed without this skill | Required behavior with this skill |
|---|---|
| Agent writes a generic summary instead of a continuation handoff | Always include API contract, data/migration, service behavior, rollout, verification, and next steps |
| Agent misses async or operational work | Always check jobs, queues, and scheduled tasks plus deploy/observability impact |
| Agent ignores frontend/client consequences of server changes | Include frontend/client action or explicitly state none was found |
| Agent reviews more than the requested branch or commit range | Use the user-specified scope exactly, including `main...feature` |
| Agent says tests passed or deploy happened without evidence | Do not claim unverified tests, deploys, or runtime behavior |

## Common Mistakes

- Treating database migrations as implementation detail only; they are rollout and rollback risk.
- Omitting old-client or old-server compatibility.
- Forgetting job retry, idempotency, and observability changes.
- Mixing current working-tree changes with an explicit commit range.
- Copying session context as fact without labeling whether it was verified.

## Example

User: "Use `HEAD~5..HEAD` and make a backend handoff."

Expected behavior:

1. Run `git diff --stat HEAD~5..HEAD` and `git diff HEAD~5..HEAD`.
2. Extract API contract, database migrations, service behavior, jobs, queues, and scheduled tasks.
3. Write `.handoffs/YYYY-MM-DD_HEAD-5-HEAD_backend.md`.
4. Include backend remaining work, rollout/backward compatibility, verification evidence, and a Continuation Prompt.
