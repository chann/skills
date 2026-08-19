import { access, readFile, readdir } from "node:fs/promises";
import path from "node:path";
import { fileURLToPath } from "node:url";

const websiteRoot = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..");
const repositoryRoot = path.resolve(websiteRoot, "..");
const catalogPath = path.join(websiteRoot, "src", "data", "skills.ts");
const expectedWorkflowCount = 28;
const expectedSelectorCount = 29;
const requiredPlanSummaryIds = [
  "plan-summary",
  "plan-summary-md",
  "plan-summary-quiz",
];

async function exists(target) {
  try {
    await access(target);
    return true;
  } catch {
    return false;
  }
}

async function packagedSkillNames() {
  const names = [];
  const repositoryEntries = await readdir(repositoryRoot, {
    withFileTypes: true,
  });

  for (const entry of repositoryEntries) {
    if (!entry.isDirectory() || entry.name.startsWith(".") || entry.name === "website") {
      continue;
    }

    const skillsDirectory = path.join(repositoryRoot, entry.name, "skills");
    if (!(await exists(skillsDirectory))) continue;

    const skillEntries = await readdir(skillsDirectory, { withFileTypes: true });
    for (const skillEntry of skillEntries) {
      if (!skillEntry.isDirectory()) continue;

      const skillPath = path.join(
        skillsDirectory,
        skillEntry.name,
        "SKILL.md",
      );
      if (!(await exists(skillPath))) continue;

      const skillSource = await readFile(skillPath, "utf8");
      const frontmatterName = skillSource.match(/^name:\s*(.+)\s*$/m)?.[1];
      if (!frontmatterName) {
        throw new Error(`Missing frontmatter name: ${skillPath}`);
      }
      names.push(frontmatterName.trim());
    }
  }

  return names.sort();
}

function catalogSkillNames(source) {
  return [...source.matchAll(/^\s*id:\s*"([^"]+)",\s*$/gm)]
    .map((match) => match[1])
    .sort();
}

function catalogAliasTokens(source) {
  return [...source.matchAll(/^\s*aliases:\s*\[([^\]]*)\],\s*$/gm)]
    .flatMap((match) => [...match[1].matchAll(/"([/$][^"]+)"/g)])
    .map((match) => match[1]);
}

function duplicates(values) {
  return values.filter((value, index) => values.indexOf(value) !== index);
}

const packaged = await packagedSkillNames();
const catalogSource = await readFile(catalogPath, "utf8");
if (!catalogSource.includes("export const skillDefinitions")) {
  throw new Error("Canonical catalog must export skillDefinitions.");
}
const catalog = catalogSkillNames(catalogSource);
const aliasTokens = catalogAliasTokens(catalogSource);
const aliasNames = [...new Set(aliasTokens.map((alias) => alias.slice(1)))];
const duplicatedCatalogIds = [...new Set(duplicates(catalog))];
const duplicatedAliasTokens = [...new Set(duplicates(aliasTokens))];
const collidingAliasNames = aliasNames.filter((name) => catalog.includes(name));
const represented = new Set([...catalog, ...aliasNames]);
const missingFromCatalog = packaged.filter((name) => !represented.has(name));
const missingFromPackages = catalog.filter((name) => !packaged.includes(name));
const missingPlanSummaryIds = requiredPlanSummaryIds.filter(
  (name) => !catalog.includes(name),
);

if (
  duplicatedCatalogIds.length ||
  duplicatedAliasTokens.length ||
  collidingAliasNames.length ||
  missingFromCatalog.length ||
  missingFromPackages.length ||
  missingPlanSummaryIds.length ||
  catalog.length !== expectedWorkflowCount ||
  packaged.length !== expectedSelectorCount
) {
  const details = [
    duplicatedCatalogIds.length
      ? `Duplicate catalog ids: ${duplicatedCatalogIds.join(", ")}`
      : null,
    duplicatedAliasTokens.length
      ? `Duplicate catalog aliases: ${duplicatedAliasTokens.join(", ")}`
      : null,
    collidingAliasNames.length
      ? `Catalog aliases collide with canonical ids: ${collidingAliasNames.join(", ")}`
      : null,
    missingFromCatalog.length
      ? `Missing from catalog: ${missingFromCatalog.join(", ")}`
      : null,
    missingFromPackages.length
      ? `Missing from packages: ${missingFromPackages.join(", ")}`
      : null,
    missingPlanSummaryIds.length
      ? `Missing plan-summary workflows: ${missingPlanSummaryIds.join(", ")}`
      : null,
    catalog.length !== expectedWorkflowCount
      ? `Expected ${expectedWorkflowCount} workflows, found ${catalog.length}`
      : null,
    packaged.length !== expectedSelectorCount
      ? `Expected ${expectedSelectorCount} packaged selectors, found ${packaged.length}`
      : null,
  ].filter(Boolean);

  throw new Error(details.join("\n"));
}

console.log(
  `Catalog matches ${catalog.length} workflows and ${packaged.length} packaged selectors.`,
);
