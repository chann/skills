---
name: gen-frontend-handoff
description: Use when backend API changes, server behavior changes, git diffs, commit ranges, branch comparisons, or current session context need to be turned into a handoff for frontend, mobile, SDK, or other client developers and coding agents
---

# Frontend Handoff Generator

## Overview

Create evidence-based handoff documents for frontend and client implementers. The handoff must help the next developer update API clients, types, UI rendering, and error handling without guessing.

**Core principle:** backend evidence in, client action out. If there is no client-visible change, say `client action 없음`.

**Announce at start:** "I'm using the gen-frontend-handoff skill to create a frontend/client handoff."

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

Record the final diff command under **Evidence**. If the user supplied `main...feature`, `HEAD~5..HEAD`, or another range, the document must state that it used the user-specified scope.

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

## Client Impact Decision

Classify the change before writing detailed work items.

| Evidence | Required output |
|---|---|
| API route, method, request, response, status code, auth, permission, validation, pagination, sorting, filtering, or feature flag changed | Write concrete frontend/client actions |
| API response fields added | Include type updates, rendering impact, and loading, empty, and error states |
| API response fields removed, renamed, nullable, or semantically changed | Flag compatibility risk and required migration |
| Error shape, status code, or validation message changed | Include error handling and user-facing copy impact |
| DB-only, index-only, logging-only, refactor-only, or internal job change with no client-visible contract | State `client action 없음` and explain why |
| Unsure whether a change is client-visible | Put it under Open Questions, not Required Client Work |

## Required Analysis

For every client-visible change, extract:

- **API contract:** endpoint, method, request params/body, response body, status codes, headers, auth and permission requirements.
- **API response fields:** field name, type, optionality/nullability, default, example value, added/removed/renamed status.
- **Type updates:** generated client, TypeScript types, schema files, SDK models, enum updates, validation schemas.
- **Rendering impact:** screens, components, table columns, cards, detail views, empty states, conditional rendering, feature flags.
- **Loading, empty, and error states:** pending behavior, no-data behavior, validation errors, permission errors, retry/cancel behavior.
- **Backward compatibility:** whether old clients keep working, whether the client must tolerate both old and new shapes during rollout.
- **Verification evidence:** tests, type checks, manual checks, or "Not verified".

Do not claim unverified tests, deploys, or runtime behavior. If there is no command output proving it, write "Not verified in this handoff."

## Output

Write the handoff to:

```text
.handoffs/<YYYY-MM-DD>_<scope>_frontend.md
```

Use `working` for unstaged/staged changes, the short SHA for a single commit, or a sanitized range/branch label for explicit scopes. Create `.handoffs/` if needed.

## Document Template

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

## Baseline Failures

| Failure observed without this skill | Required behavior with this skill |
|---|---|
| Agent summarizes backend code but misses frontend type/rendering/error work | Always extract type updates, rendering impact, and loading, empty, and error states |
| Agent invents client work for DB-only changes | State `client action 없음` for DB-only/internal-only diffs |
| Agent reviews more than the requested branch or commit range | Use the user-specified scope exactly, including `main...feature` |
| Agent says tests passed or deploy happened without evidence | Do not claim unverified tests, deploys, or runtime behavior |

## Common Mistakes

- Treating added response fields as "no client work" without checking types and display surfaces.
- Turning every backend change into a frontend task.
- Omitting error shape and permission changes.
- Mixing current working-tree changes with an explicit commit range.
- Copying session context as fact without labeling whether it was verified.

## Example

User: "Use `main...feature-user-metadata` and make a FE handoff."

Expected behavior:

1. Run `git diff --stat main...feature-user-metadata` and `git diff main...feature-user-metadata`.
2. Identify added user response fields.
3. Write `.handoffs/YYYY-MM-DD_main-feature-user-metadata_frontend.md`.
4. Include API client type updates, rendering impact, loading/empty/error handling, verified evidence, and a Continuation Prompt.
