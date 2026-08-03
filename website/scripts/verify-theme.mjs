import { readFile } from "node:fs/promises";
import path from "node:path";
import { fileURLToPath } from "node:url";

const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..");
const [toggleSource, htmlSource, stylesSource] = await Promise.all([
  readFile(path.join(root, "src", "components", "ThemeToggle.tsx"), "utf8"),
  readFile(path.join(root, "index.html"), "utf8"),
  readFile(path.join(root, "src", "styles.css"), "utf8"),
]);

for (const snippet of [
  'type Theme = "light" | "dark";',
  'window.matchMedia("(prefers-color-scheme: dark)")',
  "syncWithSystem();",
  'media.addEventListener("change", syncWithSystem)',
  'localStorage.setItem(themeStorageKey, next)',
  'theme === "dark" ? "light" : "dark"',
]) {
  if (!toggleSource.includes(snippet)) {
    throw new Error(`Theme toggle is missing ${snippet}.`);
  }
}

for (const snippet of [
  'savedTheme === "light" || savedTheme === "dark"',
  'window.matchMedia("(prefers-color-scheme: dark)").matches',
  "document.documentElement.dataset.theme = theme",
  'localStorage.removeItem("skills-theme")',
]) {
  if (!htmlSource.includes(snippet)) {
    throw new Error(`Initial theme script is missing ${snippet}.`);
  }
}

for (const [label, source, forbidden] of [
  ["theme toggle", toggleSource, ['type Theme = "system"', "Desktop"]],
  ["initial theme script", htmlSource, ['"dark", "light", "system"']],
  ["theme styles", stylesSource, ['data-theme="system"']],
]) {
  for (const snippet of forbidden) {
    if (source.includes(snippet)) throw new Error(`${label} still contains ${snippet}.`);
  }
}

if (/<html[^>]+data-theme=/.test(htmlSource)) {
  throw new Error("Initial HTML must resolve the theme before adding data-theme.");
}

const expectedThemeKeys = ["change", "dark", "light", "title"];
for (const locale of ["ko", "en", "jp", "cn"]) {
  const content = JSON.parse(
    await readFile(path.join(root, "src", "i18n", "content", `${locale}.json`), "utf8"),
  );
  const keys = Object.keys(content.theme ?? {}).sort();
  if (JSON.stringify(keys) !== JSON.stringify(expectedThemeKeys)) {
    throw new Error(`${locale}: theme keys must be ${expectedThemeKeys.join(", ")}.`);
  }
}

console.log("Binary light and dark theme persistence contract verified.");
