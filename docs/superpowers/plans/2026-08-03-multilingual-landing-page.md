# Multilingual Landing Page Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Publish a Korean-default `chann/skills` landing page with the approved efficiency message and complete English, Japanese, and Simplified Chinese static variants.

**Architecture:** Keep one React application and one Vite asset bundle. Move invariant skill contracts into canonical TypeScript data, move all visible prose into typed locale JSON files, and generate four localized static HTML documents from the bundled Korean shell. Resolve the runtime locale from the static document marker, never from browser preferences or storage.

**Tech Stack:** React 19, TypeScript 5.9, Vite 7, vanilla CSS, Motion, Phosphor Icons, Node.js ESM verification/build scripts, ImageMagick for committed social-card assets, pytest for repository contracts, agent-browser for rendered QA.

## Global Constraints

- Execute sequentially in the main session because this repository's `AGENTS.md` forbids subagent dispatch.
- Keep `/skills/` Korean. Do not add `/ko/`, browser-language redirects, or locale storage.
- Publish `/skills/en/`, `/skills/jp/`, and `/skills/cn/`; use HTML language tags `en`, `ja`, and `zh-CN`.
- The Korean hero is exactly `어제의 반복이, 오늘의 스킬로.` and has one primary action: `20개 스킬 살펴보기`.
- The Korean tagline is exactly `좋은 프롬프트는 한 번 쓰고 사라집니다. 하지만 스킬로 만들면 기본기가 됩니다.`
- Describe prompt caching as a compatible structure, not a guaranteed hit or fixed saving.
- Explain stable instructions, deterministic scripts, and LLM judgment as three distinct mechanisms.
- Keep skill IDs, English titles, selectors, aliases, commands, examples, and repository branding invariant across locales.
- Use `KO⌄`, `EN⌄`, `JP⌄`, or `CN⌄` for the trigger and `한국어 (KO)`, `English (EN)`, `日本語 (JP)`, `简体中文 (CN)` for the links in that order.
- Preserve only supported section hashes on language navigation; reset search, filter, and selected-skill state through document navigation.
- Keep `word-break: keep-all` and `overflow-wrap: break-word` on prose, with code overflow behavior unchanged.
- Keep the existing React/Vite/vanilla-CSS stack, theme behavior, official GitHub mark, favicon, and reduced-motion behavior.
- Stage explicit paths, use Conventional Commits, push each green task immediately, never force-push, and verify upstream parity `0 0` after every checkpoint.
- Design source: `docs/superpowers/specs/2026-08-03-multilingual-website-design.md`.

---

## File Responsibility Map

### Canonical application data

- `website/src/data/skills.ts`: invariant skill IDs, English titles, category keys, examples, selectors, aliases, and search tags only.
- `website/src/i18n/types.ts`: `Locale`, localized content interfaces, and `LocalizedSkill` types.
- `website/src/i18n/locales.ts`: public route registry, standards-language metadata, supported hash set, and `localeHref()`.
- `website/src/i18n/content/{ko,en,jp,cn}.json`: every visible string, category copy, twenty localized skill records, metadata, and 404 copy.
- `website/src/i18n/content.ts`: typed JSON imports, `contentByLocale`, `getContent()`, `getLocalizedSkills()`, and `formatMessage()`.

### React surfaces

- `website/src/main.tsx`: read `data-locale`, resolve the locale, and render `<App locale={locale} />`.
- `website/src/App.tsx`: consume localized content and localized skills; render the approved landing argument.
- `website/src/components/SkillExplorer.tsx`: accept localized skills, categories, and catalog labels through props.
- `website/src/components/CopyButton.tsx`: accept idle/success/error labels through props.
- `website/src/components/ThemeToggle.tsx`: accept localized theme labels through props.
- `website/src/components/LanguageSwitcher.tsx`: accessible disclosure navigation between the four static documents.
- `website/src/styles.css`: asymmetric benefits layout, language disclosure states, responsive behavior, and existing theme/motion contracts.

### Static build and verification

- `website/index.html`: Korean build shell with absolute favicon, localized metadata anchors, and locale marker.
- `website/public/404.html`: Korean no-JavaScript fallback plus path-aware localized copy and four root links.
- `website/scripts/verify-landing-message.mjs`: exact hero/tagline/claim-boundary contract.
- `website/scripts/verify-locales.mjs`: locale key parity, required records, invariant selector fields, and non-empty translations.
- `website/scripts/generate-localized-pages.mjs`: duplicate the Vite shell and inject locale metadata/FAQ schema into the four output paths.
- `website/scripts/verify-built-locales.mjs`: verify generated paths, tags, canonical/alternate links, FAQ schema, and asset references.
- `website/scripts/generate-social-cards.mjs`: deterministic locale-card SVG composition rendered to PNG with ImageMagick.
- `website/scripts/verify-social-cards.mjs`: PNG signature/dimensions and locale-to-file completeness.
- `website/scripts/verify-branding.mjs`: preserve repository branding and official GitHub mark while reading localized metadata.
- `website/package.json`: ordered prebuild, build, postbuild, and verifier commands.
- `website/README.md`: multilingual routes, content ownership, social-card regeneration, and verification commands.

### Generated committed assets

- Create `website/public/assets/skills-social-card-ko.png`.
- Create `website/public/assets/skills-social-card-en.png`.
- Create `website/public/assets/skills-social-card-jp.png`.
- Create `website/public/assets/skills-social-card-cn.png`.
- Delete `website/public/assets/skills-social-card.webp` only after all HTML points at locale PNG assets.

---

### Task 1: Ship the approved Korean landing argument

**Files:**
- Create: `website/scripts/verify-landing-message.mjs`
- Modify: `website/src/App.tsx`
- Modify: `website/src/styles.css`
- Modify: `website/index.html`
- Modify: `website/scripts/verify-branding.mjs`
- Modify: `website/package.json`

**Interfaces:**
- Consumes: existing `skills`, `categoryOrder`, `Reveal`, `TaglineReveal`, and Motion primitives.
- Produces: approved Korean hero, asymmetric `.efficiency-layout`, exact tagline, role-separation workflow, two new FAQ items, and a build-enforced messaging contract.

- [ ] **Step 1: Write the failing landing-message verifier**

Create `website/scripts/verify-landing-message.mjs` with source assertions for the exact approved copy and structure:

```js
import { readFile } from "node:fs/promises";
import path from "node:path";
import { fileURLToPath } from "node:url";

const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..");
const app = await readFile(path.join(root, "src", "App.tsx"), "utf8");
const html = await readFile(path.join(root, "index.html"), "utf8");

for (const text of [
  "어제의 반복이,",
  "오늘의 스킬로.",
  "같은 지침을 다시 만들지 않습니다.",
  "정해진 일은 스크립트가 처리합니다.",
  "LLM은 판단에 집중합니다.",
  "하지만 스킬로 만들면 기본기가 됩니다.",
  "스킬을 쓰면 토큰이 항상 줄어드나요?",
  "어떤 작업을 스크립트로 처리하나요?",
]) {
  if (!app.includes(text)) throw new Error(`Missing landing message: ${text}`);
}

if (!app.includes('className="efficiency-layout"')) {
  throw new Error("Missing asymmetric efficiency layout.");
}

const hero = app.match(/<section className="hero"[\s\S]*?<\/section>/)?.[0] ?? "";
if ((hero.match(/button--primary/g) ?? []).length !== 1) {
  throw new Error("Hero must contain exactly one primary action.");
}

if (!html.includes("chann/skills - 어제의 반복이, 오늘의 스킬로")) {
  throw new Error("Korean metadata title is stale.");
}

console.log("Approved landing message verified.");
```

- [ ] **Step 2: Add the verifier to the build and prove it fails**

Add:

```json
"verify:landing": "node scripts/verify-landing-message.mjs"
```

Insert `npm run verify:landing` before TypeScript in `build`. Run:

```bash
npm --prefix website run verify:landing
```

Expected: FAIL on `어제의 반복이,`.

- [ ] **Step 3: Replace the hero and proof line**

Render exactly one hero action and real proof values:

```tsx
<h1 id="hero-title">
  <span>어제의 반복이,</span>
  <span>오늘의 스킬로.</span>
</h1>
<p className="hero__lede">
  Claude Code와 Codex에서 되풀이하던 소프트웨어 작업을 검증 가능한
  {` ${skills.length}개의 `}워크플로로 바꿨습니다. 반복 지침은 캐시하기 좋은
  형태로 재사용하고, 결과가 정해진 단계는 스크립트에 맡겨 LLM이 필요한
  판단에 집중하게 합니다.
</p>
<div className="hero__actions">
  <a className="button button--primary" href="#explore">
    {skills.length}개 스킬 살펴보기
    <ArrowRight size={17} weight="bold" aria-hidden="true" />
  </a>
</div>
<p className="hero__meta">
  {skills.length} packaged skills · {categoryOrder.length} categories · Claude Code + Codex · MIT
</p>
```

- [ ] **Step 4: Replace equal outcome cards with the efficiency argument**

Use three items with exact titles and claim boundaries. Keep icons decorative and use existing Phosphor imports or confirmed package exports only:

```tsx
const efficiencyBenefits = [
  {
    title: "같은 지침을 다시 만들지 않습니다.",
    description: "실행 순서와 예시, 안전 규칙을 안정된 SKILL.md로 유지합니다. 반복 요청에서 동일한 앞부분이 유지되므로 지원되는 모델의 프롬프트 캐시를 활용하기 좋은 구조가 됩니다.",
  },
  {
    title: "정해진 일은 스크립트가 처리합니다.",
    description: "파일 탐색, 형식 검사, 데이터 동기화처럼 결과가 명확한 단계는 스크립트로 실행합니다. 모델이 같은 절차를 매번 다시 추론하지 않게 해 LLM 사용 범위를 줄입니다.",
  },
  {
    title: "LLM은 판단에 집중합니다.",
    description: "요구사항 해석, 코드 검토, 위험 판단처럼 문맥이 필요한 부분에 모델을 사용하고, 실행 순서와 완료 조건은 스킬이 고정합니다.",
  },
];
```

The section DOM is one intro column plus one ordered vertical list. CSS uses `grid-template-columns: minmax(15rem, 0.72fr) minmax(0, 1.28fr)` at desktop and one column below 767px. Remove the old `.outcome-grid` and `.outcome` rules after all consumers are gone.

- [ ] **Step 5: Update the tagline, workflow, and FAQs**

Set the tagline lines to:

```tsx
lines={[
  "좋은 프롬프트는 한 번 쓰고 사라집니다.",
  "하지만 스킬로 만들면 기본기가 됩니다.",
]}
```

Set the three workflow steps to `반복을 포착합니다`, `기준을 고정합니다`, and `역할을 나눕니다` with the exact descriptions in the approved spec. Append the two cache/script FAQ entries, including the sentence `항상 보장되지는 않습니다.`

- [ ] **Step 6: Update Korean metadata and FAQ JSON-LD**

Change document, Open Graph, and Twitter titles to `chann/skills - 어제의 반복이, 오늘의 스킬로`. Use this description:

```text
Claude Code와 Codex의 반복 작업을 재사용 가능한 스킬로 바꾸세요. 캐시 친화적인 지침과 스크립트 실행으로 LLM이 필요한 판단에 집중합니다.
```

Add the two visible FAQs to JSON-LD with byte-equivalent answer meaning. Update `verify-branding.mjs` to require the new title and keep its official GitHub mark checks.

- [ ] **Step 7: Run focused and production checks**

```bash
npm --prefix website run verify:landing
npm --prefix website run verify:branding
npm --prefix website run build
git diff --check
```

Expected: all pass; `dist/index.html` contains the new Korean title and copy.

- [ ] **Step 8: Review, commit, push, and prove parity**

```bash
git add website/src/App.tsx website/src/styles.css website/index.html website/scripts/verify-landing-message.mjs website/scripts/verify-branding.mjs website/package.json
git commit -m "feat(site): explain reusable skill efficiency"
git push origin main
git rev-list --left-right --count HEAD...@{upstream}
```

Expected parity: `0 0`.

---

### Task 2: Centralize Korean content behind a typed locale boundary

**Files:**
- Create: `website/src/i18n/types.ts`
- Create: `website/src/i18n/locales.ts`
- Create: `website/src/i18n/content/ko.json`
- Create: `website/src/i18n/content.ts`
- Create: `website/scripts/verify-locales.mjs`
- Modify: `website/src/data/skills.ts`
- Modify: `website/src/main.tsx`
- Modify: `website/src/App.tsx`
- Modify: `website/src/components/SkillExplorer.tsx`
- Modify: `website/src/components/CopyButton.tsx`
- Modify: `website/src/components/ThemeToggle.tsx`
- Modify: `website/scripts/verify-landing-message.mjs`
- Modify: `website/scripts/verify-catalog.mjs`
- Modify: `website/package.json`

**Interfaces:**
- Consumes: all current Korean copy and invariant skill records.
- Produces: `Locale`, `SiteContent`, `contentByLocale`, `getContent(locale)`, `getLocalizedSkills(locale)`, and prop-driven localized components while preserving Korean output.

- [ ] **Step 1: Write a failing locale verifier**

Create a recursive key collector and invariant checks:

```js
const requiredLocales = ["ko"];
const requiredSkillFields = ["summary", "whenToUse", "result"];

function keyPaths(value, prefix = "") {
  if (Array.isArray(value)) return value.flatMap((item, index) => keyPaths(item, `${prefix}[${index}]`));
  if (value && typeof value === "object") {
    return Object.entries(value).flatMap(([key, item]) => keyPaths(item, prefix ? `${prefix}.${key}` : key));
  }
  return [prefix];
}
```

The verifier reads `src/i18n/content/ko.json`, requires non-empty strings, exactly twenty skill IDs, all three localized skill fields, exactly three benefits, two tagline lines, three workflow steps, and ten FAQs. It reads canonical IDs from `src/data/skills.ts` and reports missing/extra IDs.

- [ ] **Step 2: Run the verifier and prove it fails**

```bash
node website/scripts/verify-locales.mjs
```

Expected: FAIL because `ko.json` does not exist.

- [ ] **Step 3: Define the exact TypeScript boundary**

Use these public shapes in `types.ts`:

```ts
export type Locale = "ko" | "en" | "jp" | "cn";

export interface SkillCopy {
  summary: string;
  whenToUse: string;
  result: string;
}

export interface MetadataContent {
  title: string;
  description: string;
  socialAlt: string;
}

export interface CatalogContent {
  categoryNavigation: string;
  searchLabel: string;
  searchPlaceholder: string;
  clearSearch: string;
  filtersLabel: string;
  all: string;
  count: string;
  skillList: string;
  whenToUse: string;
  result: string;
  exampleRequest: string;
  exampleCopy: string;
  aliases: string;
  emptyTitle: string;
  emptyDescription: string;
  showAll: string;
}

export interface PlatformContent {
  label: string;
  title: string[];
  descriptionBeforeCodex: string;
  descriptionBetweenSelectors: string;
  descriptionAfterClaude: string;
  sharedInstructions: string;
  contractDescription: string;
}

export interface InstallContent {
  label: string;
  title: string[];
  description: string;
  cardTitle: string;
  cardDescription: string;
  copyLabel: string;
  resultsLabel: string;
  skillResult: string;
  linkResult: string;
  platformsResult: string;
  exploreAction: string;
  githubAction: string;
  license: string;
}

export interface ProductPreviewContent {
  sidebarLabel: string;
  packagedSkills: string;
  workspace: string;
  ready: string;
  tab: string;
  kicker: string;
  title: string[];
  lede: string;
  proof: string[];
}

export interface AccessibilityContent {
  skipToMain: string;
  home: string;
  github: string;
  mainNavigation: string;
  installResults: string;
}

export interface SiteContent {
  meta: MetadataContent;
  nav: { label: string; items: Record<"why" | "explore" | "faq" | "install", string> };
  hero: { brand: string; headline: string[]; lede: string; primaryAction: string; proof: string };
  benefits: { label: string; title: string[]; description: string; items: Array<{ title: string; description: string }> };
  tagline: { label: string; lines: string[]; stats: Record<"skills" | "categories" | "platforms", string> };
  workflow: { label: string; title: string[]; description: string; steps: Array<{ number: string; label: string; title: string; description: string }>; status: string; artifact: string };
  catalog: CatalogContent;
  platforms: PlatformContent;
  faq: { label: string; title: string; description: string; items: Array<{ question: string; answer: string }> };
  install: InstallContent;
  footer: { tagline: string; license: string; github: string };
  productPreview: ProductPreviewContent;
  copy: { idle: string; copied: string; error: string };
  theme: { system: string; light: string; dark: string; change: string; title: string };
  language: { trigger: string; navigation: string };
  accessibility: AccessibilityContent;
  categories: Record<SkillCategory, { label: string; description: string }>;
  skills: Record<SkillId, SkillCopy>;
  notFound: { title: string; description: string; home: string; navigation: string };
}
```

Import `SkillCategory` and `SkillId` from `../data/skills`. Runtime verification additionally requires exactly two headline/tagline lines, exactly three benefits/workflow steps, three product proof strings, and ten FAQ items because JSON array inference does not preserve tuple lengths.

- [ ] **Step 4: Separate invariant skill definitions**

Keep this shape in `skills.ts`:

```ts
export interface SkillDefinition {
  id: SkillId;
  title: string;
  category: SkillCategory;
  example: string;
  claudeSelector: string;
  codexSelector: string;
  aliases?: string[];
  tags: string[];
}

export type SkillId =
  | "review-me"
  | "code-review"
  | "code-review-md"
  | "diff-summary"
  | "diff-summary-md"
  | "diff-summary-quiz"
  | "diff-viewer"
  | "gen-docs"
  | "git-commit"
  | "git-commit-push"
  | "git-commit-push-realtime"
  | "git-commit-realtime"
  | "git-commit-rewrite"
  | "git-merge-to-main"
  | "git-merge-to-dev"
  | "git-branch-cleanup"
  | "gen-frontend-handoff"
  | "gen-backend-handoff"
  | "long-task"
  | "work-summary";

```

Transform the existing array in place: delete only `summary`, `whenToUse`, and `result` from each object, rename the array `skillDefinitions`, add `as const satisfies readonly SkillDefinition[]`, and keep every remaining literal byte-equivalent. Do not retain an intermediate `currentSkills` array or a runtime mapping helper. The explicit `SkillId` union above and the verifier prevent a dropped or renamed entry. Keep `categoryOrder` invariant and move category labels/descriptions to locale content.

- [ ] **Step 5: Implement typed content loading and formatting**

```ts
import koJson from "./content/ko.json";
import type { Locale, SiteContent, SkillCopy } from "./types";
import { skillDefinitions, type SkillId } from "../data/skills";

const ko: SiteContent = koJson;
export const contentByLocale = { ko } as const;

export function getContent(locale: Locale): SiteContent {
  return contentByLocale[locale as keyof typeof contentByLocale] ?? ko;
}

export function formatMessage(template: string, values: Record<string, string | number>): string {
  return template.replace(/\{(\w+)\}/g, (_, key) => String(values[key] ?? `{${key}}`));
}

export function getLocalizedSkills(locale: Locale) {
  const copy = getContent(locale).skills as Record<SkillId, SkillCopy>;
  return skillDefinitions.map((definition) => ({ ...definition, ...copy[definition.id] }));
}
```

Use `{count}` tokens in locale messages where grammar wraps the skill count.

- [ ] **Step 6: Move all Korean copy and refactor consumers**

Populate `ko.json` with every existing visible and accessible string, including the approved landing copy and all twenty skill records. Render `<App locale="ko" />` through a locale resolved from `data-locale`. Pass explicit typed props to `SkillExplorer`, `CopyButton`, and `ThemeToggle`; do not make components import the Korean module directly.

Update `verify-landing-message.mjs` to read `ko.json` instead of expecting marketing copy inside `App.tsx`. Update `verify-catalog.mjs` to read invariant IDs from `skillDefinitions` and retain package parity.

- [ ] **Step 7: Verify behavior preservation**

```bash
npm --prefix website run verify:locales
npm --prefix website run verify:landing
npm --prefix website run verify:catalog
npm --prefix website run typecheck
npm --prefix website run build
git diff --check
```

Expected: all pass; root output remains Korean with twenty skills.

- [ ] **Step 8: Commit and push the typed content boundary**

```bash
git add website/src/data/skills.ts website/src/i18n/types.ts website/src/i18n/locales.ts website/src/i18n/content/ko.json website/src/i18n/content.ts website/src/main.tsx website/src/App.tsx website/src/components/SkillExplorer.tsx website/src/components/CopyButton.tsx website/src/components/ThemeToggle.tsx website/scripts/verify-locales.mjs website/scripts/verify-landing-message.mjs website/scripts/verify-catalog.mjs website/package.json
git commit -m "refactor(site): centralize localized content"
git push origin main
git rev-list --left-right --count HEAD...@{upstream}
```

Expected parity: `0 0`.

---

### Task 3: Publish English, Japanese, and Chinese static pages

**Files:**
- Create: `website/src/i18n/content/en.json`
- Create: `website/src/i18n/content/jp.json`
- Create: `website/src/i18n/content/cn.json`
- Create: `website/scripts/generate-localized-pages.mjs`
- Create: `website/scripts/verify-built-locales.mjs`
- Modify: `website/src/i18n/locales.ts`
- Modify: `website/src/i18n/content.ts`
- Modify: `website/scripts/verify-locales.mjs`
- Modify: `website/index.html`
- Modify: `website/package.json`

**Interfaces:**
- Consumes: `SiteContent`, canonical skill IDs, the bundled `dist/index.html`, and the fixed public route contract.
- Produces: four complete content modules and four crawlable static pages with correct runtime locale and metadata.

- [ ] **Step 1: Expand the failing locale verifier to four locales**

Set:

```js
const requiredLocales = ["ko", "en", "jp", "cn"];
```

Compare recursive key paths and array lengths against Korean, require the same twenty skill IDs, and fail on values that are empty or still byte-identical Korean where translation is required. Run:

```bash
npm --prefix website run verify:locales
```

Expected: FAIL because three locale files do not exist.

- [ ] **Step 2: Add the locale registry and URL helper**

```ts
export const localeRegistry = {
  ko: { code: "KO", path: "/skills/", htmlLang: "ko", ogLocale: "ko_KR", label: "한국어 (KO)", socialCard: "skills-social-card-ko.png" },
  en: { code: "EN", path: "/skills/en/", htmlLang: "en", ogLocale: "en_US", label: "English (EN)", socialCard: "skills-social-card-en.png" },
  jp: { code: "JP", path: "/skills/jp/", htmlLang: "ja", ogLocale: "ja_JP", label: "日本語 (JP)", socialCard: "skills-social-card-jp.png" },
  cn: { code: "CN", path: "/skills/cn/", htmlLang: "zh-CN", ogLocale: "zh_CN", label: "简体中文 (CN)", socialCard: "skills-social-card-cn.png" },
} as const;

export const supportedSectionHashes = new Set(["#main", "#why", "#usage", "#explore", "#faq", "#install"]);

export function localeHref(locale: Locale, hash: string): string {
  return `${localeRegistry[locale].path}${supportedSectionHashes.has(hash) ? hash : ""}`;
}
```

- [ ] **Step 3: Write native locale content**

Create full English, Japanese, and Simplified Chinese content files. They must include every field and all twenty skill summary/use-case/result records. Preserve invariant terms and code literally: `SKILL.md`, `Claude Code`, `Codex`, `Git`, `Markdown`, `$name`, `/name`, examples, and command lines.

Use these approved marketing anchors:

| Surface | EN | JP | CN |
|---|---|---|---|
| Hero | `Yesterday’s repetition becomes today’s skill.` | `昨日の繰り返しを、今日のスキルへ。` | `把昨天的重复，变成今天的技能。` |
| Benefit 1 | `Stop rebuilding the same instructions.` | `同じ指示を作り直しません。` | `不再重复编写相同的指令。` |
| Benefit 2 | `Let scripts handle predictable work.` | `決まった作業はスクリプトに任せます。` | `让脚本处理确定性的工作。` |
| Benefit 3 | `Keep the LLM focused on judgment.` | `LLMは判断に集中します。` | `让LLM专注于判断。` |
| Tagline line 1 | `A good prompt disappears after one use.` | `良いプロンプトは、一度使えば消えていきます。` | `好的提示词，用过一次就会消失。` |
| Tagline line 2 | `Turn it into a skill, and it becomes part of your foundation.` | `でもスキルにすれば、仕事の土台になります。` | `但把它做成技能，就会成为工作的基本功。` |

Translate for native clarity, not word order. English uses sentence case; Japanese and Chinese use native punctuation and concise product language. The cache FAQ in every locale must explicitly say savings are not guaranteed.

- [ ] **Step 4: Write the static page generator**

After Vite produces `dist/index.html`, read the shell and replace these surfaces for each locale: `<html lang>` and `data-locale`, title, description, canonical, Open Graph locale/title/description/url/image/alt, Twitter title/description/image, and the `#faq-schema` JSON-LD script. Write Korean back to `dist/index.html` and other locales to `dist/en/index.html`, `dist/jp/index.html`, and `dist/cn/index.html`.

Use escaping helpers:

```js
function escapeHtml(value) {
  return value.replaceAll("&", "&amp;").replaceAll('"', "&quot;").replaceAll("<", "&lt;").replaceAll(">", "&gt;");
}

function faqSchema(items) {
  return JSON.stringify({
    "@context": "https://schema.org",
    "@type": "FAQPage",
    mainEntity: items.map(({ question, answer }) => ({
      "@type": "Question",
      name: question,
      acceptedAnswer: { "@type": "Answer", text: answer },
    })),
  });
}
```

Use targeted regex replacements that require exactly one match and throw on zero or multiple matches. Change the favicon to `/skills/favicon.svg`. Add all five alternate links (`ko`, `en`, `ja`, `zh-CN`, `x-default`) to the source shell.

- [ ] **Step 5: Write the built-output verifier before wiring it**

Verify all output paths and expected values. For each page require one correct `lang`, `data-locale`, canonical, `og:locale`, title, social-card URL, ten-question JSON-LD, and all alternate links. Require no `__LOCALE_` or other generator sentinel text.

Run before generation:

```bash
node website/scripts/verify-built-locales.mjs
```

Expected: FAIL because locale output directories are missing.

- [ ] **Step 6: Wire production build ordering**

Use this order:

```json
"build": "npm run verify:catalog && npm run verify:text-wrapping && npm run verify:branding && npm run verify:landing && npm run verify:locales && tsc -b && vite build && node scripts/generate-localized-pages.mjs && node scripts/verify-built-locales.mjs"
```

Run:

```bash
npm --prefix website run build
```

Expected: four HTML pages verified.

- [ ] **Step 7: Commit and push static locale publication**

```bash
git add website/src/i18n/content/en.json website/src/i18n/content/jp.json website/src/i18n/content/cn.json website/src/i18n/content.ts website/src/i18n/locales.ts website/scripts/verify-locales.mjs website/scripts/generate-localized-pages.mjs website/scripts/verify-built-locales.mjs website/index.html website/package.json
git commit -m "feat(site): publish localized catalog routes"
git push origin main
git rev-list --left-right --count HEAD...@{upstream}
```

Expected parity: `0 0`.

---

### Task 4: Add accessible language navigation and localized 404 behavior

**Files:**
- Create: `website/src/components/LanguageSwitcher.tsx`
- Modify: `website/src/App.tsx`
- Modify: `website/src/styles.css`
- Modify: `website/public/404.html`
- Modify: `website/scripts/verify-locales.mjs`
- Modify: `website/scripts/verify-built-locales.mjs`

**Interfaces:**
- Consumes: `Locale`, `localeRegistry`, `localeHref()`, and localized language/accessibility copy.
- Produces: one disclosure control on every viewport and a no-redirect localized 404 page.

- [ ] **Step 1: Add failing switcher and 404 source checks**

Require `LanguageSwitcher.tsx`, `aria-expanded`, `aria-controls`, `aria-current="page"`, Escape focus restoration, all four native labels, and all four 404 locale dictionaries. Run:

```bash
npm --prefix website run verify:locales
```

Expected: FAIL on missing switcher source.

- [ ] **Step 2: Implement the disclosure component**

Use button plus navigation links, not a select or SPA state switch:

```tsx
import { formatMessage } from "../i18n/content";
import { localeHref, localeRegistry } from "../i18n/locales";
import type { Locale, SiteContent } from "../i18n/types";

interface LanguageSwitcherProps {
  locale: Locale;
  labels: SiteContent["language"];
}

export function LanguageSwitcher({ locale, labels }: LanguageSwitcherProps) {
  const [open, setOpen] = useState(false);
  const triggerRef = useRef<HTMLButtonElement>(null);
  const rootRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const onPointerDown = (event: PointerEvent) => {
      if (!rootRef.current?.contains(event.target as Node)) setOpen(false);
    };
    const onKeyDown = (event: KeyboardEvent) => {
      if (event.key !== "Escape" || !open) return;
      setOpen(false);
      triggerRef.current?.focus();
    };
    document.addEventListener("pointerdown", onPointerDown);
    document.addEventListener("keydown", onKeyDown);
    return () => {
      document.removeEventListener("pointerdown", onPointerDown);
      document.removeEventListener("keydown", onKeyDown);
    };
  }, [open]);

  const hash = typeof window === "undefined" ? "" : window.location.hash;
  const current = localeRegistry[locale];
  const entries = Object.entries(localeRegistry) as Array<
    [Locale, (typeof localeRegistry)[Locale]]
  >;

  return (
    <div className="language-switcher" ref={rootRef}>
      <button
        ref={triggerRef}
        type="button"
        className="language-switcher__trigger"
        aria-expanded={open}
        aria-controls="language-navigation"
        aria-label={formatMessage(labels.trigger, { language: current.label })}
        onClick={() => setOpen((value) => !value)}
      >
        <span>{current.code}</span><span aria-hidden="true">⌄</span>
      </button>
      {open ? (
        <nav
          id="language-navigation"
          className="language-switcher__menu"
          aria-label={labels.navigation}
        >
          <ul>
            {entries.map(([targetLocale, target]) => (
              <li key={targetLocale}>
                <a
                  href={localeHref(targetLocale, hash)}
                  aria-current={targetLocale === locale ? "page" : undefined}
                  onClick={() => setOpen(false)}
                >
                  {target.label}
                </a>
              </li>
            ))}
          </ul>
        </nav>
      ) : null}
    </div>
  );
}
```

The visible trigger is `${code}⌄`. `aria-label` names the current language in the active locale. Every link uses `localeHref(targetLocale, hash)` and current locale uses `aria-current="page"`.

- [ ] **Step 3: Fit the switcher into the existing header**

Render it before the theme toggle. CSS uses a `position: relative` root, compact 42px-minimum pill, absolutely positioned right-aligned list, full theme tokens, and 160ms `var(--ease-out)` transitions. At mobile width keep the same pill, hide no language control, and ensure header actions plus brand fit at 320px.

- [ ] **Step 4: Localize 404 without redirecting**

Keep complete Korean static markup. Add a small inline dictionary and replace text/attributes after reading the first path segment after `/skills/`:

```js
const locale = location.pathname.split("/").filter(Boolean)[1];
const active = ["en", "jp", "cn"].includes(locale) ? locale : "ko";
document.documentElement.lang = { ko: "ko", en: "en", jp: "ja", cn: "zh-CN" }[active];
```

Render direct links to all four roots and set their native labels. Do not call `location.replace`, `location.assign`, or set `location.href`.

- [ ] **Step 5: Run source, build, and browser interaction checks**

```bash
npm --prefix website run verify:locales
npm --prefix website run build
```

In a production preview, prove: direct route loads, trigger list order, current item, outside click, Escape focus return, known hash preservation, unknown hash drop, catalog state reset after navigation, and no horizontal overflow at 320px.

- [ ] **Step 6: Commit and push language navigation**

```bash
git add website/src/components/LanguageSwitcher.tsx website/src/App.tsx website/src/styles.css website/public/404.html website/scripts/verify-locales.mjs website/scripts/verify-built-locales.mjs
git commit -m "feat(site): add accessible language navigation"
git push origin main
git rev-list --left-right --count HEAD...@{upstream}
```

Expected parity: `0 0`.

---

### Task 5: Generate localized social cards and complete end-to-end proof

**Files:**
- Create: `website/scripts/generate-social-cards.mjs`
- Create: `website/scripts/verify-social-cards.mjs`
- Create: `website/public/assets/skills-social-card-ko.png`
- Create: `website/public/assets/skills-social-card-en.png`
- Create: `website/public/assets/skills-social-card-jp.png`
- Create: `website/public/assets/skills-social-card-cn.png`
- Delete: `website/public/assets/skills-social-card.webp`
- Modify: `website/scripts/verify-built-locales.mjs`
- Modify: `website/package.json`
- Modify: `website/README.md`

**Interfaces:**
- Consumes: locale headline records and the existing `chann/skills` social-card composition.
- Produces: four 1200×630 PNG assets, deterministic verification, maintenance documentation, and production/browser evidence.

- [ ] **Step 1: Write the failing PNG asset verifier**

Read the first 24 bytes of each file, verify the PNG signature, and read big-endian IHDR dimensions at offsets 16 and 20:

```js
const signature = Buffer.from([137, 80, 78, 71, 13, 10, 26, 10]);
if (!buffer.subarray(0, 8).equals(signature)) throw new Error(`${file} is not PNG`);
if (buffer.readUInt32BE(16) !== 1200 || buffer.readUInt32BE(20) !== 630) {
  throw new Error(`${file} must be 1200x630`);
}
```

Run:

```bash
node website/scripts/verify-social-cards.mjs
```

Expected: FAIL on missing locale PNGs.

- [ ] **Step 2: Add a reproducible ImageMagick generator**

Use this fixed record set and pipe a flat SVG into ImageMagick:

```js
import { spawn } from "node:child_process";
import { mkdir } from "node:fs/promises";
import path from "node:path";
import { fileURLToPath } from "node:url";

const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..");
const outputDirectory = path.join(root, "public", "assets");
const cards = [
  { locale: "ko", lang: "ko", lines: ["어제의 반복이,", "오늘의 스킬로."] },
  { locale: "en", lang: "en", lines: ["Yesterday’s repetition", "becomes today’s skill."] },
  { locale: "jp", lang: "ja", lines: ["昨日の繰り返しを、", "今日のスキルへ。"] },
  { locale: "cn", lang: "zh-CN", lines: ["把昨天的重复，", "变成今天的技能。"] },
];

function escapeXml(value) {
  return value.replaceAll("&", "&amp;").replaceAll("<", "&lt;").replaceAll(">", "&gt;");
}

function svgFor(card) {
  const [first, second] = card.lines.map(escapeXml);
  return `<svg xmlns="http://www.w3.org/2000/svg" width="1200" height="630" viewBox="0 0 1200 630" lang="${card.lang}">
    <rect width="1200" height="630" fill="#000000"/>
    <rect x="72" y="64" width="1056" height="502" rx="24" fill="#181818"/>
    <rect x="72" y="64" width="8" height="502" fill="#0044ff"/>
    <text x="128" y="148" fill="#85a2ff" font-family="Geist, Noto Sans CJK KR, Noto Sans CJK JP, Noto Sans CJK SC, sans-serif" font-size="30" font-weight="650">chann/skills</text>
    <text x="128" y="306" fill="#f7f8ff" font-family="Geist, Noto Sans CJK KR, Noto Sans CJK JP, Noto Sans CJK SC, sans-serif" font-size="70" font-weight="700" letter-spacing="-2">${first}</text>
    <text x="128" y="390" fill="#f7f8ff" font-family="Geist, Noto Sans CJK KR, Noto Sans CJK JP, Noto Sans CJK SC, sans-serif" font-size="70" font-weight="700" letter-spacing="-2">${second}</text>
    <text x="128" y="500" fill="#b4bad0" font-family="Geist, Noto Sans CJK KR, Noto Sans CJK JP, Noto Sans CJK SC, sans-serif" font-size="26">20 packaged skills · Claude Code + Codex · MIT</text>
  </svg>`;
}

function render(svg, output) {
  return new Promise((resolve, reject) => {
    const child = spawn("magick", ["svg:-", output], { stdio: ["pipe", "inherit", "inherit"] });
    child.on("error", () => reject(new Error("ImageMagick 'magick' is required to regenerate social cards.")));
    child.on("exit", (code) => code === 0 ? resolve() : reject(new Error(`magick exited with ${code}`)));
    child.stdin.end(svg);
  });
}

await mkdir(outputDirectory, { recursive: true });
for (const card of cards) {
  await render(svgFor(card), path.join(outputDirectory, `skills-social-card-${card.locale}.png`));
}
```

This is a maintainer command, not part of CI build. The committed PNGs are the CI inputs.

Generate:

```bash
node website/scripts/generate-social-cards.mjs
npm --prefix website run verify:social-cards
```

Expected: four valid 1200×630 images.

- [ ] **Step 3: Wire page metadata and remove the old asset**

Ensure each localized HTML points to its own PNG. Delete the old WebP only after:

```bash
rg -n "skills-social-card\.webp" website
```

returns no matches outside Git history. Extend built-output verification to require each locale mapping.

- [ ] **Step 4: Update maintenance documentation**

Document the four public routes, content files, locale verifier, generated static pages, ImageMagick card command, and full build. Update the structure table to distinguish invariant data from locale content.

- [ ] **Step 5: Run the full repository gate**

```bash
npm --prefix website run verify:catalog
npm --prefix website run verify:landing
npm --prefix website run verify:locales
npm --prefix website run verify:social-cards
npm --prefix website run typecheck
npm --prefix website run build
pytest -ra
git diff --check
```

Expected: all website checks and build pass; pytest reports no failures.

- [ ] **Step 6: Run rendered local QA**

Use `agent-browser` against `npm --prefix website run preview` and verify every locale at 320px, 390px, and 1440px in light and dark themes. Check one H1, exact locale copy, twenty catalog rows, localized search plus `$git` search, language disclosure keyboard behavior, current language, hash navigation, zero document overflow, zero console errors, and branded localized 404. Run Axe after opening the disclosure and after catalog search/filter/selection; record violations and incomplete items separately.

- [ ] **Step 7: Commit and push localized social delivery**

```bash
git add website/scripts/generate-social-cards.mjs website/scripts/verify-social-cards.mjs website/public/assets/skills-social-card-ko.png website/public/assets/skills-social-card-en.png website/public/assets/skills-social-card-jp.png website/public/assets/skills-social-card-cn.png website/scripts/verify-built-locales.mjs website/package.json website/README.md
git add -u website/public/assets/skills-social-card.webp
git commit -m "feat(site): localize social sharing assets"
git push origin main
git rev-list --left-right --count HEAD...@{upstream}
```

Expected parity: `0 0`.

- [ ] **Step 8: Verify GitHub Pages and final parity**

Wait for the Pages workflow triggered by the final commit. Confirm all four public URLs return successful localized HTML, metadata/FAQ schema and social-card URLs match local output, deployed social-card SHA-256 values match local assets, responsive/theme/keyboard/Axe representative checks pass, and the deployed commit equals local `HEAD`.

Finish with:

```bash
git fetch origin
git status --short --branch
git rev-list --left-right --count HEAD...@{upstream}
git ls-remote origin refs/heads/main
```

Expected: clean worktree, parity `0 0`, and one SHA for local/tracking/live `main`.
