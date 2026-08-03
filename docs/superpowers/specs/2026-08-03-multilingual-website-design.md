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
- Lead with the approved promise, "어제의 반복이, 오늘의 스킬로.", and explain
  how reusable instructions and scripted deterministic work can reduce the
  amount of repeated LLM processing.
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
- No guarantee of a fixed token, cost, or latency reduction. Prompt-cache
  eligibility and savings depend on the model, stable-prefix length, cache
  lifetime, and request structure.
- No redesign of the catalog or theme control and no framework or styling-stack
  migration. The landing-page change is limited to copy, the benefits layout,
  and the supporting workflow argument.

## Landing Message and Conversion Contract

### Layout and page outline

Use layout A, a classic hero followed by product sections, because the existing
product-window preview makes the catalog understandable above the fold. Retain
the current section order and upgrade the argument inside it:

1. hero with one primary action and the product preview;
2. asymmetric efficiency benefits;
3. large word-by-word tagline reveal;
4. three-step role-separation workflow;
5. searchable skill catalog;
6. one skill shared by Claude Code and Codex;
7. FAQ with cache and scripting objections answered;
8. installation card and final call to action.

The hero has one primary conversion action, scrolling to the catalog. The
existing install button is removed from above the fold so it does not compete
with exploration before the visitor understands the offer. Installation
remains the final action after the argument and catalog.

### Hero

The Korean hero copy is fixed:

```text
어제의 반복이,
오늘의 스킬로.

Claude Code와 Codex에서 되풀이하던 소프트웨어 작업을 검증 가능한 20개의
워크플로로 바꿨습니다. 반복 지침은 캐시하기 좋은 형태로 재사용하고, 결과가
정해진 단계는 스크립트에 맡겨 LLM이 필요한 판단에 집중하게 합니다.
```

The primary action is `20개 스킬 살펴보기`. The adjacent proof line uses only
repository facts: `20 packaged skills · 6 categories · Claude Code + Codex ·
MIT`. No fabricated savings percentage or performance claim appears.

The four headline translations carry the same idea naturally rather than
matching Korean word for word:

| Locale | Headline |
|---|---|
| KO | `어제의 반복이, 오늘의 스킬로.` |
| EN | `Yesterday’s repetition becomes today’s skill.` |
| JP | `昨日の繰り返しを、今日のスキルへ。` |
| CN | `把昨天的重复，变成今天的技能。` |

Every locale provides a native-language subheadline with the same three facts:
twenty verified workflows, reusable cache-friendly instructions, and scripted
steps that let the LLM focus on judgment. `cache-friendly` is phrased as a
structural advantage, never a guaranteed cache hit.

### Efficiency benefits

Replace the generic three-equal-card outcome grid with an asymmetric section:
the claim and factual counts occupy the left column, while three vertically
stacked explanations occupy the wider right column. On narrow screens the
content becomes one reading-order column.

The Korean benefit contract is:

1. **같은 지침을 다시 만들지 않습니다.** 실행 순서와 예시, 안전 규칙을
   안정된 `SKILL.md`로 유지합니다. 반복 요청에서 동일한 앞부분이 유지되므로
   지원되는 모델의 프롬프트 캐시를 활용하기 좋은 구조가 됩니다.
2. **정해진 일은 스크립트가 처리합니다.** 파일 탐색, 형식 검사, 데이터
   동기화처럼 결과가 명확한 단계는 스크립트로 실행합니다. 모델이 같은 절차를
   매번 다시 추론하지 않게 해 LLM 사용 범위를 줄입니다.
3. **LLM은 판단에 집중합니다.** 요구사항 해석, 코드 검토, 위험 판단처럼
   문맥이 필요한 부분에 모델을 사용하고, 실행 순서와 완료 조건은 스킬이
   고정합니다.

The copy distinguishes two mechanisms. Stable reusable instruction prefixes
are more compatible with prompt caching; deterministic scripts reduce the work
that needs model judgment in the first place. It does not claim that saving a
`SKILL.md` automatically enables an API cache.

### Tagline reveal

Keep the existing word-by-word reveal and use the exact user-approved Korean
copy:

```text
좋은 프롬프트는 한 번 쓰고 사라집니다.
하지만 스킬로 만들면 기본기가 됩니다.
```

Each translation preserves the contrast between an ephemeral prompt and a
reusable skill. The reveal remains at least two lines, uses meaningful line
breaks, and honors reduced motion.

### How it works

Refocus the existing three-step window from a generic request lifecycle to the
division of responsibilities:

1. **반복을 포착합니다.** 자주 되풀이하는 요청과 산출물을 찾습니다.
2. **기준을 고정합니다.** 실행 순서, 안전 규칙과 완료 조건을 스킬에
   남깁니다.
3. **역할을 나눕니다.** 판단은 LLM이 맡고, 결과가 정해진 단계는 스크립트가
   실행합니다.

The existing product chrome and verified status row stay in place so the
section demonstrates a real workflow rather than becoming another prose block.

### FAQ and claim boundaries

Add two visible FAQ entries, sourced from the same locale data as FAQ JSON-LD:

**스킬을 쓰면 토큰이 항상 줄어드나요?**

> 항상 보장되지는 않습니다. 프롬프트 캐시는 사용하는 모델과 지침 길이,
> 동일한 앞부분의 유지 여부에 따라 달라집니다. 다만 스킬은 반복 지침을
> 안정된 형태로 재사용하고, 스크립트로 처리할 단계를 분리해 불필요한 LLM
> 작업을 줄이도록 설계됩니다.

**어떤 작업을 스크립트로 처리하나요?**

> 입력과 결과를 규칙으로 확인할 수 있는 작업입니다. 파일 검색, 형식 검사,
> 카탈로그 동기화와 테스트 실행은 스크립트에 맡기고, 해석과 검토가 필요한
> 작업은 LLM이 담당합니다.

These boundaries reflect the official platform behavior: OpenAI documents
discounted cached input for repeated common prompt prefixes, and Anthropic
documents that cache hits require reusable, identical prefix content. The site
may describe the design as cache-friendly, but it may not promise a hit or a
specific saving. References:

- <https://openai.com/index/api-prompt-caching/>
- <https://platform.claude.com/docs/en/build-with-claude/prompt-caching>

### SEO and social copy

The Korean document and social title becomes
`chann/skills - 어제의 반복이, 오늘의 스킬로`. The Korean description is:

```text
Claude Code와 Codex의 반복 작업을 재사용 가능한 스킬로 바꾸세요. 캐시
친화적인 지침과 스크립트 실행으로 LLM이 필요한 판단에 집중합니다.
```

English, Japanese, and Simplified Chinese use native equivalents rather than
the Korean text. All four social cards use the locale headline while retaining
the current `chann/skills` composition. The page remains indexed because it is
an evergreen open-source catalog, not a time-bound campaign.

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
6. every locale supplies the hero, three efficiency benefits, tagline reveal,
   three workflow steps, and both claim-boundary FAQ entries;
7. Korean keeps the exact approved hero and tagline wording, and the hero has
   exactly one primary conversion action;
8. the existing catalog, branding, and text-wrapping verifiers remain green.

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
- one primary hero action, the asymmetric benefits layout, exact Korean hero
  and tagline copy, and natural localized equivalents in all four languages;
- cache and scripting explanations that preserve the approved claim boundaries
  and appear in both visible FAQ and JSON-LD;
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
- The Korean hero reads `어제의 반복이, 오늘의 스킬로.` and exposes only the
  `20개 스킬 살펴보기` primary action above the fold.
- The benefits explain reusable cache-friendly instructions, deterministic
  scripted steps, and LLM judgment as distinct mechanisms without promising a
  fixed saving.
- The Korean tagline reads `좋은 프롬프트는 한 번 쓰고 사라집니다. 하지만
  스킬로 만들면 기본기가 됩니다.` and retains its word-by-word reveal.
- The workflow teaches capture, fixed criteria, and script/LLM role separation,
  and the two new FAQ entries state the cache and scripting boundaries.
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
