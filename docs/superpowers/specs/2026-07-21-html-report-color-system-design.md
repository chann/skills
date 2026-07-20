# HTML Report Color System Design

**Date:** 2026-07-21
**Status:** Approved direction; pending spec review

## Problem

The HTML report family already shares the same core light and dark values, but
those values are the flat default zinc palette: pure white page and card
surfaces, near-black text, and nearly indistinguishable muted, secondary, and
accent backgrounds. The result is technically consistent but visually weak,
especially in the light theme.

The report family needs a deliberate shared color system that makes
`code-review-html`, `diff-summary`, and `diff-viewer` look like one product
family while preserving the distinct meaning of review severity, summary
impact, and added/deleted diff content.

## Goals

- Replace the current zinc palette with the approved **Cool editorial**
  direction.
- Give the light theme visible surface hierarchy without relying on heavy
  shadows or saturated decoration.
- Give the dark theme the same cool hue family and clearer page/card/popover
  separation.
- Keep every core theme token byte-for-byte identical across the three
  canonical HTML templates.
- Add one shared semantic status palette for success, warning, danger, and
  information, then map report-specific colors onto it.
- Keep body text, muted text, controls, badges, and status text at WCAG AA
  contrast or better.
- Preserve exact-selector package independence and the generated single-file
  report behavior.

## Non-goals

- No layout, spacing, typography, metadata, command-panel, navigation, or
  interaction changes.
- No parser, renderer, CLI, report naming, comment, quiz, or diff behavior
  changes.
- No runtime shared stylesheet. Each skill remains independently installable
  and each generated report keeps its existing asset model.
- No new font, icon, framework, animation, or network dependency.
- No replacement of the user-selectable Highlight.js code schemes in
  `code-review-html` and `diff-viewer`.

## Canonical Surfaces

The color system applies to these canonical templates:

1. `code-review/skills/code-review/assets/report-template.html`
2. `code-review/skills/diff-summary/assets/summary-template.html`
3. `code-review/skills/diff-viewer/assets/diff-template.html`

The diff-summary template remains byte-identical in its independently
installable copies:

- `code-review/skills/diff-summary-md/assets/summary-template.html`
- `code-review/skills/diff-summary-quiz/assets/summary-template.html`
- `.agents/skills/diff-summary/assets/summary-template.html`
- `.agents/skills/diff-summary-md/assets/summary-template.html`
- `.agents/skills/diff-summary-quiz/assets/summary-template.html`

## Visual Direction

The page uses a restrained editorial hierarchy:

- A pale blue-gray page distinguishes the canvas from white cards in light
  mode.
- White cards remain neutral so code, prose, and status accents stay legible.
- Ink-blue text replaces near-black zinc and softens the light theme without
  reducing contrast.
- Steel blue is the single interaction color for primary controls, focus, and
  informational state.
- Borders use cool gray-blue values that remain visible without making every
  component look boxed in.
- Dark mode uses ink/navy surfaces rather than pure black, with the same steel
  blue interaction family and lighter semantic status colors.

Color is not decorative. Blue identifies interaction or information, green
means successful/added/positive, amber means warning or elevated impact, and
red means destructive/deleted/critical.

## Core Theme Tokens

Every canonical template uses these exact values.

| Token | Light | Dark |
|---|---|---|
| `--background` | `#F5F7FA` | `#10151C` |
| `--foreground` | `#1E293B` | `#E7EDF5` |
| `--card` | `#FFFFFF` | `#151C25` |
| `--card-foreground` | `#1E293B` | `#E7EDF5` |
| `--popover` | `#FFFFFF` | `#1A222D` |
| `--popover-foreground` | `#1E293B` | `#E7EDF5` |
| `--muted` | `#EEF2F6` | `#202A36` |
| `--muted-foreground` | `#5F6B7A` | `#A8B3C2` |
| `--primary` | `#2F5D8C` | `#8FB7DE` |
| `--primary-foreground` | `#FFFFFF` | `#102235` |
| `--secondary` | `#E8EEF5` | `#202A36` |
| `--secondary-foreground` | `#26384D` | `#DCE5EF` |
| `--accent` | `#E3EDF7` | `#24364A` |
| `--accent-foreground` | `#244F7A` | `#DCEBFA` |
| `--destructive` | `#B4233A` | `#8E2F3D` |
| `--destructive-foreground` | `#FFFFFF` | `#FFD9DE` |
| `--border` | `#D6DEE8` | `#2D3948` |
| `--input` | `#C8D3E0` | `#39485A` |
| `--ring` | `#3D6F9E` | `#91B9E0` |
| `--shadow` | `0 1px 2px rgba(15, 34, 58, 0.08)` | `none` |

The light page background and card color must remain different. The dark page,
card, and popover values must also remain distinct so the hierarchy does not
depend on borders alone.

## Shared Semantic Status Tokens

Every canonical template declares the following tokens, even when a report
does not use every token directly.

| Token | Light | Dark | Meaning |
|---|---|---|---|
| `--status-success` | `#24734D` | `#74C69D` | positive, added, correct |
| `--status-success-soft` | `#DDF3E7` | `#183B2D` | positive surface |
| `--status-warning` | `#7A5900` | `#E9C46A` | elevated impact, caution |
| `--status-warning-soft` | `#F7EBC6` | `#3F3416` | warning surface |
| `--status-danger` | `#B4233A` | `#FF8A99` | critical, deleted, invalid |
| `--status-danger-soft` | `#FCE4E7` | `#4A2028` | danger surface |
| `--status-info` | `#2F5D8C` | `#9CC4EA` | informational, low severity |
| `--status-info-soft` | `#E3EDF7` | `#21364B` | informational surface |

Report-specific tokens map onto this shared vocabulary:

| Report | Mapping |
|---|---|
| `code-review-html` | critical → status-danger; medium → status-warning; low → status-info; info → muted foreground; high uses `#A84413` light and `#F5A367` dark |
| `diff-summary` | impact-high → status-warning; positive → status-success; positive-soft → status-success-soft; incorrect/destructive → status-danger |
| `diff-viewer` | added text/line → status-success/status-success-soft; deleted text/line → status-danger/status-danger-soft; hunk → status-info |

The aliases may use `var(...)`, but the resolved colors must be identical across
reports. Component-specific tokens must not introduce a second competing green,
amber, red, or blue family.

## Code And Diff Colors

The light code canvas uses:

- `--code-bg: #F8FAFC`
- `--code-fg: #1E293B`
- `--code-muted: #728095`
- add hue/text from the shared success family
- delete hue/text from the shared danger family
- hunk hue/text from the shared info family
- selection color derived from `--status-info`

The selectable Highlight.js schemes keep controlling syntax token colors.
Page-theme changes must not make a dark code scheme unreadable on a light page
or vice versa. Existing `data-code-tone` overrides remain the boundary for
diff-line text on dark code canvases.

## Contrast Contract

The chosen values have these measured contrast ratios:

| Pair | Ratio |
|---|---:|
| light foreground / background | `13.63:1` |
| light muted foreground / muted | `4.82:1` |
| light primary / white | `6.85:1` |
| light destructive / white | `6.48:1` |
| light positive / card | `5.78:1` |
| dark foreground / background | `15.56:1` |
| dark muted foreground / muted | `6.84:1` |
| dark primary / primary foreground | `7.68:1` |
| dark destructive foreground / destructive | `6.19:1` |
| dark positive / card | `8.42:1` |

Tests enforce at least `4.5:1` for normal text pairs and status text against its
actual surface. Focus indicators remain visible against both the page and
control surfaces.

## Print Behavior

Print output always resolves to the light palette. Its page background becomes
white, while card borders and semantic status text keep the Cool editorial
light values. Decorative shadows are removed. The print override must not
reintroduce the old zinc token values.

## Packaging And Synchronization

The three canonical templates deliberately duplicate the core and semantic
token declarations because every skill must remain portable. Consistency is
enforced by tests rather than a runtime import.

After the canonical diff-summary template is updated, it is copied byte for
byte to the two exact-selector package copies and the three local `.agents`
mirrors. No mirror receives a hand-edited palette.

## Testing Strategy

1. Change the style-contract tests first so the old zinc palette fails.
2. Assert exact light and dark core token maps for all three canonical
   templates.
3. Assert exact semantic status maps and report-specific alias resolution.
4. Assert light/dark contrast for body, muted, primary, destructive, status,
   focus, and code/diff pairs.
5. Assert that the previous zinc literals are absent from active theme and
   print declarations.
6. Update the canonical templates and synchronize the standalone and local
   mirrors.
7. Run focused renderer, style-contract, package, and exact-selector tests.
8. Run the complete repository test suite.
9. Generate representative code-review, diff-summary, quiz, and diff-viewer
   artifacts; inspect light and dark themes at desktop and narrow widths.

## Acceptance Criteria

- Light reports visibly separate page, card, muted, secondary, accent, input,
  and border surfaces while retaining a restrained appearance.
- Dark reports use the same cool family and preserve page/card/popover
  hierarchy.
- The three canonical templates expose identical core and semantic token
  values in light and dark themes.
- Review severity, summary impact/positive state, and diff add/delete/hunk
  colors resolve to the same semantic families.
- All tested normal-text color pairs meet or exceed `4.5:1`.
- Theme, code-scheme, quiz, comment, copy, sidebar, print, and responsive
  behavior remains unchanged.
- Diff-summary canonical, exact-selector, and local mirror templates are
  byte-identical.
- Focused and full test suites pass.
- Generated artifacts are inspected in both themes and no active surface uses
  the old zinc palette.
