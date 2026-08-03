import { skillDefinitions, type SkillDefinition, type SkillId } from "../data/skills";
import koJson from "./content/ko.json";
import type { Locale, SiteContent, SkillCopy } from "./types";

const ko: SiteContent = koJson;

export const contentByLocale = { ko } as const;

export type LocalizedSkill = SkillDefinition & SkillCopy;

export function getContent(locale: Locale): SiteContent {
  return contentByLocale[locale as keyof typeof contentByLocale] ?? ko;
}

export function formatMessage(
  template: string,
  values: Record<string, string | number>,
): string {
  return template.replace(/\{(\w+)\}/g, (_, key: string) =>
    String(values[key] ?? `{${key}}`),
  );
}

export function getLocalizedSkills(locale: Locale): LocalizedSkill[] {
  const copy = getContent(locale).skills as Record<SkillId, SkillCopy>;
  return skillDefinitions.map((definition) => ({ ...definition, ...copy[definition.id] }));
}
