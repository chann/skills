# Periodic work summaries and natural generated docs — design

Date: 2026-08-09
Status: approved by the user's implementation request

## Goals

1. Extend `work-summary` with calendar-quarter and calendar-year ranges.
2. Save requested reports under predictable period-specific Markdown paths.
3. Make Korean prose from document-generating skills sound natural without
   making `human-friendly-writing` a required installation dependency.

## Scope

The natural-prose behavior applies to selectors whose primary output is a
reader-facing document in the repository's docs, handoff, or report families:

- `gen-docs`
- `plan-summary`, `plan-summary-md`, and `plan-summary-quiz`
- `gen-frontend-handoff` and `gen-backend-handoff`
- `work-summary`

Review and automation selectors are outside this change. Their primary job is
diagnosis or execution rather than general document generation.

## Work-summary range and storage contract

`this quarter` and `last quarter` use calendar quarters in the user's local
timezone: Q1 is January through March, Q2 April through June, Q3 July through
September, and Q4 October through December. `this year` and `last year` use
local calendar years. Current periods end at the current instant; previous
periods cover the complete calendar period.

When the user asks to save without providing an explicit path, classify by the
requested range syntax rather than guessing from coincidental start and end
dates:

| Request class | Default path |
| --- | --- |
| `today`, `yesterday`, `YYYY-MM-DD` | `.work-summaries/daily/<YYYY>/<YYYY-MM-DD>[-detailed].md` |
| `this week`, `last week` | `.work-summaries/weekly/<ISO-week-year>/<YYYY-Www>[-detailed].md` |
| `this month`, `last month` | `.work-summaries/monthly/<YYYY>/<YYYY-MM>[-detailed].md` |
| `this quarter`, `last quarter` | `.work-summaries/quarterly/<YYYY>/<YYYY-Qn>[-detailed].md` |
| `this year`, `last year` | `.work-summaries/yearly/<YYYY>[-detailed].md` |
| `YYYY-MM-DD..YYYY-MM-DD` | `.work-summaries/custom/<start>--<end>[-detailed].md` |

An explicit user-supplied output path wins over the default. The existing
privacy rules remain: no file unless requested, no automatic `.gitignore`
edit, and no staging or commit of generated reports.

## Optional natural-prose integration

Each in-scope selector remains self-contained. Its own workflow requires plain,
concrete Korean prose, avoids translation-like rhythm, AI filler, and internal
method vocabulary, and preserves facts, numbers, dates, identifiers, commands,
quotes, links, and parser-significant labels.

If the runtime already exposes `human-friendly-writing`, the selector may use
it as the final pass over newly authored Korean prose before artifact
generation. This is optional enhancement, not a required sub-skill:

- never install, fetch, or require it;
- never stop, warn, or reduce output when it is absent or unreadable;
- never pass source documents or preserved human prose through it;
- never allow it to change evidence, fixed templates, structural keys, or
  Korean/English alignment;
- always rerun the selector's normal validation after the pass.

Standalone installations therefore produce complete documents using only the
selected skill. Installing `human-friendly-writing` improves the final Korean
wording but does not unlock functionality.

## Alternatives considered

- A required `human-friendly-writing` dependency was rejected because exact
  selector installs must remain executable on their own.
- Copying the complete lexicon and style guide into every selector was rejected
  because it would create large, drifting duplicates.
- The chosen design duplicates only a small fallback writing contract and
  treats the dedicated skill as an optional final pass.

## Verification

- Add failing package-contract tests before editing skill behavior.
- Add `work-summary` eval scenarios for quarterly saving and missing optional
  writing support.
- Prove each exact selector still packages independently; existing generation
  tests must remain green without installing `human-friendly-writing`.
- Run the focused package tests, the full Python suite, website build, Markdown
  diff checks, and final Git upstream parity.
