# Code Review UI and Writing Design

**Date:** 2026-07-14
**Status:** Approved for implementation

## Problem

The `code-review` plugin has three tracked HTML report families:

1. `diff-summary`, rendered from `skills/diff-summary/assets/summary-template.html`
2. `diff-viewer`, rendered from `skills/diff-viewer/assets/diff-template.html`
3. `code-review-html`, rendered through the shared `skills/code-review/assets/report-template.html`

They belong to one plugin but do not look like one product. `diff-viewer` and
`code-review-html` already use similar neutral colors, compact controls, and a
sidebar layout. `diff-summary` instead uses a separate paper-and-atlas visual
concept, decorative grid texture, oversized typography, and ornamental labels.

The review prompts have a second consistency problem. They ask for concise,
evidence-based writing while also requiring canned announcements, a fixed
quality summary, positive observations, file-by-file repetition, and a second
conversation recap. Those requirements encourage filler and AI-like report
padding even when the diff does not support the sections.

## Goals

- Make all three HTML report families use one shadcn-inspired visual language.
- Preserve the information architecture and interactions specific to each report.
- Keep every generated HTML document browser-readable without a build step.
- Keep each installable skill independent; a single-skill installation must not
  require a sibling skill's runtime files.
- Remove decorative `diff-summary` copy and presentation that does not convey data.
- Make review prose direct, specific, proportionate to the evidence, and useful
  to an engineer deciding what to change.
- Encode the UI and writing contracts in automated tests.
- Keep tracked package sources and installed local mirrors aligned after changes.

## Non-goals

- Do not convert the templates to React or add the shadcn/ui package.
- Do not add a frontend build, package-manager, web-server, or network requirement.
- Do not merge the three generators into one renderer.
- Do not remove report-specific behavior such as split diffs, bilingual review
  switching, summary-card comments, or per-finding actions.
- Do not redesign Markdown parsing, evidence collection, diff semantics, comment
  persistence, or artifact naming unless a style change exposes a direct defect.
- Do not force the three reports to have identical content or page structure.

## Chosen Approach

Use an independent-template, shared-design-contract approach.

Each template keeps its own markup, JavaScript, and packaging boundary. The three
templates duplicate a small, explicit set of semantic tokens and component rules
so the emitted HTML stays self-contained and each skill remains independently
installable. Tests compare the contract across templates to prevent drift.

This is preferable to a shared CSS asset because `diff-summary` and `diff-viewer`
must work when installed without the main `code-review` skill. It is preferable
to a single renderer because the three reports render different document models
and have materially different interactions.

## Shared Visual Contract

### Semantic tokens

Every template will expose the same core token names for light and dark themes:

- `--background` and `--foreground`
- `--card` and `--card-foreground`
- `--popover` and `--popover-foreground`
- `--muted` and `--muted-foreground`
- `--primary` and `--primary-foreground`
- `--secondary` and `--secondary-foreground`
- `--accent` and `--accent-foreground`
- `--destructive` and `--destructive-foreground`
- `--border`, `--input`, and `--ring`
- `--radius`, `--font-sans`, and `--font-mono`

Report-specific status colors remain allowed for review severity and diff
addition/deletion states, but they must sit on top of the shared neutral system.
Raw color values must not be used to create a competing page-level theme.

### Components

The templates will share the same visual rules for these primitives even though
the class names may remain renderer-specific where changing them would create
unnecessary risk:

- Sidebar shell, header, navigation item, collapse control, and resizer
- Primary, secondary, outline, ghost, and destructive buttons
- Select controls and segmented button groups
- Cards and card headers
- Badges for severity, category, impact, and metrics
- Tables, inline code, code blocks, and empty states
- Comment editors, action toolbars, and status notifications
- Focus-visible ring, disabled state, hover state, and selected state

Controls use compact, consistent heights and spacing. Rounded corners are modest
and systematic rather than decorative. Accent-bordered findings remain flat so
the left severity marker does not combine with an exaggerated rounded card.
Shadows are limited to overlays or a subtle one-pixel card lift.

### Layout and responsive behavior

Desktop reports retain their collapsible and resizable sidebar. Main content uses
a consistent maximum width, page padding, section rhythm, and sticky-control
treatment. Mobile layouts collapse to one column without horizontal page
overflow. Code and diff content may scroll within its own region.

All existing keyboard and screen-reader hooks remain available. Focus styles use
the shared ring token. Print styles continue to hide controls, expand collapsed
content, and use readable neutral surfaces.

## Report-specific UI Changes

### `diff-summary`

`diff-summary` receives the largest visual change.

- Replace the paper, ink, cobalt, and amber palette with the shared tokens.
- Remove the grid texture, registration marks, atlas decoration, oversized report
  title, and other editorial-poster styling.
- Replace phrases such as `Engineering change atlas`, `Offline review plate`,
  `Atlas index`, and `Portable review artifact` with plain product labels.
- Recompose the summary header, metrics, cards, files, comments, and footer from
  the shared visual primitives.
- Keep theme persistence, sidebar resizing, section navigation, per-card copy,
  comment editing, feedback export, storage fallback, responsive behavior, and
  print behavior.

### `diff-viewer`

- Map existing page tokens to the shared semantic names.
- Align buttons, selects, metrics, sidebar navigation, comments, and top controls
  with the shared component rules.
- Preserve unified/split rendering, word-level highlights, line selection,
  comment threads, code schemes, and diff-specific colors.

### `code-review-html`

- Apply the same token and component contract as `diff-viewer`.
- Preserve bilingual switching, severity styling, syntax schemes, finding
  comments, feedback copy, and report copy.
- Keep finding actions after the finding content.
- Preserve flat severity-accent findings instead of adding decorative rounding.

## Anti-slop Writing Contract

The main `code-review` skill is the authoritative writing contract. The Markdown
and HTML wrappers reference that contract instead of restating a weaker summary.
`diff-summary` receives a parallel evidence-summary contract. The raw
`diff-viewer` remains analytical-prose-free.

### Required behavior

- Start with the finding or verified result; do not add a canned skill
  announcement or generic review preface.
- Use a finding title that states the concrete failure or risk.
- Cite the changed path and line range before making a claim.
- Write the body in this order: observed behavior, practical consequence, and
  smallest justified correction.
- Distinguish verified facts from inferences and open questions.
- Use the user's language while preserving code, identifiers, paths, IDs, and
  severity labels.
- Keep output proportional to the diff. A one-line defect may have a one-line
  explanation.
- When there are no actionable findings, state that directly and list only
  material residual risks or verification gaps.

### Prohibited behavior

- No generic praise, congratulatory language, or claims that code is "solid",
  "robust", "clean", or "well-structured" without a decision-relevant reason.
- No throat-clearing such as "Overall", "In summary", "It's worth noting",
  or "This change improves" unless the phrase adds specific information.
- No restatement of code in prose when the consequence is the useful part.
- No repeated conclusion across an executive summary, finding body, file table,
  and conversation handoff.
- No mandatory `Positive Observations` section.
- No manufactured INFO findings or questions used to make a report look complete.
- No fixed number of findings, bullets, sentences, or "top 1-3" recap.
- No vague recommendation such as "consider adding validation" without a path,
  condition, and expected behavior.

### Conditional report sections

The report always includes metadata and an actionable findings area. Other
sections appear only when they carry distinct information:

- `Decision Summary`: only for cross-cutting risk that is not already obvious
  from the first finding and metrics.
- `Positive Observations`: only for a specific pattern that materially reduces
  risk or review effort; never required.
- `Open Questions`: only for a real uncertainty that blocks severity or action.
- `File Summary`: only when it helps navigate a multi-file review and does not
  repeat each finding.

The conversation handoff reports artifact paths and verification facts. It does
not reproduce the report's findings unless the user needs an urgent finding
without opening the artifact.

## Tests

Implementation follows test-driven development.

1. Add a shared style-contract test that reads all three tracked templates and
   initially fails because `diff-summary` lacks the semantic tokens and contains
   atlas decoration.
2. Add template-specific assertions for shared control states, responsive hooks,
   focus behavior, and removal of ornamental copy.
3. Keep renderer behavior tests green while restyling templates.
4. Add prompt-contract tests that initially fail on mandatory announcements,
   mandatory positive observations, repeated recap requirements, and missing
   evidence-first constraints.
5. Add wrapper tests proving `code-review-md` and `code-review-html` inherit the
   authoritative writing contract.
6. Generate representative reports for all three families and inspect them at
   desktop and narrow widths in light and dark themes.
7. Run targeted suites, the full test suite, skill validation, package discovery,
   and `git diff --check` before completion.

## Packaging and Mirrors

Tracked files under `code-review/skills/` are authoritative. Repository-local
`.agents/skills/` copies and the user-level installed copies under
`/Users/channprj/.agents/skills/` are runtime mirrors, not additional source
files. After each logical implementation phase, sync affected installed copies
from the verified tracked files and compare them byte-for-byte.

The repository-local mirror currently lacks `diff-summary`; installation or
explicit mirroring must restore it before the final live-surface verification.

## Commit and Push Boundaries

Use Conventional Commits and push after each successful commit:

1. `docs(code-review): define unified report design`
2. `style(diff-summary): align report with shared UI`
3. `style(code-review): unify HTML report components`
4. `fix(code-review): enforce evidence-first review writing`
5. Documentation or follow-up fixes only when verification proves they are
   independently necessary.

Never force-push. Stop and report a non-fast-forward rejection.

## Acceptance Criteria

- The tracked HTML inventory still contains exactly the three intended report
  templates and all three implement the shared semantic token contract.
- Generated `diff-summary`, `diff-viewer`, and `code-review-html` documents read
  as one product family in light and dark themes at desktop and narrow widths.
- Every report-specific interaction continues to work.
- `diff-summary` contains no atlas/paper/poster visual language or ornamental UI
  copy.
- The main review prompt and its wrappers no longer force announcements,
  positive filler, duplicate recaps, or a fixed number of observations.
- Review prose instructions require concrete evidence, consequence, and action;
  unsupported claims are labeled or omitted.
- Targeted and full tests, skill validation, discovery, rendered-report checks,
  mirror comparisons, and `git diff --check` pass.
- Intermediate commits are present on the remote without force pushes.
