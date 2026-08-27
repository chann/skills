---
name: hol-guard
description: Use when the user asks to protect, secure, or guard a supported local coding-agent session before file edits, shell commands, package installation, credential use, or other risky tool execution, including "protect this agent with HOL Guard". Use `/hol-guard` in Claude Code or `$hol-guard` in Codex. For read-only code review use code-review instead.
---

# HOL Guard

Put HOL Guard on the local coding-agent execution path before risky tool use.
Treat Guard as the runtime boundary for supported local harnesses, not as a
prompt-only checklist and not as a substitute for the target tool's own auth,
permissions, confirmations, or review controls.

## 1. Verify the CLI and inspect current state

Probe the real CLI instead of relying on a POSIX-only executable lookup:

```bash
hol-guard --version
hol-guard status
hol-guard detect --json
```

If the CLI is unavailable, install the maintained package in an isolated app
environment:

```bash
pipx install hol-guard
```

Then rerun `hol-guard --version`, `hol-guard status`, and
`hol-guard detect --json`.

Use only the exact harness identifier returned by `hol-guard detect --json`.
Do not maintain or guess a parallel list of supported products.

## 2. Bootstrap and install the detected harness

For the detected `<harness>`:

```bash
hol-guard bootstrap
hol-guard install <harness>
```

Stop if either command fails. Do not claim the session is protected merely
because the package installed.

## 3. Prove the protected launch path

Run the protected harness in dry-run mode, then check the harness-specific
health evidence:

```bash
hol-guard run <harness> --dry-run
hol-guard doctor <harness> --json
```

Require both commands to succeed before mutation-bearing work. If dry-run or
doctor reports an error, unexpected mutation, missing protection, timeout, or
unavailable runtime, stop and report the exact evidence.

## 4. Launch through Guard

Only after the checks above succeed:

```bash
hol-guard run <harness>
```

Perform the user's state-changing coding-agent work from that protected session.
Keep repository instructions, target-service authentication, native permission
checks, confirmations, and human-review requirements in force.

## 5. Handle blocks and review states

Never turn a Guard decision into an unprotected fallback. Inspect the request
through Guard instead:

```bash
hol-guard approvals
hol-guard approvals open
hol-guard receipts
hol-guard diff <harness>
```

A deny, review-required state, Guard error, timeout, or unavailable runtime is a
stop condition until the Guard-owned path resolves it.

## 6. Diagnose protection drift

If the protected harness later appears unhealthy, stop further mutation and
re-check:

```bash
hol-guard status
hol-guard detect --json
hol-guard doctor <harness> --json
hol-guard settings show
```

Resume a protection claim only when current Guard output proves the local
harness is configured successfully.

## Boundary

This skill covers HOL Guard's supported **local coding-agent harness** boundary.
It does not claim that HOL Guard runs inside a third-party cloud service,
server-side runtime, or unrelated CLI. It is additive to the controls of the
system the agent is operating.

HOL Guard source: https://github.com/hashgraph-online/hol-guard
