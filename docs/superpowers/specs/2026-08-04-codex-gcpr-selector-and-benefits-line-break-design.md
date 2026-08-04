# Design — Codex `$gcpr` selector and Korean benefits line break

Date: 2026-08-04
Status: accepted for implementation planning

## Context

The repository already exposes `/gcpr` as a Claude Code command alias for
`/git-commit-push-realtime`. The canonical skill description also mentions
`$gcpr`, but Codex 0.146.0 discovers selectors from actual skill packages. The
current package scan therefore exposes `$git-commit-push-realtime` but not a
selectable `$gcpr` entry.

This design supersedes only the "Alias skill directory — rejected" decision in
`docs/superpowers/specs/2026-07-28-gcpr-command-alias-design.md`. The existing
canonical workflow, Claude Code command alias, and safety contracts remain in
place.

The Korean benefits heading also currently stores two lines and renders exactly
two array entries. It needs the following fixed three-line composition:

```text
반복할수록,
덜 설명하고
더 선명하게.
```

## Goals

1. Make `$gcpr` an actual Codex selector after installing the alias package.
2. Keep `git-commit-push-realtime` as the only source of workflow and safety
   rules.
3. Preserve the existing `/gcpr` behavior in Claude Code.
4. Render the requested Korean benefits heading as three explicit lines without
   changing the other locales.

## Non-goals

- Renaming or removing `$git-commit-push-realtime`.
- Adding a Codex `$gcr` selector in the same change.
- Duplicating the full realtime workflow under the alias.
- Publishing, deploying, or releasing the repository as part of implementation
  unless requested separately.

## Codex alias design

Add `git-skill/skills/gcpr/` as a real, minimal skill package:

- `SKILL.md` declares `name: gcpr`, advertises `/gcpr` and `$gcpr`, and requires
  the agent to load and follow the installed `git-commit-push-realtime` skill in
  full before taking any Git action.
- `agents/openai.yaml` publishes the Codex display name, short description, and
  a default prompt that invokes `$gcpr` exactly.
- If the canonical skill cannot be found, the wrapper must stop before any Git
  mutation and report the exact canonical skill that also needs installation.

The alias contains no checkpoint, staging, push, drift, or force-push policy of
its own. This avoids two independently maintained safety contracts. The
canonical long selector remains independently installable and discoverable.

The existing `git-skill/commands/gcpr.md` remains the Claude Code wrapper. Its
body stays byte-identical to the canonical Claude Code command.

## Catalog and documentation model

`gcpr` is an installable selector alias, not a second workflow. Documentation
and the website should distinguish canonical workflows from packaged selectors:

- The canonical catalog continues to show one Git Commit and Push Realtime card.
- That card lists both `/gcpr` and `$gcpr` as aliases.
- Repository/package documentation lists `$gcpr` next to the long Codex
  selector.
- Package verification accepts `gcpr` as an alias represented by the canonical
  catalog entry instead of requiring a duplicate website card.
- Counts and wording identify 20 canonical workflows and 21 installable Codex
  selector packages, rather than describing the alias as a new workflow.

The normal all-skills installation installs both the alias and canonical skill.
An update only refreshes selectors that are already installed, so existing
users must add `gcpr` once. A selective installation must include `gcpr`,
`git-commit-push-realtime`, `git-commit`, and `git-commit-push`; documentation
will show that dependency set explicitly.

## Korean heading design

Change the Korean `benefits.title` value from two entries to three:

1. `반복할수록,`
2. `덜 설명하고`
3. `더 선명하게.`

Replace the benefits heading's fixed `[0]`/`[1]` rendering with an array-driven
line renderer. Each localized array item becomes one explicit visual line. The
English, Japanese, and Chinese content arrays remain unchanged and therefore
retain their current line compositions.

The heading remains a single semantic `h2`; line wrappers and breaks are
presentational only. Existing responsive typography and `word-break: keep-all`
behavior remain in effect.

## Failure behavior

- `$gcpr` without the canonical skill: stop, name the missing dependency, and do
  not inspect, stage, commit, or push a repository.
- Invalid or missing alias metadata: package tests fail before publication.
- Catalog alias not mapped to a canonical workflow: catalog verification fails.
- Missing or reordered Korean heading lines: landing-message verification fails.

## Verification

### Package and selector

- Unit tests assert the `gcpr` skill package and Codex metadata exist.
- Tests assert the wrapper delegates to `git-commit-push-realtime` and contains
  no copied Git workflow.
- `npx skills add . --list --full-depth` lists `gcpr`.
- A temporary Codex-targeted installation contains both `gcpr/SKILL.md` and the
  canonical skill.
- After local activation, a fresh Codex session exposes `$gcpr`; session reload
  is reported as a runtime boundary.

### Website

- The landing-message contract pins the three Korean lines, and locale
  verification permits the benefits title to have a locale-specific line count.
- Catalog verification recognizes `$gcpr` as an alias of the canonical card.
- TypeScript checks and the production website build pass.
- Browser QA checks the benefits heading at narrow and wide widths and confirms
  the other locales are unchanged.

### Repository

- `python3 -m pytest tests`
- `npm --prefix website run build`
- `git diff --check`
