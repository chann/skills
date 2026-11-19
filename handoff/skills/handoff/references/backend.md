# Backend handoff

Audience: backend developers, platform engineers, and server-side coding agents.
Output: `.handoffs/<YYYY-MM-DD>_<scope>_backend.md`.

**Core principle:** changed server behavior in, continuation-ready backend plan
out. The document makes the server-side contract, data model, rollout risk,
verification state, and remaining work clear enough for someone else to continue.

## Required analysis

Extract the server-side continuation surface:

- **API contract:** routes, methods, request and response schemas, status codes,
  headers, auth, permissions, validation, rate limits.
- **Data model:** schema changes, database migrations, seed data, backfills,
  indexes, constraints, rollback risk.
- **Service behavior:** business logic, feature flags, config, environment
  variables, third-party integrations, caching.
- **Async work:** jobs, queues, and scheduled tasks; retry policy, idempotency,
  dead-letter handling, observability.
- **Compatibility:** backward compatibility, old client behavior, old server
  version behavior, rollout order.
- **Cross-team impact:** frontend/client action, SDK action, QA action, ops
  action, or "No external action found".
- **Verification evidence:** tests, type checks, migrations, manual checks, or
  "Not verified".

Database migrations are rollout and rollback risk, not an implementation detail.
Report jobs and queues as changed or explicitly as unchanged.

## Template

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

## Audience-specific failures

| Failure observed without this reference | Required behavior |
|---|---|
| Writes a generic summary instead of a continuation handoff | Always include API contract, data and migrations, service behavior, rollout, verification, and next steps |
| Misses async or operational work | Always check jobs, queues, and scheduled tasks, plus deploy and observability impact |
| Ignores frontend/client consequences of server changes | Include the frontend/client action, or state that none was found |

## Mistakes to avoid

- Omitting old-client or old-server compatibility.
- Forgetting job retry, idempotency, and observability changes.

## Example

User: "Use `HEAD~5..HEAD` and make a backend handoff."

1. Run `git diff --stat HEAD~5..HEAD` and `git diff HEAD~5..HEAD`.
2. Extract the API contract, database migrations, service behavior, jobs, queues,
   and scheduled tasks.
3. Write `.handoffs/YYYY-MM-DD_HEAD-5-HEAD_backend.md`.
4. Include the remaining backend work, rollout and backward compatibility,
   verification evidence, and a Continuation Prompt.
