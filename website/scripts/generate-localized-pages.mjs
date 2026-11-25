import { mkdir, readFile, writeFile } from "node:fs/promises";
import path from "node:path";
import { fileURLToPath } from "node:url";

const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..");
const dist = path.join(root, "dist");
const origin = "https://chann.github.io";
const locales = {
  ko: {
    path: "/skills/",
    output: "index.html",
    htmlLang: "ko",
    ogLocale: "ko_KR",
    socialCard: "skills-social-card-ko.png",
  },
  en: {
    path: "/skills/en/",
    output: "en/index.html",
    htmlLang: "en",
    ogLocale: "en_US",
    socialCard: "skills-social-card-en.png",
  },
  jp: {
    path: "/skills/jp/",
    output: "jp/index.html",
    htmlLang: "ja",
    ogLocale: "ja_JP",
    socialCard: "skills-social-card-jp.png",
  },
  cn: {
    path: "/skills/cn/",
    output: "cn/index.html",
    htmlLang: "zh-CN",
    ogLocale: "zh_CN",
    socialCard: "skills-social-card-cn.png",
  },
};

function escapeHtml(value) {
  return value
    .replaceAll("&", "&amp;")
    .replaceAll('"', "&quot;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;");
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

function replaceExactlyOnce(source, pattern, replacement, label) {
  const matches = source.match(pattern) ?? [];
  if (matches.length !== 1) {
    throw new Error(`${label}: expected one match, found ${matches.length}.`);
  }
  return source.replace(pattern, replacement);
}

const shell = await readFile(path.join(dist, "index.html"), "utf8");

for (const [locale, descriptor] of Object.entries(locales)) {
  const content = JSON.parse(
    await readFile(path.join(root, "src", "i18n", "content", `${locale}.json`), "utf8"),
  );
  const canonical = `${origin}${descriptor.path}`;
  const socialImage = `${origin}/skills/assets/${descriptor.socialCard}`;
  let html = shell;

  const replacements = [
    [/<html lang="[^"]+" data-locale="[^"]+"/g, `<html lang="${descriptor.htmlLang}" data-locale="${locale}"`, "html locale"],
    [/<link rel="canonical" href="[^"]+"\s*\/?>/g, `<link rel="canonical" href="${canonical}" />`, "canonical"],
    [/<meta\s+name="description"\s+content="[^"]*"\s*\/?>/g, `<meta name="description" content="${escapeHtml(content.meta.description)}" />`, "description"],
    [/<meta\s+property="og:locale"\s+content="[^"]*"\s*\/?>/g, `<meta property="og:locale" content="${descriptor.ogLocale}" />`, "Open Graph locale"],
    [/<meta\s+property="og:title"\s+content="[^"]*"\s*\/?>/g, `<meta property="og:title" content="${escapeHtml(content.meta.title)}" />`, "Open Graph title"],
    [/<meta\s+property="og:description"\s+content="[^"]*"\s*\/?>/g, `<meta property="og:description" content="${escapeHtml(content.meta.description)}" />`, "Open Graph description"],
    [/<meta\s+property="og:url"\s+content="[^"]*"\s*\/?>/g, `<meta property="og:url" content="${canonical}" />`, "Open Graph URL"],
    [/<meta\s+property="og:image"\s+content="[^"]*"\s*\/?>/g, `<meta property="og:image" content="${socialImage}" />`, "Open Graph image"],
    [/<meta\s+property="og:image:alt"\s+content="[^"]*"\s*\/?>/g, `<meta property="og:image:alt" content="${escapeHtml(content.meta.socialAlt)}" />`, "Open Graph image alt"],
    [/<meta\s+name="twitter:title"\s+content="[^"]*"\s*\/?>/g, `<meta name="twitter:title" content="${escapeHtml(content.meta.title)}" />`, "Twitter title"],
    [/<meta\s+name="twitter:description"\s+content="[^"]*"\s*\/?>/g, `<meta name="twitter:description" content="${escapeHtml(content.meta.description)}" />`, "Twitter description"],
    [/<meta\s+name="twitter:image"\s+content="[^"]*"\s*\/?>/g, `<meta name="twitter:image" content="${socialImage}" />`, "Twitter image"],
    [/<title>[\s\S]*?<\/title>/g, `<title>${escapeHtml(content.meta.title)}</title>`, "title"],
    [/<script type="application\/ld\+json" id="faq-schema">[\s\S]*?<\/script>/g, `<script type="application/ld+json" id="faq-schema">${faqSchema(content.faq.items)}</script>`, "FAQ schema"],
  ];

  for (const [pattern, replacement, label] of replacements) {
    html = replaceExactlyOnce(html, pattern, replacement, `${locale} ${label}`);
  }

  const output = path.join(dist, descriptor.output);
  await mkdir(path.dirname(output), { recursive: true });
  await writeFile(output, html);
}

console.log("Generated localized pages for ko, en, jp, cn.");
