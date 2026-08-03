# Multilingual Skills Website Design

**Date:** 2026-08-03
**Status:** Approved direction

## Problem

The public `chann/skills` website currently has one Korean HTML entry point and
keeps nearly all visible copy inside React components or
`website/src/data/skills.ts`. Its navigation, catalog, twenty skill summaries,
FAQ, accessibility labels, structured data, social metadata, and 404 page are
therefore Korean-only.

The site must support Korean, English, Japanese, and Simplified Chinese without
changing the existing Korean-first product contract. A visitor who opens the
root URL must continue to see Korean regardless of browser preferences. The
three additional languages need durable, directly loadable GitHub Pages URLs,
fully localized content, and search/share metadata that does not depend on
client-side JavaScript.

## Goals

- Keep `https://chann.github.io/skills/` permanently Korean with no browser
  language redirect and no previously selected locale override.
- Add stable English, Japanese, and Simplified Chinese pages at `/skills/en/`,
  `/skills/jp/`, and `/skills/cn/`.
- Localize all product prose: navigation, hero and supporting sections,
  catalog category copy, all twenty skill summaries/use cases/results, FAQ,
  interactive feedback, accessibility labels, metadata, and 404 copy.
- Keep source contracts such as skill IDs, titles, selectors, aliases,
  installation commands, and code examples unchanged.
- Use one current-language pill and disclosure list at every viewport size.
- Preserve only the current section hash when changing languages. Reset
  catalog search, filter, and selected-skill state.
- Emit crawlable, language-specific HTML metadata and structured data at build
  time.
- Fail the build on missing or structurally inconsistent translations.
- Preserve the current visual system, responsive behavior, theme control,
  Korean-aware line breaking, and official GitHub mark.

## Non-goals

- No automatic locale negotiation or redirect from the Korean root.
- No `/ko/` route. Korean remains the unprefixed canonical page.
- No translation of skill identifiers, human-readable skill titles, selectors,
  aliases, commands, code samples, or repository names.
- No URL persistence for search text, category filters, or selected skills.
- No user-authored translation editor, remote translation service, or runtime
  translation download.
- No redesign of the catalog, theme control, page sections, or overall visual
  hierarchy.

## Locale and Route Contract

The public route code is deliberately separate from the standards-compliant
document language code:

| Locale key | Public path | HTML `lang` | Open Graph locale | Switcher label |
|---|---|---|---|---|
| `ko` | `/skills/` | `ko` | `ko_KR` | `한국어 (KO)` |
| `en` | `/skills/en/` | `en` | `en_US` | `English (EN)` |
| `jp` | `/skills/jp/` | `ja` | `ja_JP` | `日本語 (JP)` |
| `cn` | `/skills/cn/` | `zh-CN` | `zh_CN` | `简体中文 (CN)` |

`jp` and `cn` remain the user-requested URL codes; `ja` and `zh-CN` are used
where HTML and search standards expect language tags. Locale resolution is a
pure function of the current entry point. It does not consult
`navigator.language` or locale storage.

The production build emits:

```text
website/dist/
├── index.html
├── en/index.html
├── jp/index.html
├── cn/index.html
├── 404.html
└── assets/...
```

The production pipeline uses Vite for the shared application bundle and a
deterministic locale-page generation step for the four HTML files. Every
supported URL therefore exists as a real static file on GitHub Pages. The entry
pages share the same React application and asset graph, but each declares its
locale before bootstrapping the application. Direct loads and refreshes return
a successful document without relying on `404.html` as an SPA router.

## Architecture

### Locale registry

`website/src/i18n/locales.ts` is the single route registry. It defines the
locale union, public path, HTML language, Open Graph locale, native switcher
label, canonical URL, and social-card path. Helpers map an entry-point locale to
its base URL and create a language-switch URL from an optional supported hash.

The application receives the resolved locale explicitly from its static entry
point. Components consume a typed locale model rather than inspecting
`window.location.pathname` independently.

### Canonical skill data

`website/src/data/skills.ts` is split conceptually into:

1. invariant skill data: `id`, title, category key, examples, selectors,
   aliases, and non-display lookup tags;
2. locale content: summary, when-to-use, result, and any localized search
   terms.

The packaged-skill verifier continues to validate the invariant IDs and
selectors against repository `SKILL.md` frontmatter. Localization is joined by
skill ID, so translation work cannot duplicate or redefine the package
contract.

### Translation schema

Each locale exports the same TypeScript schema. The schema contains:

- document and social metadata;
- navigation, hero, workflow, outcome, installation, FAQ, and footer copy;
- category labels and descriptions;
- interactive catalog labels, counts, empty states, facts, and copy feedback;
- theme, GitHub, skip-link, product-preview, and other accessibility names;
- all twenty localized skill summaries, use cases, and results;
- 404 title, explanation, home action, and language navigation label.

The Korean module becomes the reference content rather than an implicit
fallback. English, Japanese, and Simplified Chinese modules must satisfy the
same exact shape. `satisfies` checks provide compile-time parity, while a build
verifier checks runtime key sets, locale registry completeness, skill ID order,
and non-empty localized fields. Missing text fails the build; it never silently
falls back to Korean.

FAQ rendering and FAQ JSON-LD use the same locale content so screen copy and
structured data cannot drift. Search combines localized summary/use-case/result
text with invariant skill IDs, English titles, selectors, aliases, examples,
and tags. Users can therefore search naturally in the active language or by the
canonical command name.

## Static Entry Points and Metadata

The four HTML entry points are generated from one maintained template during
the production build rather than hand-copying large documents. The generator
reuses Vite's bundled HTML shell and writes language-specific values for:

- `<html lang>`;
- `<title>` and description;
- canonical URL;
- `og:locale`, title, description, URL, image, and image alt;
- Twitter title, description, and image;
- FAQ JSON-LD;
- locale bootstrap value;
- alternate `hreflang` links.

Every page links to the following alternates:

```text
ko      https://chann.github.io/skills/
en      https://chann.github.io/skills/en/
ja      https://chann.github.io/skills/jp/
zh-CN   https://chann.github.io/skills/cn/
x-default https://chann.github.io/skills/
```

The Korean root is `x-default` because it is the deliberate product default,
not the result of language negotiation.

Four 1200×630 social cards retain the current composition and `chann/skills`
branding while localizing the supporting tagline. Each page references its own
card and translated alt text. Asset verification checks dimensions, existence,
and the exact page-to-card mapping.

## Language Switcher

The header renders the same compact pill on desktop and mobile. Its visible
label is the current route code followed by a chevron: `KO⌄`, `EN⌄`, `JP⌄`, or
`CN⌄`. The disclosure list always uses this order:

1. `한국어 (KO)`
2. `English (EN)`
3. `日本語 (JP)`
4. `简体中文 (CN)`

The trigger is a native button with an accessible name in the active language,
`aria-expanded`, and `aria-controls`. The disclosed choices are ordinary links
because changing language is navigation, not selection inside the current
document. The current link receives `aria-current="page"`.

Interaction behavior:

- click, Enter, or Space toggles the disclosure;
- Tab moves through its links using native browser order;
- Escape closes it and returns focus to the trigger;
- clicking outside closes it;
- choosing a language performs normal document navigation;
- the current hash is retained only when it names an existing site section;
- search text, category filter, and selected skill reset because they are
  component-local state in the newly loaded document.

Examples:

```text
/skills/#faq        -> /skills/en/#faq
/skills/jp/#explore -> /skills/#explore
/skills/cn/         -> /skills/jp/
```

The disclosure aligns to the right edge of the header action group and may not
increase the document's scroll width at 320px. It keeps the existing light and
dark tokens, visible hover/current/focus states, and reduced-motion contract.

## 404 Behavior

GitHub Pages serves one `website/public/404.html`. A small inline script reads
only the first segment after `/skills/`:

- `en` selects English;
- `jp` selects Japanese;
- `cn` selects Simplified Chinese;
- every other path, including `/skills/` descendants, selects Korean.

The 404 document does not redirect. It renders localized heading, explanation,
home action, accessible labels, and direct links to all four language roots.
Its initial static markup is complete Korean content so it remains usable when
JavaScript is unavailable. It retains `noindex`, current responsive styling,
both color-scheme variants, `word-break: keep-all`, and
`overflow-wrap: break-word`.

## Error and Fallback Rules

- Missing locale content, metadata, skill translation, or social-card mapping
  is a build error.
- An unsupported locale-like path is a localized 404, never a redirect.
- A language switch keeps only known section hashes. Unknown hashes are dropped
  rather than carried to an element that cannot receive focus or scroll.
- If local storage is unavailable, theme behavior keeps its existing dark
  fallback. Locale behavior is unaffected because it uses no storage.
- Catalog zero-result behavior stays within the active locale and the reset
  action restores the locale's default catalog state.

## Accessibility and Typography Contract

- Every translated interactive control has a native-language accessible name.
- The language trigger exposes expansion state and returns focus on Escape.
- The current language link exposes `aria-current="page"`.
- Status messages such as result counts and copy confirmation are translated
  and remain in their live regions.
- The skip link, navigation label, product preview, search, filter group, skill
  list, examples, GitHub link, and theme control are covered by the translation
  schema.
- Keyboard navigation, focus-visible rings, reduced motion, and target sizes
  retain the current site contracts.
- Global prose continues to use `word-break: keep-all` plus
  `overflow-wrap: break-word`; code, selectors, and long commands retain their
  overflow-safe code behavior.
- The switcher and translated strings must not create horizontal document
  overflow at 320px, 390px, or desktop width.

## Verification Strategy

### Static and build verification

Extend the website build pipeline with a multilingual verifier that checks:

1. all four locale modules satisfy the same recursive key set;
2. all twenty invariant skill IDs have exactly one localized record per locale;
3. selectors, aliases, examples, and canonical names do not change by locale;
4. each generated entry point has the expected `lang`, canonical, Open Graph
   locale, localized title/description, social card, FAQ JSON-LD, and all five
   alternate links;
5. the output contains `index.html`, `en/index.html`, `jp/index.html`,
   `cn/index.html`, and `404.html`;
6. the existing catalog, branding, and text-wrapping verifiers remain green.

Run:

```bash
npm --prefix website run verify:catalog
npm --prefix website run build
pytest -ra
```

### Local browser verification

Exercise all four direct URLs in a production-equivalent preview:

- correct visible language and `<html lang>` after direct load and refresh;
- correct current-language pill and native-name list order;
- mouse and keyboard disclosure behavior, Escape focus return, outside close,
  and current-page announcement;
- language switching from the page top and from each supported section hash;
- catalog state reset across a language change;
- localized query matches plus canonical selector/title search;
- copy feedback, empty state, FAQ, theme control, GitHub link, and 404 copy;
- light and dark themes at 320px, 390px, and 1440px;
- zero horizontal document overflow and no browser console errors;
- Axe automated accessibility checks after the switcher is open and after
  search/filter/selection interactions. Any Axe `incomplete` result is reported
  separately from violations.

### Deployment verification

After the implementation checkpoint is pushed and GitHub Pages completes:

- request all four production URLs and confirm successful responses;
- verify visible locale, canonical, alternates, JSON-LD, and social-card URLs
  from the deployed HTML;
- confirm each deployed social card matches its local artifact hash;
- repeat representative desktop/mobile, theme, keyboard, and Axe checks on the
  public site;
- confirm the deployed commit is the pushed commit;
- finish with a clean worktree and local/tracking/live-remote parity of `0 0`.

## Acceptance Criteria

- `/skills/` always renders Korean and never redirects based on browser or
  stored language.
- `/skills/en/`, `/skills/jp/`, and `/skills/cn/` are directly loadable static
  pages in English, Japanese, and Simplified Chinese.
- All visible product copy, all twenty skill descriptions/use cases/results,
  FAQ, feedback, accessibility labels, metadata, and 404 copy are localized.
- Skill identifiers, titles, selectors, aliases, commands, and examples remain
  source-accurate and identical across locales.
- Every viewport uses the approved current-language pill and native-name
  disclosure list.
- Language switching preserves supported section hashes and resets transient
  catalog state.
- Each page has correct standards-language tags, canonical URL, alternates,
  localized structured data, and localized social card.
- Missing translations fail verification instead of falling back silently.
- The existing visual, theming, line-breaking, catalog, branding, and official
  GitHub mark contracts remain intact.
- Repository tests, website build, local browser/accessibility checks, Pages
  deployment checks, and Git parity all pass.
