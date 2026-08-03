import type { Locale } from "./types";

export const defaultLocale: Locale = "ko";

export const localeRegistry = {
  ko: {
    code: "KO",
    path: "/skills/",
    htmlLang: "ko",
    ogLocale: "ko_KR",
    label: "한국어 (KO)",
    socialCard: "skills-social-card-ko.png",
  },
  en: {
    code: "EN",
    path: "/skills/en/",
    htmlLang: "en",
    ogLocale: "en_US",
    label: "English (EN)",
    socialCard: "skills-social-card-en.png",
  },
  jp: {
    code: "JP",
    path: "/skills/jp/",
    htmlLang: "ja",
    ogLocale: "ja_JP",
    label: "日本語 (JP)",
    socialCard: "skills-social-card-jp.png",
  },
  cn: {
    code: "CN",
    path: "/skills/cn/",
    htmlLang: "zh-CN",
    ogLocale: "zh_CN",
    label: "简体中文 (CN)",
    socialCard: "skills-social-card-cn.png",
  },
} as const;

export const supportedSectionHashes = new Set([
  "#main",
  "#why",
  "#usage",
  "#explore",
  "#faq",
  "#install",
]);

export function localeHref(locale: Locale, hash: string): string {
  return `${localeRegistry[locale].path}${supportedSectionHashes.has(hash) ? hash : ""}`;
}

export function isLocale(value: string | undefined): value is Locale {
  return value === "ko" || value === "en" || value === "jp" || value === "cn";
}

export function resolveDocumentLocale(): Locale {
  const locale = document.documentElement.dataset.locale;
  return isLocale(locale) ? locale : defaultLocale;
}
