# Completion Audit

The completion audit is the gate between "the orchestrator thinks it's done" and "the project actually meets its acceptance criteria." It is the final defense against the most common autonomous-agent failure: declaring victory on uncovered work.

The audit is **manual** — the orchestrator (you) writes it. The plugin only enforces the existence of `.agent/audit.md` and disarms the Stop hook once `/long-task complete` runs. The honesty of the audit is on you.

## When to run it

`/long-task complete` is what kicks off the audit. Before running it, you should believe — with evidence — that the project meets `.agent/goal.md`'s acceptance criteria. If you are not sure, do not run `/long-task complete` yet. Keep working.

## Audit procedure

1. **Restate acceptance criteria.** Open `.agent/goal.md`. Copy each acceptance criterion verbatim into `.agent/audit.md`. Do not paraphrase — verbatim, so future readers can cross-check.

2. **Map each criterion to concrete evidence.** For every criterion, list:
   - Files that exist (with paths)
   - Functions / endpoints / commands that work (with the command output)
   - Tests that pass (test name, file, and `passed` count)
   - Behavior verified by running the system (transcript or screenshot reference)

   Evidence is concrete. "Implemented" is not evidence. "src/auth/login.ts exports `login()`, test `auth.test.ts` runs 12 cases all passing" is evidence.

3. **Flag missing or weak evidence.** For every criterion without concrete evidence, mark it as **deferred** and explain why. Examples:
   - "Could not verify because external API key was unavailable — deferred to user with note."
   - "Edge case X tested only by unit test, not integration — listed under Known Issues."

4. **Distinguish deferred vs. broken.** A deferred criterion is one you consciously chose not to deliver. A broken criterion is one you tried to deliver but it doesn't work. Be honest about which is which.

5. **Summarize the build.** For each milestone, write 2-4 lines: what was delivered, how many review iterations it went through, and what (if anything) was deferred from that milestone.

6. **Final verdict.** Three checkboxes at the end of `.agent/audit.md`:
   - [ ] Every acceptance criterion has evidence above or is explicitly listed as deferred.
   - [ ] Every deferred item has a one-line rationale and a recommended follow-up.
   - [ ] No silent gaps — anything skipped is mentioned.

   If you can't check all three, the audit isn't done. Go back to work.

## What "evidence" looks like

| Bad | Good |
|---|---|
| "Login works" | "POST /auth/login returns 200 with valid creds; test `tests/auth/login.test.ts:12` covers happy path and 4 error cases, all green" |
| "API has rate limiting" | "Express middleware `src/middleware/rateLimit.ts:18` enforces 100 req/min per IP; integration test `tests/rate-limit.test.ts` proves 101st request gets 429" |
| "Frontend looks good" | "Visited `/dashboard` in headless Chrome, screenshot at `.agent/screenshots/dashboard.png`; matches Figma spec for layout, copy, and color tokens" |
| "Migration works" | "Ran `npm run db:migrate` against fresh DB → schema matches `schema.sql`; ran on staging clone → 0 errors, 0 row-loss; rollback `db:rollback` reverts cleanly" |

## What to write in the final report to the user

After the audit passes, summarize for the user in plain language:

- **What was built**, milestone-by-milestone (1-2 sentences each)
- **What was deferred**, with the rationale and the recommended follow-up step
- **Known issues**, ranked by severity, with workarounds where applicable
- **Where the audit lives** (`.agent/audit.md`) and which acceptance criteria it covers
- **How to resume** if the user wants to address deferred items (`/long-task clear`, then restart for a focused follow-up; or just open `.agent/audit.md` and pick an item)

The audit is for the user. The user trusts you when the audit is honest. Once.
