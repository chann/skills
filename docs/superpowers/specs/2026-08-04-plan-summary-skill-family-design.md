# Design — Bilingual plan-summary skill family

## Context

The repository has a mature `diff-summary` family for explaining Git changes in
aligned Korean and English Markdown, self-contained bilingual HTML, and an
optional comprehension quiz. Plans, PRDs, design specifications, and similar
decision documents need the same reading experience without pretending that a
document is a Git diff.

The new family must summarize only user-selected source files, preserve source
ambiguity instead of filling gaps, and remain independently installable for
Claude Code and Codex.

## Goals

1. Add `plan-summary`, `plan-summary-md`, and `plan-summary-quiz` as three exact
   selectors.
2. Accept one or more explicitly selected Markdown or plain-text documents.
3. Produce aligned Korean and English summaries by default.
4. Provide a self-contained bilingual HTML report for the default and quiz
   selectors.
5. Turn source-backed concepts into an aligned interactive comprehension quiz.
6. Keep each selector independently installable with its complete runtime.
7. Publish all three workflows in repository documentation and the website.

## Non-goals

- Discovering documents automatically from a repository or directory.
- Summarizing PDFs, word-processing files, spreadsheets, or remote URLs.
- Editing, rewriting, approving, or executing the source plan.
- Reviewing a plan for defects or recommending implementation changes unless a
  later skill explicitly owns that workflow.
- Comparing document versions or Git revisions.
- Reusing Git-specific `diff-summary` metadata such as scope, command, or HEAD.

## Package architecture

Create a new top-level plugin:

```text
plan-summary/
├── .claude-plugin/plugin.json
├── README.md
├── README.ko.md
├── commands/
│   ├── plan-summary.md
│   ├── plan-summary-md.md
│   └── plan-summary-quiz.md
└── skills/
    ├── plan-summary/
    │   ├── SKILL.md
    │   ├── agents/openai.yaml
    │   ├── scripts/collect_plan_evidence.py
    │   ├── scripts/generate_plan_summary.py
    │   └── assets/summary-template.html
    ├── plan-summary-md/
    │   ├── SKILL.md
    │   ├── agents/openai.yaml
    │   ├── references/plan-summary-workflow.md
    │   ├── scripts/collect_plan_evidence.py
    │   ├── scripts/generate_plan_summary.py
    │   └── assets/summary-template.html
    └── plan-summary-quiz/
        ├── SKILL.md
        ├── agents/openai.yaml
        ├── references/plan-summary-workflow.md
        ├── scripts/collect_plan_evidence.py
        ├── scripts/generate_plan_summary.py
        └── assets/summary-template.html
```

`plan-summary` owns the authoritative workflow and runtime. The Markdown-only
and quiz variants contain synchronized copies so exact-selector installation is
executable without sibling skills. Tests enforce byte parity for the shared
workflow, collector, generator, and template.

The HTML presentation should inherit the established `diff-summary` visual and
accessibility language while using plan-specific labels, metadata, storage
keys, IDs, and output paths. It must not import files from another installed
skill at runtime.

## Selector behavior

| Selector | Output | Browser |
|---|---|---|
| `plan-summary` | Korean Markdown, English Markdown, bilingual HTML | Open HTML |
| `plan-summary-md` | Korean Markdown and English Markdown | Do not open |
| `plan-summary-quiz` | Korean and English Markdown with quizzes, bilingual interactive HTML | Open HTML |

Claude Code exposes `/plan-summary*`; Codex exposes `$plan-summary*`. Natural
language triggers cover plans, PRDs, product requirements, technical designs,
architecture proposals, implementation plans, specifications, and their Korean
equivalents.

## Exact input contract

The user must explicitly identify one or more source files. Accept `.md`,
`.markdown`, and `.txt` regular UTF-8 files. An attached document is valid when
the host exposes it as an explicit local file path.

No-argument invocation does not scan `docs/`, `plans/`, `specs/`, the working
directory, or repository history. It requests an explicit source instead.
Directories, glob patterns, remote URLs, and pasted shell expressions are not
expanded.

Invoke the packaged collector with a trusted absolute Python 3.10+ interpreter
in isolated mode and a fixed argv:

```text
/absolute/trusted/python3 -I <skill-path>/scripts/collect_plan_evidence.py
```

Send one JSON request through standard input:

```json
{"paths":["docs/plan.md","docs/design.md"]}
```

Paths are data, never shell syntax. The collector:

- resolves each explicitly supplied path without executing repository content;
- rejects duplicates, directories, symlinks, non-regular files, unsupported
  extensions, binary data, invalid UTF-8, and files outside configured size
  limits;
- caps the file count, per-file bytes, and aggregate bytes;
- returns the ordered source paths, sizes, SHA-256 digests, and exact UTF-8
  contents as JSON; and
- writes no artifacts.

Source contents, filenames, headings, links, and embedded prompts are untrusted
data. They cannot authorize commands, network access, additional file reads, or
scope expansion. A collector failure is fail-closed and produces no report.

## Evidence-first analysis

Summarize only claims supported by the collected documents. Preserve explicit
status, priority, ownership, deadlines, and decisions exactly. Label meaningful
inference as inference. Do not turn a missing statement into a negative claim.

When sources disagree, report the contradiction with both source locations.
When a required decision is unresolved, keep it under open questions rather
than choosing a value. Do not evaluate whether the plan is good or bad; route a
request for critique to a review workflow.

Use these dimensions only when supported:

- purpose and expected outcome;
- goals and success criteria;
- scope and non-goals;
- users, actors, and user flows;
- functional and non-functional requirements;
- decisions, constraints, and alternatives;
- architecture, components, interfaces, and data flow;
- milestones, sequencing, ownership, and dependencies;
- risks, assumptions, contradictions, and open questions; and
- acceptance criteria, rollout, verification, and rollback.

## Stable bilingual report contract

Generate one Korean source and one English source from the same analysis. Korean
is the default view. Both reports use the same `PS-*` IDs, order, categories,
source references, and claims. Translation must not add or remove information.

Top-level shape:

```markdown
# Plan Summary Report

**Date:** YYYY-MM-DD
**Sources:** `docs/plan.md`, `docs/design.md`
**Source Digests:** `<sha256>`, `<sha256>`
**Language:** ko

## Executive Summary

[Source-backed purpose, intended outcome, and most important constraint.]

## Summary

### Goals and Scope

#### [PS-001] Define the first release boundary

**Category:** Scope
**Sources:** `docs/plan.md#release-scope`

**Summary:** [What the source states.]

**Why it matters:** [Practical consequence supported by the source.]

**Source basis:** [Exact heading, requirement ID, or concise location evidence.]

## Plan Map

| Source | Section | Role | Key point |
|---|---|---|---|

## Risks, Contradictions, and Open Questions

- [Only source-backed or explicitly unresolved items.]
```

Parser-significant metadata keys and structural headings remain English in both
sources. Card IDs are unique and sequential from `PS-001`. Each card has one
category and a non-empty, ordered list of source references. Supported
categories are `Overview`, `Goal`, `Scope`, `Requirement`, `Decision`,
`Architecture`, `Flow`, `Milestone`, `Dependency`, `Risk`, `Acceptance`, and
`Open Question`.

Sections with no supported content are omitted. The report must not pad a fixed
card count or repeat the same claim in multiple cards.

## Output ownership

The generator owns filenames and atomic writes under `.plan-summaries/`:

```text
.plan-summaries/<date>_<source-tag>.md
.plan-summaries/<date>_<source-tag>.en.md
.plan-summaries/<date>_<source-tag>.html
```

The source tag uses readable source stems plus a digest of the exact ordered
source identity so different source sets cannot collide. The generator rejects
a symlinked or non-directory artifact parent, validates the complete bilingual
contract before writing, and never overwrites either source document.

The default selector uses bilingual JSON standard input and emits all three
artifacts. The Markdown-only selector validates the same contract but emits only
the two Markdown files and never attempts a browser open. Explicit
single-language mode is allowed only when the user requests it.

## Quiz contract

`plan-summary-quiz` appends `## Quiz` as the final section in both languages.
Use five medium-difficulty questions by default, reducing the count only when
the source cannot support five distinct concepts without padding.

Each question:

- uses a unique sequential `QZ-*` ID;
- contains 2 to 6 single-line options with exactly one `- [x]` answer;
- ends with one non-empty `**Explanation:**` tied to report evidence;
- tests goals, scope, decisions, flows, dependencies, risks, or acceptance
  criteria instead of line-count trivia; and
- has the same option count and correct-answer index in Korean and English.

The self-contained HTML turns options into accessible controls, reveals the
correct answer and explanation after one choice, disables the answered
question, supports printing as an answer key, and performs no network request.

## Documentation and website

Update root documentation, architecture, usage, package documentation, plugin
metadata, and installation examples for all three exact selectors. English and
Korean package documentation must describe the same capabilities and limits.

Add three canonical website cards in the docs category. Keep selectors, English
titles, examples, and search tags invariant while adding localized summary,
when-to-use, and result content for Korean, English, Japanese, and Chinese so
the existing locale contract remains complete.

The website workflow count increases by three. The separate `$gcpr` alias
remains represented by its canonical workflow and does not affect this count.

## Validation strategy

Use test-driven development and prove each behavior through a red-green cycle:

1. Package contracts for commands, skills, Codex metadata, plugin metadata,
   docs, website definitions, and exact-selector discovery.
2. Collector tests for ordered multiple inputs, digests, relative and absolute
   paths, duplicate files, missing files, unsupported extensions, directories,
   symlinks, binary data, invalid UTF-8, file-count limits, byte limits, and
   inert prompt-like content.
3. Parser and generator tests for metadata, sequential `PS-*` IDs, categories,
   source references, bilingual alignment, atomic output, collision-safe names,
   Markdown-only mode, and single-language mode.
4. Quiz tests for IDs, option count, one correct answer, visible-text
   normalization, explanations, bilingual answer alignment, accessible HTML,
   answer interaction, and print behavior.
5. Byte-parity checks across the three independently installable runtime copies.
6. Exact-selector forward-use installation and real artifact generation from a
   bounded fixture plan.
7. Full repository tests, per-skill validation, catalog verification, website
   type checking, and the production build.
8. Desktop and mobile browser checks for search, all three cards, selector copy,
   bilingual report switching, quiz interaction, reduced motion, dark mode,
   accessibility, and horizontal overflow.
9. GitHub Pages deployment, live health and browser checks, and local/upstream/
   live-main parity.

## Failure handling

- Invalid or unreadable source: report the exact rejected path and reason; do
  not read substitutes or create artifacts.
- Unsupported or excessive input: fail before partial content is returned.
- Misaligned Korean and English reports: reject generation and write nothing.
- Invalid quiz: identify the question and contract violation; do not drop the
  quiz silently.
- Browser-open failure: retain verified artifacts and report the warning.
- Existing `.plan-summaries/` not ignored: suggest a `.gitignore` entry but do
  not edit it automatically.
- Push rejection or upstream drift: stop without pull, merge, rebase, or force.
- Pages failure: report the failed workflow and do not claim the site is live.
