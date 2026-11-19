# Session handoff

Audience: a fresh agent, or another person, who will continue this same work.
Output: `.handoffs/<YYYY-MM-DD>_<slug>_session.md`. Derive `<slug>` from the goal,
not from the date or the branch.

Two things separate a usable handoff from a transcript summary. First, proven and
unproven are never mixed. Second, it references artifacts instead of restating
them — a plan, spec, diff, or issue is named by path, not copied in. A handoff
that duplicates a spec goes stale the moment the spec changes, and the next agent
cannot tell which copy is current.

## 1. Separate what is proven from what is not

This step decides whether the handoff is worth writing. Go through the session and
sort every claim:

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
edits ago and is stale now is the most expensive line you can write.

## 2. Say where the work is

Only what the next agent cannot read off the repository at a glance:

- **Goal** — one paragraph: what is being built and why, in the project's own
  vocabulary.
- **Branch and base** — the branch, what it forked from, whether it is pushed.
- **Committed** — commit subjects with hashes, or the range.
- **Uncommitted** — the paths still dirty and what is half-done in each.
- **Artifacts** — plan, spec, design doc, issue, review, diagnosis record, each by
  path or URL. Do not restate their contents.

Where the repository has a domain or architecture document, use its vocabulary so
the handoff and the codebase agree on names.

## 3. Record the decisions and the traps

The expensive knowledge in a session is what was ruled out and why, not the code.

- **Decisions made** — the choice and the reason. A decision without its reason
  gets re-litigated in the next session.
- **Decisions still open** — the question, the options, and who or what would
  settle it.
- **Ruled out** — approaches tried and abandoned, each with the reason. This stops
  the next agent walking into the same wall.
- **Traps** — the non-obvious things that cost time here: a test that only fails
  in CI, a generated file that must be rebuilt after a schema edit, a service that
  must be running, a flag that changes behavior silently.

## 4. Write the next actions as checkable steps

Ordered, each with a done-check. "Continue the API work" is not an action; "add the
`cursor` index migration, then confirm `pnpm test:db` passes" is.

```markdown
1. Apply migration `0043_add_cursor_index` → done when `pnpm test:db` passes
2. Wire the rate limiter into the paginated route → done when `pnpm vitest run src/api` is green
3. Update `docs/api.md` for the new cursor parameter → done when the example request matches the handler
```

Then add **Suggested skills**: which workflows the next agent should use, and for
what, named exactly. When they are installed, `/bug-hunt` for a failing integration
test, `/interrogate` before the merge, `/git-commit push` to land it. Name only
workflows the repository's catalog actually has; if none is installed, omit the
list.

## 5. End with a resume prompt

A copyable block the next agent can be started with. It states the goal, points at
this document, and names the first action — nothing else. It is a pointer, not a
second copy of the handoff.

```text
Continue the cursor-pagination work on branch `feature/cursor-pagination`.
Read `.handoffs/2026-08-19_cursor-pagination_session.md` first — it has the proven
state, the open decisions, and the traps. Start with next action 1.
```

## Refusals

- Do not copy a plan, spec, diff, or issue into the handoff. Reference it by path.
- Do not write next actions without a done-check.
- Do not summarize the conversation turn by turn. The next agent needs state and
  decisions, not history.

## Related workflows

When installed: `review-me` closes open decisions before the work continues, and
`bug-hunt` fits when the handoff exists because a defect is still unexplained.
`recall` is for a date-ranged report across sessions rather than one session's
state. To hand an API or server change to another team from a diff, resolve the
audience to `frontend` or `backend` instead.
