import { access, readFile, readdir } from "node:fs/promises";
import path from "node:path";
import { fileURLToPath } from "node:url";

const websiteRoot = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..");
const repositoryRoot = path.resolve(websiteRoot, "..");
const catalogPath = path.join(websiteRoot, "src", "data", "skills.ts");

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

function duplicates(values) {
  return values.filter((value, index) => values.indexOf(value) !== index);
}

const packaged = await packagedSkillNames();
const catalogSource = await readFile(catalogPath, "utf8");
if (!catalogSource.includes("export const skillDefinitions")) {
  throw new Error("Canonical catalog must export skillDefinitions.");
}
const catalog = catalogSkillNames(catalogSource);
const duplicatedCatalogIds = [...new Set(duplicates(catalog))];
const missingFromCatalog = packaged.filter((name) => !catalog.includes(name));
const missingFromPackages = catalog.filter((name) => !packaged.includes(name));

if (
  duplicatedCatalogIds.length ||
  missingFromCatalog.length ||
  missingFromPackages.length
) {
  const details = [
    duplicatedCatalogIds.length
      ? `Duplicate catalog ids: ${duplicatedCatalogIds.join(", ")}`
      : null,
    missingFromCatalog.length
      ? `Missing from catalog: ${missingFromCatalog.join(", ")}`
      : null,
    missingFromPackages.length
      ? `Missing from packages: ${missingFromPackages.join(", ")}`
      : null,
  ].filter(Boolean);

  throw new Error(details.join("\n"));
}

console.log(`Catalog matches ${packaged.length} packaged skills.`);
