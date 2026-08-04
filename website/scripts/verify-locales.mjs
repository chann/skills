import { readFile } from "node:fs/promises";
import path from "node:path";
import { fileURLToPath } from "node:url";

const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..");
const requiredLocales = ["ko", "en", "jp", "cn"];
const requiredSkillFields = ["summary", "whenToUse", "result"];

function keyPaths(value, prefix = "") {
  if (Array.isArray(value)) {
    return value.flatMap((item, index) => keyPaths(item, `${prefix}[${index}]`));
  }
  if (value && typeof value === "object") {
    return Object.entries(value).flatMap(([key, item]) =>
      keyPaths(item, prefix ? `${prefix}.${key}` : key),
    );
  }
  return [prefix];
}

function requireNonEmptyStrings(value, locale) {
  for (const key of keyPaths(value)) {
    const item = key
      .replace(/\[(\d+)\]/g, ".$1")
      .split(".")
      .reduce((current, segment) => current?.[segment], value);
    if (typeof item === "string" && item.trim() === "") {
      throw new Error(`${locale}: empty localized string at ${key}`);
    }
  }
}

const skillsSource = await readFile(path.join(root, "src", "data", "skills.ts"), "utf8");
const canonicalIds = [...skillsSource.matchAll(/^\s+id: "([^"]+)",$/gm)].map(
  (match) => match[1],
);

if (canonicalIds.length !== 23 || new Set(canonicalIds).size !== 23) {
  throw new Error(`Expected 23 unique canonical skill IDs, found ${canonicalIds.length}.`);
}

const localizedContent = Object.fromEntries(
  await Promise.all(
    requiredLocales.map(async (locale) => {
      const file = path.join(root, "src", "i18n", "content", `${locale}.json`);
      return [locale, JSON.parse(await readFile(file, "utf8"))];
    }),
  ),
);
const localeShapePaths = (content) =>
  keyPaths(content)
    .filter((key) => !/^benefits\.title\[\d+\]$/.test(key))
    .sort();
const koreanKeyPaths = localeShapePaths(localizedContent.ko);

for (const locale of requiredLocales) {
  const content = localizedContent[locale];
  requireNonEmptyStrings(content, locale);

  const localeKeyPaths = localeShapePaths(content);
  if (JSON.stringify(localeKeyPaths) !== JSON.stringify(koreanKeyPaths)) {
    const missing = koreanKeyPaths.filter((key) => !localeKeyPaths.includes(key));
    const extra = localeKeyPaths.filter((key) => !koreanKeyPaths.includes(key));
    throw new Error(
      `${locale}: locale keys differ (missing: ${missing.join(", ") || "none"}; extra: ${extra.join(", ") || "none"}).`,
    );
  }

  if (locale !== "ko" && /[가-힣]/.test(JSON.stringify(content))) {
    throw new Error(`${locale}: untranslated Korean text remains.`);
  }

  const localizedIds = Object.keys(content.skills ?? {});
  const missing = canonicalIds.filter((id) => !localizedIds.includes(id));
  const extra = localizedIds.filter((id) => !canonicalIds.includes(id));
  if (localizedIds.length !== 23 || missing.length || extra.length) {
    throw new Error(
      `${locale}: skill IDs differ (missing: ${missing.join(", ") || "none"}; extra: ${extra.join(", ") || "none"}).`,
    );
  }

  for (const id of canonicalIds) {
    for (const field of requiredSkillFields) {
      if (typeof content.skills[id]?.[field] !== "string" || !content.skills[id][field].trim()) {
        throw new Error(`${locale}: ${id}.${field} must be a non-empty string.`);
      }
    }
  }

  const expectedLengths = [
    ["hero.headline", content.hero?.headline, 2],
    ["benefits.title", content.benefits?.title, locale === "ko" ? 3 : 2],
    ["benefits.items", content.benefits?.items, 3],
    ["tagline.lines", content.tagline?.lines, 2],
    ["workflow.steps", content.workflow?.steps, 3],
    ["productPreview.proof", content.productPreview?.proof, 3],
    ["faq.items", content.faq?.items, 10],
  ];
  for (const [field, items, length] of expectedLengths) {
    if (!Array.isArray(items) || items.length !== length) {
      throw new Error(`${locale}: ${field} must contain exactly ${length} items.`);
    }
  }
}

const switcherSource = await readFile(
  path.join(root, "src", "components", "LanguageSwitcher.tsx"),
  "utf8",
);
for (const snippet of [
  "aria-expanded",
  "aria-controls",
  "aria-current",
  'event.key !== "Escape"',
  "triggerRef.current?.focus()",
  "localeHref(targetLocale, hash)",
]) {
  if (!switcherSource.includes(snippet)) {
    throw new Error(`Language switcher is missing ${snippet}.`);
  }
}

const localeSource = await readFile(path.join(root, "src", "i18n", "locales.ts"), "utf8");
for (const label of ["한국어 (KO)", "English (EN)", "日本語 (JP)", "简体中文 (CN)"]) {
  if (!localeSource.includes(label)) throw new Error(`Locale registry is missing ${label}.`);
}

const notFoundSource = await readFile(path.join(root, "public", "404.html"), "utf8");
for (const locale of requiredLocales) {
  if (!notFoundSource.includes(`${locale}: {`)) {
    throw new Error(`404 page is missing the ${locale} dictionary.`);
  }
}
for (const forbidden of ["location.replace", "location.assign", "location.href ="]) {
  if (notFoundSource.includes(forbidden)) {
    throw new Error(`404 page must not redirect with ${forbidden}.`);
  }
}

console.log(`Localized content verified for ${requiredLocales.join(", ")}.`);
