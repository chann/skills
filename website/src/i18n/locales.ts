import type { Locale } from "./types";

export const defaultLocale: Locale = "ko";

export function isLocale(value: string | undefined): value is Locale {
  return value === "ko" || value === "en" || value === "jp" || value === "cn";
}

export function resolveDocumentLocale(): Locale {
  const locale = document.documentElement.dataset.locale;
  return isLocale(locale) ? locale : defaultLocale;
}
