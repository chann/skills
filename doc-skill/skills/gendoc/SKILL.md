---
name: gendoc
description: Use when a software project needs README, README.ko, ARCHITECTURE, or USAGE documentation created, refreshed, reorganized, translated, or kept in sync without clobbering existing prose
---

# Documentation Generator

## Overview

Generate or update the four-doc project documentation set: `README.md`, `README.ko.md`, `ARCHITECTURE.md`, and `USAGE.md`.

**Core principle:** `README.md` is the front door. Keep it short, link to deeper docs, preserve human prose, and write only after the user has seen the diff.

**REQUIRED BACKGROUND: Use writing-skills** before editing this skill itself. New skill behavior must be tested with baseline failures first.

## Document Contract

| File | Role |
|---|---|
| `README.md` | English front door: pitch, highlights, primary install path, one quick start, links to deeper docs, license |
| `README.ko.md` | Faithful Korean mirror of `README.md`; preserve code, commands, flags, file names, and proper nouns verbatim |
| `ARCHITECTURE.md` | Components, responsibilities, data flow, directory map, design decisions |
| `USAGE.md` | Detailed install, command/API reference, configuration, examples, troubleshooting |

Omit sections with no evidence. Do not invent support matrices, flags, environment variables, or architecture claims.

## Workflow

1. Resolve the target root from arguments or cwd.
2. Detect which of the four docs exist and which are missing.
3. Confirm the target set with the user.
4. Run hybrid analysis:
   - Main agent reads manifests, top-level tree, existing docs, LICENSE, CI, and remote URL.
   - For larger projects, dispatch parallel Explore subagents for component map, entrypoints and flags, configuration, and examples.
   - For small projects, do the same probes inline.
5. Build one project model: name, pitch, install, quick start, components, data flow, directory map, command/API reference, configuration, examples, troubleshooting, license.
6. Render from templates in `templates/`.
7. Merge existing files in place.
8. Show per-file diffs and wait for confirmation.
9. Write only confirmed docs.

## Update-in-Place Rules

- Parse existing docs by `#` and `##` headings.
- Replace derivable sections: install, quick start, command reference, configuration, directory structure, version, badges.
- Preserve unknown custom prose verbatim.
- Preserve any section containing `<!-- doc-skill:keep -->`, even if it is normally derivable.
- Insert missing canonical sections in template order.
- Never delete a target document.
- Never modify files outside `README.md`, `README.ko.md`, `ARCHITECTURE.md`, and `USAGE.md`.

## Safety

- Show diffs before writing.
- Get explicit confirmation before writing.
- Never embed secret values found in `.env`, credentials, keys, tokens, or local config.
- Mention uncertain findings as uncertain instead of filling gaps with guesses.
- Do not run the target project unless the user asks; static analysis is enough for v1.

## Baseline Failures

These are the baseline failures this skill exists to prevent:

| Failure observed without the skill | Required behavior with this skill |
|---|---|
| README becomes a dumping ground for install, usage, architecture, and troubleshooting | Keep README as the front door and move depth to `USAGE.md` / `ARCHITECTURE.md` |
| Existing hand-written sections are overwritten | Merge by heading and preserve unknown custom prose |
| Korean README is skipped or drifts from English | Render `README.ko.md` as a faithful mirror whenever `README.md` changes |
| Agent writes files immediately | Show per-file diff and wait for confirmation |
| Agent writes extra docs or edits unrelated files | Restrict writes to the four target docs |

## Common Mistakes

- Duplicating the same usage reference in README and `USAGE.md`.
- Translating commands or flags in `README.ko.md`.
- Treating an absent config file as proof there is no configuration surface.
- Claiming every dependency is part of the public architecture.
- Skipping the diff because the generated docs look obvious.
