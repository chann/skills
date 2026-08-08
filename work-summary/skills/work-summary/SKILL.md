---
name: work-summary
description: Use when the user wants coding-agent work history summarized or reported for today, yesterday, this or last week, month, quarter, or year, one date, or an explicit YYYY-MM-DD..YYYY-MM-DD span from local Claude Code, Codex, opencode, and agy session stores. Trigger on phrases like "오늘 작업 요약해줘", "이번 분기 작업 정리해줘", "올해 작업 상세 리포트", "what did I work on this quarter", "summarize my coding sessions", "/work-summary", or "$work-summary"; for one Git change use diff-summary instead.
---

# Work Summary

Generate a date-ranged Markdown report of coding-agent work from the session
history stores that agents such as Claude Code, Codex, opencode, and agy keep
on this machine. The outcome is an evidence-based digest of what was asked and
what was done — a compact summary by default, a detailed report on request.

## Session contract

- Stay read-only toward every history store: never modify, move, or delete
  session files or databases.
- Keep history content local: it may appear in the report and this
  conversation, but never send it to an external service. Never stage or
  commit a generated report.
- Report only recorded facts, with counts and quotes taken from the stores.
  A range without activity yields an honest "no recorded activity" report,
  never filler.
- Match the user's language for report prose; keep the template's English
  section headings as-is so the report shape stays checkable, keep dates in
  ISO form, and do all bucketing in the user's local timezone.

## 1. Resolve the range, depth, and scope

Parse the request; default to `today` at summary depth across all projects.

| Request | Range |
| --- | --- |
| `today` | local midnight to now |
| `yesterday` | the previous local calendar day |
| `this week` / `last week` | Monday-start weeks in local time |
| `this month` / `last month` | local calendar months |
| `this quarter` / `last quarter` | local calendar quarters: Q1 Jan–Mar, Q2 Apr–Jun, Q3 Jul–Sep, Q4 Oct–Dec |
| `this year` / `last year` | local calendar years |
| `YYYY-MM-DD` | that single local day |
| `YYYY-MM-DD..YYYY-MM-DD` | inclusive custom span |

Current week, month, quarter, and year ranges start at the local calendar
boundary and end now. Previous periods cover the complete local calendar
period. Weekly labels and directories use the ISO week-year that matches the
Monday-start week.

- Depth becomes detailed when the user asks for detail ("상세", "자세히",
  "detailed", "full report"); a detailed report adds the timeline and
  request-log sections.
- Scope narrows to one project when the user says so ("이 프로젝트만", "only
  this repo"); match it against each record's project or cwd field.

This step is complete when the range has concrete start and end instants in
the user's local timezone and the depth and scope are fixed.

## 2. Mine the agent history stores

Read [`references/agent-history-stores.md`](references/agent-history-stores.md)
completely before touching any store. Then, for every store present on this
machine:

1. Query the cheap prompt-level index first (`history.jsonl` files, SQLite
   session tables) for in-range prompts, sessions, and projects.
2. Open full session transcripts only for evidence the report needs —
   assistant outcomes, files touched, commands run — and only for in-range
   sessions. Discover those sessions from the union of index hits and each
   store's cheap pre-filter (such as transcript-file mtime); the index stays
   authoritative for session and prompt counts, transcripts for outcomes.
3. Filter by each record's own timestamp field. Epoch units and timezones
   differ per store (milliseconds vs seconds, UTC records vs local-time
   paths); the reference pins each one — normalize before comparing.
4. Drop non-work noise: Claude Code records flagged `isMeta` or
   `isSidechain`, Codex `developer`-role messages, and agy conversations
   flagged `is_internal`.

Silently skip stores that are absent. A store that exists but cannot be read
is listed as skipped in the report's Sources line instead of failing the run;
a store mined without in-range records is listed as "no in-range activity",
not as skipped.

This step is complete when every existing store is either mined for the range
or recorded as skipped with a reason.

## 3. Compose the Markdown report

Build the report in this shape; omit the two detailed-only sections at
summary depth:

```markdown
# Work Summary — <range label> (<start> ~ <end>, <UTC±HH:MM>)

- Sources: <stores with activity> (no in-range activity: <none | stores>; skipped: <none | store — reason>)
- Sessions: <n> · Prompts: <n> · Projects: <n>

## Overview

<3–6 sentences: the main threads of work and their outcomes>

## By project

### <project path>

- Asked: <condensed representative requests>
- Done: <outcomes evidenced by transcripts>
- Agents: <store names with session counts>

## By agent

| Agent | Sessions | Prompts | Projects |
| --- | --- | --- | --- |

## Timeline (detailed only)

### <YYYY-MM-DD>

- <HH:MM> · <agent> · <project> — <request → outcome>

## Requests log (detailed only)

| Time | Agent | Project | Request |
| --- | --- | --- | --- |
```

- Condense long prompts to their intent; never paraphrase into claims the
  records do not support.
- An empty range keeps the header and Sources lines accurate and states
  "no recorded activity in this range." under `## Overview`.

This step is complete when every section is backed by mined records and the
totals match the collected counts.

## 4. Deliver the report

Reply with the full Markdown report. Write a file only when the user asks for
one. If the user gives an explicit output path, use it. Otherwise create the
matching directory under the current project and classify the path from the
requested range syntax, not from coincidental start and end dates:

| Request class | Default path |
| --- | --- |
| `today`, `yesterday`, `YYYY-MM-DD` | `.work-summaries/daily/<YYYY>/<YYYY-MM-DD>[-detailed].md` |
| `this week`, `last week` | `.work-summaries/weekly/<ISO-week-year>/<YYYY-Www>[-detailed].md` |
| `this month`, `last month` | `.work-summaries/monthly/<YYYY>/<YYYY-MM>[-detailed].md` |
| `this quarter`, `last quarter` | `.work-summaries/quarterly/<YYYY>/<YYYY-Qn>[-detailed].md` |
| `this year`, `last year` | `.work-summaries/yearly/<YYYY>[-detailed].md` |
| `YYYY-MM-DD..YYYY-MM-DD` | `.work-summaries/custom/<start>--<end>[-detailed].md` |

Suggest — never apply — a `.work-summaries/` ignore entry in repositories
that track it. Never stage or commit a report; it can quote prompts from
unrelated private projects.
