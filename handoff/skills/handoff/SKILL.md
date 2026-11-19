---
name: handoff
description: Use when work must be handed to someone else, or to a fresh agent, as a document — API changes for client developers (frontend), server-side changes for backend developers (backend), or this session itself for whoever continues it (session). Including "프론트 인수인계 문서 만들어줘", "클라이언트 팀에 넘길 핸드오프", "백엔드에 넘길 문서", "지금까지 작업 인수인계 문서로 만들어줘", "다음 세션에서 이어갈 수 있게 정리해줘", "handoff for the client team", "backend handoff for HEAD~5..HEAD", "hand this session off", "write a handoff so a new agent can continue", "/handoff [frontend | backend | session] [scope]", or "$handoff". Writes an evidence-based document under `.handoffs/` that separates proven from unproven and ends with a continuation or resume prompt. To rebuild your own context from past work use recall; to explain what a change does use diff-summary.
---

# Handoff

Turn a diff or a session into a document the next person or agent can continue
from without guessing. The reader has none of this conversation — only the
document and the repository.

One rule outranks every template: **proven and unproven are never mixed.** A claim
that something works names the command that proved it; everything else is labeled
unproven.

## 1. Resolve the audience

Pick the audience in this order and stop at the first that decides it:

1. **The argument.** `/handoff frontend`, `backend`, or `session` (also `fe`, `be`).
2. **The request's wording.** "프론트 인수인계", "handoff for the client team",
   "백엔드에 넘길 문서", "다음 세션에서 이어갈 수 있게", "hand this session off".
3. **Inference.** A request to continue the work with no diff scope is `session`.
   A diff whose client-visible contract changed is `frontend`. Server-internal
   changes are `backend`.

State the resolved audience and the reason in the first line of the work, for
example `Audience: backend — the range changes a migration and a queue worker, no
response shape.` Never pick silently. When one diff needs both a frontend and a
backend document and the user asked for "the handoff", write both and say so.

Then load exactly the reference for each resolved audience, and no other:

| Audience | Load | Output |
|---|---|---|
| `frontend` | `references/frontend.md` | `.handoffs/<YYYY-MM-DD>_<scope>_frontend.md` |
| `backend` | `references/backend.md` | `.handoffs/<YYYY-MM-DD>_<scope>_backend.md` |
| `session` | `references/session.md` | `.handoffs/<YYYY-MM-DD>_<slug>_session.md` |

The reference holds that audience's required analysis and document template. The
rest of this file is what all three share.

## 2. Resolve the scope

Use the scope the user requested. Do not broaden it.

| User asks for | Use |
|---|---|
| Current changes / no explicit scope | `git diff --stat`, `git diff`, `git diff --staged --stat`, `git diff --staged` |
| Last commit | `git diff HEAD~1..HEAD` |
| Last N commits | `git diff HEAD~N..HEAD` |
| Exact range, including reversed ranges | The exact range first; if it looks wrong or empty, report that and suggest the likely intended range |
| Branch comparison such as `main...feature` | `git diff main...feature` exactly |
| PR number | `gh pr diff <number>` if `gh` is available |

Record the final diff command under **Evidence**. When the user supplied
`main...feature`, `HEAD~5..HEAD`, or another range, the document states that it
used the user-specified scope. For `session`, the scope is the conversation plus
the repository state, not a diff; text after the audience word is a note about
what the next session is for.

Output file names: `working` for unstaged and staged changes, the short SHA for a
single commit, a sanitized range or branch label for explicit scopes. Create
`.handoffs/` if needed. If the target file already exists, read it first and add a
numeric suffix instead of overwriting it.

## 3. Collect evidence

Gather only what the handoff needs:

```bash
git status --short
git log --oneline --decorate -n 10
git diff --stat [scope]
git diff [scope]
```

Also use conversation notes, Codex or Claude session summaries, pasted review
comments, test output, and deployment notes when the user provides them. Label
them "User-provided session context" unless a file or command verified them.

## 4. Keep proven apart from unproven

- **Proven (`VERIFIED`)** — a command ran after the last change and its result was
  observed. Record the command and the result.
- **Not proven (`NOT VERIFIED`)** — written but never run. Write "Not verified in
  this handoff."
- **`INCONCLUSIVE`** — ran before the last change, or the output did not settle
  it. Never count it as proven.

Do not claim unverified tests, deploys, or runtime behavior, and do not claim
anything works without the command that proved it. If no command output proves it,
it is not proven; unproven work goes under the unproven heading. A reading of the code that no run confirmed is
labeled `inferred`; a hunch is labeled `guess`.

## 5. Write the document

Write in the language of the request. For Korean, write reader-facing text as
plain, concrete Korean: direct sentences, no translation-like rhythm, no vague AI
filler, no internal method vocabulary. Preserve facts, numbers, dates, proper
nouns, code identifiers, commands, quotes, links, API fields, and evidence.

This skill is self-contained. When the runtime already exposes `unslop`, it may
run once, as an optional pass over only the newly written Korean draft before the
file is saved. Do not install, fetch, or require it; if it is absent or unreadable,
continue with the rules above. After an optional pass, validate the document
again. The pass may change wording only — never evidence, template headings, API
details, or the instructions in the Continuation Prompt or resume prompt.

## 6. Redact before saving

Never include secrets from `.env`, credentials, tokens, private keys, or
local-only config values. Scrub tokens, keys, passwords, connection strings,
customer identifiers, and personal data out of every quoted command, log line, and
error message. A handoff gets pasted into issues and chat more often than anyone
plans for. When asked to include a secret, refuse and say so in the reply rather than
dropping it silently.

## Baseline failures

| Failure observed without this skill | Required behavior |
|---|---|
| The agent reviews more than the requested range | Use the user-specified scope exactly, including `main...feature` |
| The agent says tests passed or a deploy happened without evidence | Do not claim unverified tests, deploys, or runtime behavior |
| The agent picks an audience without saying so | State the audience and the reason in the first line |
| The agent writes a generic summary | Follow the audience reference: its sections are the continuation surface |

## Common mistakes

- Mixing current working-tree changes with an explicit commit range.
- Copying session context as fact without labeling whether it was verified.
- Writing the frontend document from server internals, or the backend document
  from a client's point of view; each reference owns its own audience.
- Committing or pushing as part of writing the handoff. Do not commit or push; the
  only file written is the handoff.

## Not this skill

`recall` rebuilds your own context from past sessions and history. `diff-summary`
explains what a change does for a reader who only wants to understand it. This
skill produces a document that lets someone else continue.

**Reply:** the resolved audience and why, the path of each handoff written, the exact scope or diff command used, what is proven versus not verified, open questions, and any refusal (a secret left out, a scope not broadened, nothing committed).
