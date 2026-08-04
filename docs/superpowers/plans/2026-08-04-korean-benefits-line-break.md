# Korean Benefits Line Break Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Render the Korean benefits heading as the exact three requested lines while preserving every other locale's existing composition.

**Architecture:** Treat localized title arrays as the source of explicit visual lines and render every item generically inside one semantic `h2`. Pin the Korean three-line contract in the existing Node verification scripts and confirm responsive behavior in a browser.

**Tech Stack:** React 19, TypeScript, CSS, JSON localization, Vite, Node verification scripts.

## Global Constraints

- The Korean lines are exactly `반복할수록,`, `덜 설명하고`, and `더 선명하게.` in that order.
- English, Japanese, and Chinese title content remains unchanged.
- The heading remains one semantic `h2`.
- Existing `word-break: keep-all`, themes, and responsive layout remain supported.

---

### Task 1: Pin locale-specific heading lines

**Files:**
- Modify: `website/scripts/verify-landing-message.mjs`
- Modify: `website/scripts/verify-locales.mjs`

**Interfaces:**
- Consumes: `content.benefits.title: string[]` from each locale JSON file.
- Produces: exact Korean line-order assertion and locale-specific title-length validation.

- [ ] **Step 1: Write the failing landing contract**

Add:

```js
const expectedBenefitsTitle = ["반복할수록,", "덜 설명하고", "더 선명하게."];
if (JSON.stringify(content.benefits.title) !== JSON.stringify(expectedBenefitsTitle)) {
  throw new Error("Korean benefits title must use the approved three-line composition.");
}
```

In locale verification, assert Korean has three benefit-title items and every other locale has two, without requiring locale arrays to expose identical indexed key paths.

- [ ] **Step 2: Run the checks and confirm the intended failure**

Run:

```bash
npm --prefix website run verify:landing
npm --prefix website run verify:locales
```

Expected: both checks fail because Korean still has two title entries.

### Task 2: Render any localized title length

**Files:**
- Modify: `website/src/i18n/content/ko.json`
- Modify: `website/src/App.tsx`
- Modify: `website/src/styles.css`

**Interfaces:**
- Consumes: `content.benefits.title: string[]`.
- Produces: one `h2` containing one block-level span per localized line.

- [ ] **Step 1: Split the Korean title into three values**

Use:

```json
"title": ["반복할수록,", "덜 설명하고", "더 선명하게."]
```

- [ ] **Step 2: Replace fixed indexes with array rendering**

Use:

```tsx
<h2 id="efficiency-title">
  {content.benefits.title.map((line) => <span key={line}>{line}</span>)}
</h2>
```

- [ ] **Step 3: Preserve explicit visual lines in CSS**

Add:

```css
.efficiency-intro h2 span {
  display: block;
}
```

- [ ] **Step 4: Run narrow and production checks**

Run:

```bash
npm --prefix website run verify:landing
npm --prefix website run verify:locales
npm --prefix website run typecheck
npm --prefix website run build
git diff --check
```

Expected: all commands pass.

### Task 3: Verify responsive rendering and publish the outcome

**Files:**
- Verify only: built website served from `website/dist/`

**Interfaces:**
- Consumes: production build.
- Produces: browser evidence for exact lines at narrow/wide widths and unchanged non-Korean locale headings.

- [ ] **Step 1: Inspect Korean at desktop and mobile widths**

Serve the built site and inspect at approximately 1440 px and 390 px. Confirm the `h2` has one accessible heading and three visual spans with exact text, with no overflow or unintended fourth line.

- [ ] **Step 2: Inspect other locales**

Open `/en/`, `/jp/`, and `/cn/`; confirm each benefits heading retains its original two explicit lines and does not overflow at the same widths.

- [ ] **Step 3: Commit and push the verified website outcome**

Stage only the line-break implementation, tests, and these two plan documents. Commit:

```bash
git commit -m "fix(site): set Korean benefits heading lines"
git push
```

Verify `git rev-list --left-right --count HEAD...@{u}` returns `0 0` and the working tree is clean.
