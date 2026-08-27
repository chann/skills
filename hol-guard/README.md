# hol-guard

[한국어](README.ko.md) · [← back to main](../README.md)

Protect supported local coding-agent sessions with HOL Guard before risky tool
execution. The workflow detects the exact supported harness at runtime,
bootstraps Guard, proves the protected path, and fails closed instead of
suggesting an unprotected fallback.

## Installation

Global:

```bash
npx skills add -y -g chann/skills --skill hol-guard
```

Project-local:

```bash
npx skills add chann/skills --skill hol-guard
```

Install the HOL Guard runtime in an isolated Python application environment:

```bash
pipx install hol-guard
```

## Usage

| Claude Code | Codex | Action |
| --- | --- | --- |
| `/hol-guard` | `$hol-guard` | Protect the detected local coding-agent harness before risky tool execution |

The skill uses `hol-guard detect --json` as the source of truth for the exact
harness identifier, then follows `bootstrap → install → dry-run → doctor → run`.
A deny, review state, Guard error, timeout, or unavailable runtime stops the
workflow rather than authorizing an unprotected agent.

## Security boundary

HOL Guard protects supported local coding-agent harnesses. It does not replace
the target service's authentication, permissions, confirmations, review, or
server-side controls.

## License

MIT
