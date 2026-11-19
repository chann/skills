# handoff

[한국어](README.ko.md) · [← back to main](../README.md)

One handoff skill with an audience argument: pass work to client developers, to server developers, or to whoever continues this session.

## What it does

- Creates evidence-based markdown handoffs from git diffs, commit ranges, branch comparisons, and current session context
- `frontend` covers backend API changes that frontend, mobile, SDK, or other clients need to consume, and says `client action 없음` when nothing client-visible changed
- `backend` covers server-side continuation work: API contracts, database migrations, jobs, rollout, and verification
- `session` hands the current session to a fresh agent, separating proven state from unproven and ending with a copyable resume prompt
- Resolves the audience from the argument, then the request's wording, then the diff, and states which it chose and why in the first line
- Writes output to `.handoffs/`
- Preserves the user-specified scope, including branch comparisons such as `main...feature`
- Marks unverified tests, deploys, and runtime behavior as unverified instead of presenting assumptions as facts
- Redacts secrets from quoted commands and logs, and never commits or pushes
- Writes Korean handoffs in plain prose and optionally uses `unslop` when the runtime already provides it

## Installation

**Recommended (global):**

```bash
npx skills add -y -g chann/skills --skill handoff
```

**Project-local:**

```bash
npx skills add chann/skills --skill handoff
```

One-line selector form: `npx skills add chann/skills --skill handoff`

The skill works by itself. It does not install or require `unslop`; its built-in writing rules remain the fallback when that optional skill is unavailable.

## Usage

| Claude Code | Codex | Output |
|---|---|---|
| `/handoff frontend [scope]` | `$handoff frontend [scope]` | Frontend/client handoff at `.handoffs/<date>_<scope>_frontend.md` |
| `/handoff backend [scope]` | `$handoff backend [scope]` | Backend/server handoff at `.handoffs/<date>_<scope>_backend.md` |
| `/handoff session [note]` | `$handoff session [note]` | Session handoff at `.handoffs/<date>_<slug>_session.md` |
| `/handoff [scope]` | `$handoff [scope]` | Audience resolved from the wording or the diff; both documents when a diff needs both |

Examples:

```
> /handoff frontend main...feature-user-api
> /handoff backend HEAD~5..HEAD
> /handoff session
> Create a FE handoff from the current backend API diff
> Write a handoff so a new agent can continue this work tomorrow
```

### Migrating from the three old skills

| Old | New |
|---|---|
| `/gen-frontend-handoff [scope]` | `/handoff frontend [scope]` |
| `/gen-backend-handoff [scope]` | `/handoff backend [scope]` |
| `/gen-session-handoff [note]` | `/handoff session [note]` |
| `$gen-frontend-handoff`, `$gen-backend-handoff`, `$gen-session-handoff` | `$handoff frontend`, `$handoff backend`, `$handoff session` |

Output paths and file names are unchanged.

## Scope rules

- No explicit scope: inspect unstaged and staged changes.
- Exact range: use the user-provided range first.
- Branch comparison: use the exact comparison, such as `main...feature`.
- Session context: use only context provided in the conversation or verified from files and commands.
- `session` hands off the session itself, so its scope is the conversation plus the repository state rather than a diff. Every claim that something works names the command that proved it; everything else is recorded as unproven.

## Requirements

- An agent platform that supports skills
- Git repository

## License

MIT
