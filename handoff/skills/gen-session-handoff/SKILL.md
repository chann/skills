---
name: gen-session-handoff
description: Use when the current session must be handed to a fresh agent or another person because context is running out, the work spans sessions, or someone else will continue it, including "지금까지 작업 인수인계 문서로 만들어줘", "다음 세션에서 이어갈 수 있게 정리해줘", "컨텍스트 정리해서 넘겨줘", "hand this session off", "write a handoff so a new agent can continue", "summarize where we are so I can resume tomorrow", "/gen-session-handoff", or "$gen-session-handoff". Separates proven state from unproven, names the exact command behind each proven claim, and ends with a copyable resume prompt. For handing API changes to client or server developers use gen-frontend-handoff or gen-backend-handoff.
---

# Generate Session Handoff

Compact this session into a document a fresh agent can resume from without
guessing. The next reader has none of this conversation — only what the document
says and what the repository shows.

Two things separate a usable handoff from a transcript summary. First, **proven
and unproven are never mixed**: every claim that something works names the
command that proved it, and everything else is labeled unproven. Second, it
**references artifacts instead of restating them** — a plan, spec, diff, or issue
is named by path, not copied in. A handoff that duplicates a spec goes stale the
moment the spec changes, and the next agent cannot tell which copy is current.

## Output

```text
.handoffs/<YYYY-MM-DD>_<slug>_session.md
```

Derive `<slug>` from the goal, not from the date or the branch. Create
`.handoffs/` if needed.

## 1. Separate what is proven from what is not

This is the step that decides whether the handoff is worth writing. Go through
the session and sort every claim:

- **Proven** — a command was run and its result observed. Record the command.
- **Unproven** — written but never run, or run before the last change. Say so.

```markdown
### Proven
- Cursor pagination returns stable pages — `pnpm vitest run src/api/pagination.test.ts` (18 passed)
- Type surface is clean — `pnpm typecheck`

### Unproven
- Migration `0043_add_cursor_index` — written, never applied to any database
- Rate-limit interaction with pagination — not exercised by any test
```

"I implemented X" is not a proven claim. "X's tests pass under `<command>`" is.
The next agent will trust this list and build on it; a claim that was true two
edits ago and is now stale is the most expensive line you can write.

## 2. Say where the work is

Only what the next agent cannot read off the repository in a glance:

- **Goal** — one paragraph. What is being built and why, in the project's own
  vocabulary.
- **Branch and base** — the branch, what it forked from, whether it is pushed.
- **Committed** — commit subjects with hashes, or the range.
- **Uncommitted** — the paths still dirty and what is half-done in each.
- **Artifacts** — plan, spec, design doc, issue, review, diagnosis record, each
  by path or URL. Do not restate their contents.

Where the repository has a domain or architecture document, use its vocabulary so
the handoff and the codebase agree on names.

## 3. Record the decisions and the traps

The expensive knowledge in a session is not the code — it is what was ruled out
and why.

- **Decisions made** — the choice, and the reason. A decision without its reason
  gets re-litigated in the next session.
- **Decisions still open** — the question, the options, and who or what would
  settle it.
- **Ruled out** — approaches tried and abandoned, each with the reason. This is
  what stops the next agent walking into the same wall.
- **Traps** — the non-obvious things that cost time here: a test that only fails
  in CI, a generated file that must be rebuilt after a schema edit, a service
  that must be running, a flag that changes behavior silently.

## 4. Write the next actions as checkable steps

Ordered, each with a done-check. "Continue the API work" is not an action;
"add the `cursor` index migration, then confirm `pnpm test:db` passes" is.

```markdown
1. Apply migration `0043_add_cursor_index` → done when `pnpm test:db` passes
2. Wire the rate limiter into the paginated route → done when `pnpm vitest run src/api` is green
3. Update `docs/api.md` for the new cursor parameter → done when the example request matches the handler
```

Then add **Suggested skills** — which workflows from this catalog the next agent
should invoke, and for what. Name them exactly: `/bug-hunt` for the failing
integration test, `/code-review` before the merge, `/git-commit-push` to land it.

## 5. End with a resume prompt

A copyable block the next agent can be started with. It states the goal, points
at this document, and names the first action — nothing else. It is a pointer, not
a second copy of the handoff.

```text
Continue the cursor-pagination work on branch `feature/cursor-pagination`.
Read `.handoffs/2026-08-19_cursor-pagination_session.md` first — it has the proven
state, the open decisions, and the traps. Start with next action 1.
```

## 6. Redact before saving

Scrub tokens, keys, passwords, connection strings, customer identifiers, and
personal data out of every quoted command, log line, and error message. A handoff
is pasted into issues and chat more often than anyone plans for.

## Refusals

- Do not claim anything works without the command that proved it. Unproven work
  goes under **Unproven**.
- Do not copy a plan, spec, diff, or issue into the handoff. Reference it by path.
- Do not write next actions without a done-check.
- Do not summarize the conversation turn by turn. The next agent needs state and
  decisions, not history.
- Do not include a secret, token, or credential in a quoted command or log.
- Do not commit or push as part of writing the handoff.

## Integration

**Pairs with:** `work-summary` for a date-ranged report across sessions rather than
one session's state, `review-me` when the open decisions need closing before the
work continues, and `bug-hunt` when the handoff exists because a defect is still
unexplained.

**Use instead of:** `gen-frontend-handoff` and `gen-backend-handoff`, which hand
API and server changes to another team from a diff. This skill hands the *session*
to whoever continues the same work.
