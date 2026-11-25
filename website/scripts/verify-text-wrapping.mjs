import { readFile } from "node:fs/promises";
import path from "node:path";
import { fileURLToPath } from "node:url";

const websiteRoot = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..");
const targets = [
  path.join(websiteRoot, "src", "styles.css"),
  path.join(websiteRoot, "public", "404.html"),
];

for (const target of targets) {
  const source = await readFile(target, "utf8");
  const bodyRule = source.match(/(?:^|})\s*body\s*\{([^}]*)\}/m)?.[1];

  if (!bodyRule) {
    throw new Error(`Missing global body rule: ${target}`);
  }

  for (const declaration of [
    "word-break: keep-all",
    "overflow-wrap: break-word",
  ]) {
    if (!bodyRule.includes(declaration)) {
      throw new Error(`Missing ${declaration} in global body rule: ${target}`);
    }
  }
}

console.log(`Global text wrapping verified in ${targets.length} stylesheets.`);
