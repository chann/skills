import type { SkillCategory, SkillId } from "../data/skills";

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
  label: string;
  title: string[];
  description: string;
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
  repositoryStats: string;
  installResults: string;
}

export interface SiteContent {
  meta: MetadataContent;
  nav: {
    label: string;
    items: Record<"why" | "explore" | "faq" | "install", string>;
  };
  hero: {
    brand: string;
    headline: string[];
    lede: string;
    primaryAction: string;
    proof: string;
  };
  benefits: {
    label: string;
    title: string[];
    description: string;
    items: Array<{ label: string; title: string; description: string }>;
  };
  tagline: {
    label: string;
    lines: string[];
    stats: Record<"skills" | "categories" | "platforms", string>;
  };
  workflow: {
    label: string;
    title: string[];
    description: string;
    steps: Array<{
      number: string;
      label: string;
      title: string;
      description: string;
    }>;
    status: string;
    artifact: string;
  };
  catalog: CatalogContent;
  platforms: PlatformContent;
  faq: {
    label: string;
    title: string;
    description: string;
    items: Array<{ question: string; answer: string }>;
  };
  install: InstallContent;
  footer: { tagline: string; license: string; github: string };
  productPreview: ProductPreviewContent;
  copy: { idle: string; copied: string; error: string };
  theme: { light: string; dark: string; change: string; title: string };
  language: { trigger: string; navigation: string };
  accessibility: AccessibilityContent;
  categories: Record<SkillCategory, { label: string; description: string }>;
  skills: Record<SkillId, SkillCopy>;
  notFound: { title: string; description: string; home: string; navigation: string };
}
