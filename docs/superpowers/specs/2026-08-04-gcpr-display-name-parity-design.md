# Design — `$gcpr` canonical display-name parity

## Context

The Codex alias package `gcpr` delegates to the canonical
`git-commit-push-realtime` skill, but its UI metadata currently displays the
abbreviation `GCPR`. The canonical skill and website use the full title
`Git Commit and Push Realtime`.

The alias must keep its short selector while presenting the canonical workflow
name consistently in Codex and on the public catalog.

## Goals

1. Display `Git Commit and Push Realtime` as the exact Codex title for `$gcpr`.
2. Preserve `$gcpr` as the alias package's invocation selector.
3. Make the alias-to-canonical-name relationship explicit on the website.
4. Keep one canonical workflow card and avoid inflating workflow counts.
5. Pin source, installed metadata, website, and deployed output to the same name.

## Non-goals

- Renaming the `gcpr` package or selector.
- Changing the canonical Git workflow or its safety rules.
- Adding a second website card for the alias.
- Making `$gcpr` and `$git-commit-push-realtime` visually indistinguishable in
  Codex beyond their shared title.
- Adding or changing other aliases.

## Codex metadata

Change only the alias package's user-facing title:

```yaml
interface:
  display_name: "Git Commit and Push Realtime"
  short_description: "Alias for verified realtime commit and push"
  default_prompt: "Use $gcpr to commit and push each verified outcome while working."
```

The `display_name` must be byte-for-byte equal to the canonical skill's
`display_name`. The alias-specific short description remains so the two Codex
entries are distinguishable, and `default_prompt` continues to invoke `$gcpr`
exactly.

The installed copy under `~/.agents/skills/gcpr/` must be refreshed from the
repository package and compared byte-for-byte. A newly opened Codex session may
be required before cached skill-list metadata refreshes.

## Website presentation

Keep `git-commit-push-realtime` as the single canonical workflow card. Its title
remains `Git Commit and Push Realtime`, and its aliases remain `/gcpr` and
`$gcpr`.

In the alias line, render the relationship explicitly:

```text
Aliases: /gcpr, $gcpr → Git Commit and Push Realtime
```

The localized alias label remains unchanged; selectors and the canonical title
remain invariant across locales. The same generic presentation applies to any
other canonical card with aliases, without creating duplicate data records.

## Validation

Follow test-driven development:

1. Add a failing package contract asserting that the alias `display_name`, the
   canonical `display_name`, and the website canonical title are identical.
2. Change the alias metadata and confirm the focused test turns green.
3. Validate every affected skill package and run the full Python suite.
4. Run the website catalog verifier and production build.
5. Refresh the installed Codex alias and compare its files with repository
   sources.
6. In a browser, search for `gcpr` and confirm the one canonical card shows the
   explicit alias-to-full-name mapping at desktop and mobile widths.
7. After deployment, repeat the live browser check and confirm local, upstream,
   and live `main` parity.

## Failure handling

- If the canonical and alias titles drift, the package contract fails.
- If website catalog identity or alias mapping drifts, catalog verification or
  the cross-surface contract fails.
- If the global install does not match repository sources, stop before claiming
  Codex activation.
- If push is rejected or upstream advances, stop without pulling, rebasing, or
  force-pushing.
- If Pages deployment fails, report the workflow failure and do not claim the
  website is live.
