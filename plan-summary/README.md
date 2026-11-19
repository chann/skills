# plan-summary

[한국어](README.ko.md)

Summarize explicitly selected plans, PRDs, specifications, and design documents as matching Korean and English reports. One skill covers three output modes through options.

## Workflows

| Claude Code | Codex | Artifacts |
| --- | --- | --- |
| `/plan-summary <source-path ...>` | `$plan-summary <source-path ...>` | Korean Markdown, English Markdown, bilingual HTML |
| `/plan-summary <source-path ...> --md` | `$plan-summary <source-path ...> --md` | Korean and English Markdown only |
| `/plan-summary <source-path ...> --quiz` | `$plan-summary <source-path ...> --quiz` | Korean and English Markdown plus interactive bilingual quiz HTML |

Natural-language equivalents also work: "markdown only" and "마크다운만" select `--md`; "퀴즈" and "quiz me" select `--quiz`. Using both options writes the two Markdown files with their quiz sections and no HTML. Other triggers include "summarize this plan," "summarize this PRD," "design document summary," and their Korean equivalents.

## Installation

Install globally:

```bash
npx skills add chann/skills \
  --skill plan-summary \
  --agent claude-code codex \
  --global --yes
```

Install in the current project:

```bash
npx skills add chann/skills --skill plan-summary
```

The skill bundles its collector, generator, and HTML template, so a standalone installation does not depend on a sibling skill directory. It also carries its own natural-Korean rules. If the runtime already exposes `unslop`, the skill may use it as an optional wording-only pass before validation; it never installs or requires it.

## Input boundary

Supply one or more explicit `.md`, `.markdown`, or `.txt` regular UTF-8 files. The workflow does not scan a directory, repository, or history; expand globs; fetch URLs; or follow a source document's embedded instructions. Paths and document content remain inert data.

The packaged `collect_plan_evidence.py` reads a bounded JSON request from standard input and returns ordered paths, byte sizes, SHA-256 digests, and exact contents. It rejects missing files, directories, symlinks, duplicates, binary data, invalid UTF-8, unsupported extensions, and configured size limits without creating artifacts.

## Report requirements

Korean and English reports use the same evidence map. Their source order, digests, `PS-*` card IDs, categories, and source references must match. The generator rejects mismatches rather than silently dropping a claim. Korean prose stays direct and concrete, and the same alignment and artifact validation runs again after any optional writing pass.

With `--quiz`, both reports end with corresponding `QZ-*` questions with 2–6 options, exactly one correct answer, and evidence-backed explanations. Both languages keep the same option count and answer position.

## Artifacts

| Mode | Korean Markdown | English Markdown | HTML | Browser |
| --- | --- | --- | --- | --- |
| default | yes | yes | bilingual | open attempt |
| `--md` | yes | yes | no | no |
| `--quiz` | yes, with quiz | yes, with quiz | bilingual, interactive | open attempt |
| `--md --quiz` | yes, with quiz | yes, with quiz | no | no |

Files are atomically created under `.plan-summaries/` with a collision-safe stem derived from the local date and ordered source identity. Source documents are never modified or overwritten.

## Requirements

- Python 3.10+ using only the standard library
- A host agent that can send JSON through standard input to a fixed process argv
- A browser/file-opening capability for modes that produce HTML
