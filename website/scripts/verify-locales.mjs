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

if (canonicalIds.length !== 20 || new Set(canonicalIds).size !== 20) {
  throw new Error(`Expected 20 unique canonical skill IDs, found ${canonicalIds.length}.`);
}

const localizedContent = Object.fromEntries(
  await Promise.all(
    requiredLocales.map(async (locale) => {
      const file = path.join(root, "src", "i18n", "content", `${locale}.json`);
      return [locale, JSON.parse(await readFile(file, "utf8"))];
    }),
  ),
);
const koreanKeyPaths = keyPaths(localizedContent.ko).sort();

for (const locale of requiredLocales) {
  const content = localizedContent[locale];
  requireNonEmptyStrings(content, locale);

  const localeKeyPaths = keyPaths(content).sort();
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
  if (localizedIds.length !== 20 || missing.length || extra.length) {
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

console.log(`Localized content verified for ${requiredLocales.join(", ")}.`);
