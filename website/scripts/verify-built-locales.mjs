import { readFile } from "node:fs/promises";
import path from "node:path";
import { fileURLToPath } from "node:url";

const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..");
const dist = path.join(root, "dist");
const origin = "https://chann.github.io";
const locales = {
  ko: { path: "/skills/", output: "index.html", htmlLang: "ko", ogLocale: "ko_KR", socialCard: "skills-social-card-ko.png" },
  en: { path: "/skills/en/", output: "en/index.html", htmlLang: "en", ogLocale: "en_US", socialCard: "skills-social-card-en.png" },
  jp: { path: "/skills/jp/", output: "jp/index.html", htmlLang: "ja", ogLocale: "ja_JP", socialCard: "skills-social-card-jp.png" },
  cn: { path: "/skills/cn/", output: "cn/index.html", htmlLang: "zh-CN", ogLocale: "zh_CN", socialCard: "skills-social-card-cn.png" },
};
const alternates = [
  ["ko", `${origin}/skills/`],
  ["en", `${origin}/skills/en/`],
  ["ja", `${origin}/skills/jp/`],
  ["zh-CN", `${origin}/skills/cn/`],
  ["x-default", `${origin}/skills/`],
];

for (const [locale, descriptor] of Object.entries(locales)) {
  const html = await readFile(path.join(dist, descriptor.output), "utf8");
  const content = JSON.parse(
    await readFile(path.join(root, "src", "i18n", "content", `${locale}.json`), "utf8"),
  );
  const canonical = `${origin}${descriptor.path}`;
  const socialImage = `${origin}/skills/assets/${descriptor.socialCard}`;
  const required = [
    `<html lang="${descriptor.htmlLang}" data-locale="${locale}"`,
    `<link rel="canonical" href="${canonical}" />`,
    `<meta property="og:locale" content="${descriptor.ogLocale}" />`,
    `<meta property="og:url" content="${canonical}" />`,
    `<meta property="og:image" content="${socialImage}" />`,
    `<meta name="twitter:image" content="${socialImage}" />`,
    `<title>${content.meta.title.replaceAll("&", "&amp;").replaceAll('"', "&quot;").replaceAll("<", "&lt;").replaceAll(">", "&gt;")}</title>`,
  ];
  for (const snippet of required) {
    if (!html.includes(snippet)) throw new Error(`${locale}: missing ${snippet}`);
  }
  for (const [hreflang, href] of alternates) {
    const alternate = `<link rel="alternate" hreflang="${hreflang}" href="${href}" />`;
    if (!html.includes(alternate)) throw new Error(`${locale}: missing ${alternate}`);
  }

  const schemaText = html.match(
    /<script type="application\/ld\+json" id="faq-schema">([\s\S]*?)<\/script>/,
  )?.[1];
  if (!schemaText) throw new Error(`${locale}: missing FAQ schema.`);
  const schema = JSON.parse(schemaText);
  if (schema.mainEntity?.length !== 10) {
    throw new Error(`${locale}: expected 10 FAQ schema entries.`);
  }
  if (/__LOCALE_|__LANG_|__META_/.test(html)) {
    throw new Error(`${locale}: generator sentinel remains in output.`);
  }
}

console.log("Built locale pages verified for ko, en, jp, cn.");
