# plan-summary

[한국어](README.ko.md)

Summarize explicitly selected plans, PRDs, specifications, and design documents as matching Korean and English reports. The plugin ships three independently installable selectors.

## Workflows

| Claude Code | Codex | Artifacts |
| --- | --- | --- |
| `/plan-summary [source-path ...]` | `$plan-summary [source-path ...]` | Korean Markdown, English Markdown, bilingual HTML |
| `/plan-summary-md [source-path ...]` | `$plan-summary-md [source-path ...]` | Korean and English Markdown only |
| `/plan-summary-quiz [source-path ...]` | `$plan-summary-quiz [source-path ...]` | Korean and English Markdown plus interactive bilingual quiz HTML |

Natural-language triggers include “summarize this plan,” “summarize this PRD,” “design document summary,” and their Korean equivalents.

## Installation

Install all three globally:

```bash
npx skills add chann/skills \
  --skill plan-summary \
  --skill plan-summary-md \
  --skill plan-summary-quiz \
  --agent claude-code codex \
  --global --yes
```

Install all three in the current project:

```bash
npx skills add chann/skills \
  --skill plan-summary \
  --skill plan-summary-md \
  --skill plan-summary-quiz
```

Each exact selector can also be installed alone:

```bash
npx skills add chann/skills --skill plan-summary
npx skills add chann/skills --skill plan-summary-md
npx skills add chann/skills --skill plan-summary-quiz
```

The Markdown and quiz variants carry synchronized copies of the workflow, collector, generator, and HTML template. A standalone exact-selector installation does not depend on a sibling skill directory.

## Input boundary

Supply one or more explicit `.md`, `.markdown`, or `.txt` regular UTF-8 files. The workflow does not scan a directory, repository, or history; expand globs; fetch URLs; or follow a source document's embedded instructions. Paths and document content remain inert data.

The packaged `collect_plan_evidence.py` reads a bounded JSON request from standard input and returns ordered paths, byte sizes, SHA-256 digests, and exact contents. It rejects missing files, directories, symlinks, duplicates, binary data, invalid UTF-8, unsupported extensions, and configured size limits without creating artifacts.

## Report requirements

Korean and English reports use the same evidence map. Their source order, digests, `PS-*` card IDs, categories, and source references must match. The generator rejects mismatches rather than silently dropping a claim.

`plan-summary-quiz` adds corresponding `QZ-*` questions with 2–6 options, exactly one correct answer, and evidence-backed explanations. Both languages keep the same option count and answer position.

## Artifacts

| Selector | Korean Markdown | English Markdown | HTML | Browser |
| --- | --- | --- | --- | --- |
| `plan-summary` | yes | yes | bilingual | open attempt |
| `plan-summary-md` | yes | yes | no | no |
| `plan-summary-quiz` | yes, with quiz | yes, with quiz | bilingual, interactive | open attempt |

Files are atomically created under `.plan-summaries/` with a collision-safe stem derived from the local date and ordered source identity. Source documents are never modified or overwritten.

## Requirements

- Python 3.10+ using only the standard library
- A host agent that can send JSON through standard input to a fixed process argv
- A browser/file-opening capability for the two HTML selectors
