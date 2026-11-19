# Frontend handoff

Audience: frontend, mobile, SDK, or other client developers and coding agents.
Output: `.handoffs/<YYYY-MM-DD>_<scope>_frontend.md`.

**Core principle:** backend evidence in, client action out. The next developer
must be able to update API clients, types, UI rendering, and error handling
without guessing. If there is no client-visible change, say `client action 없음`.

## Client impact decision

Classify the change before writing any work item.

| Evidence | Required output |
|---|---|
| API route, method, request, response, status code, auth, permission, validation, pagination, sorting, filtering, or feature flag changed | Write concrete frontend/client actions |
| API response fields added | Include type updates, rendering impact, and loading, empty, and error states |
| API response fields removed, renamed, nullable, or semantically changed | Flag the compatibility risk and the required migration |
| Error shape, status code, or validation message changed | Include error handling and user-facing copy impact |
| DB-only, index-only, logging-only, refactor-only, or internal job change with no client-visible contract | State `client action 없음` and explain why, citing the evidence |
| Unsure whether a change is client-visible | Put it under Open Questions, not Required Client Work |

Do not invent a contract change to fill the template. A DB-only diff produces a
short document whose Client Impact section says `client action 없음`.

## Required analysis

For every client-visible change, extract:

- **API contract:** endpoint, method, request params and body, response body,
  status codes, headers, auth and permission requirements.
- **API response fields:** name, type, optionality or nullability, default,
  example value, added, removed, or renamed.
- **Type updates:** generated client, TypeScript types, schema files, SDK models,
  enums, validation schemas.
- **Rendering impact:** screens, components, table columns, cards, detail views,
  empty states, conditional rendering, feature flags.
- **Loading, empty, and error states:** pending behavior, no-data behavior,
  validation errors, permission errors, retry and cancel behavior.
- **Backward compatibility:** whether old clients keep working, and whether the
  client must tolerate both the old and new shapes during rollout.
- **Verification evidence:** tests, type checks, manual checks, or "Not verified".

Every claim about a request or response shape cites the diff hunk or file it came
from.

## Template

```markdown
# Frontend Handoff

**Date:** YYYY-MM-DD
**Scope:** [working tree | staged changes | HEAD~N..HEAD | main...feature | PR #N]
**Audience:** Frontend/client developer or coding agent

## Summary

- What changed:
- Client action:
- Compatibility risk:

## Evidence

- Diff command:
- Files inspected:
- User-provided session context:
- Tests/deploys verified:

## Client Impact

[Write `client action 없음` when the evidence is DB-only/internal-only.]

| Area | Impact | Required action |
|---|---|---|
| API client/types | ... | ... |
| Rendering | ... | ... |
| Loading/empty/error states | ... | ... |

## API Contract Changes

| Endpoint | Change | Client impact |
|---|---|---|

## Request Details

- Params:
- Body:
- Headers/auth:
- Validation:

## Response Details

- API response fields added:
- API response fields removed/renamed:
- Optional/nullability changes:
- Example response:

## Error And Permission Handling

- Status codes:
- Error shape:
- User-facing behavior:

## Rollout Notes

- Backend deployment dependency:
- Feature flags:
- Backward compatibility:
- Safe fallback:

## Frontend Implementation Checklist

- [ ] Update API client and generated types
- [ ] Update rendering logic
- [ ] Update loading, empty, and error states
- [ ] Add or update tests
- [ ] Verify against backend/API fixture

## Open Questions

- ...

## Continuation Prompt

Use the evidence above to update the frontend/client implementation for this API change. Preserve the stated scope, do not assume unverified backend behavior, and resolve the open questions before changing ambiguous flows.
```

## Audience-specific failures

| Failure observed without this reference | Required behavior |
|---|---|
| Summarizes backend code but misses type, rendering, and error work | Always extract type updates, rendering impact, and loading, empty, and error states |
| Invents client work for DB-only changes | State `client action 없음` for DB-only or internal-only diffs |

## Mistakes to avoid

- Treating added response fields as "no client work" without checking types and
  display surfaces.
- Turning every backend change into a frontend task.
- Omitting error shape and permission changes.

## Example

User: "Use `main...feature-user-metadata` and make a FE handoff."

1. Run `git diff --stat main...feature-user-metadata` and
   `git diff main...feature-user-metadata`.
2. Identify the added user response fields.
3. Write `.handoffs/YYYY-MM-DD_main-feature-user-metadata_frontend.md`.
4. Include type updates, rendering impact, loading/empty/error handling, the
   verified evidence, and a Continuation Prompt.
