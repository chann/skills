# handoff

[한국어](README.ko.md) · [← back to main](../README.md)

Handoff document generators for passing work between backend, frontend/client, and coding-agent sessions.

## What it does

- Creates evidence-based markdown handoffs from git diffs, commit ranges, branch comparisons, and current session context
- Provides `/gen-frontend-handoff` for backend API changes that frontend, mobile, SDK, or other clients need to consume
- Provides `/gen-backend-handoff` for server-side continuation work covering API contracts, database migrations, jobs, rollout, and verification
- Writes output to `.handoffs/`
- Preserves the user-specified scope, including branch comparisons such as `main...feature`
- Marks unverified tests, deploys, and runtime behavior as unverified instead of presenting assumptions as facts

## Installation

**Recommended (global):**

```bash
npx skills add -y -g chann/skills \
  --skill gen-frontend-handoff \
  --skill gen-backend-handoff
```

**Project-local:**

```bash
npx skills add chann/skills \
  --skill gen-frontend-handoff \
  --skill gen-backend-handoff
```

Use the actual skill names with `--skill`; this plugin packages both handoff generators together.

One-line selector form: `npx skills add chann/skills --skill gen-frontend-handoff --skill gen-backend-handoff`
Backend-only selector form: `npx skills add chann/skills --skill gen-backend-handoff`

## Usage

| Command | Skill | Output |
|---|---|---|
| `/gen-frontend-handoff` | `gen-frontend-handoff` | Frontend/client handoff at `.handoffs/<date>_<scope>_frontend.md` |
| `/gen-backend-handoff` | `gen-backend-handoff` | Backend/server handoff at `.handoffs/<date>_<scope>_backend.md` |

Examples:

```
> /gen-frontend-handoff main...feature-user-api
> /gen-backend-handoff HEAD~5..HEAD
> Create a FE handoff from the current backend API diff
> Create a backend handoff from the current Codex session context and git diff
```

## Scope rules

- No explicit scope: inspect unstaged and staged changes.
- Exact range: use the user-provided range first.
- Branch comparison: use the exact comparison, such as `main...feature`.
- Session context: use only context provided in the conversation or verified from files/commands.

## Requirements

- An agent platform that supports skills
- Git repository

## License

MIT
