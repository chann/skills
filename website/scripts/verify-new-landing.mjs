import { readdir, readFile } from "node:fs/promises";
import path from "node:path";
import { fileURLToPath } from "node:url";

const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..");
const repository = path.resolve(root, "..");
const read = (...segments) => readFile(path.join(root, ...segments), "utf8");

const [data, app, skills, html, mainHtml] = await Promise.all([
  read("src", "new", "data.ts"),
  read("src", "new", "NewApp.tsx"),
  read("src", "data", "skills.ts"),
  read("new", "index.html"),
  read("index.html"),
]);

// The page prints the playbook count, so it has to match the files that ship.
const playbooks = (
  await readdir(path.join(repository, "chann-mode", "skills", "chann", "playbooks"))
).filter((name) => name.endsWith(".md"));
const declared = Number(data.match(/export const playbookCount = (\d+);/)?.[1]);
if (declared !== playbooks.length) {
  throw new Error(`playbookCount is ${declared}, but ${playbooks.length} playbooks ship.`);
}

// Every skill and playbook the page names must exist.
const skillIds = new Set([...skills.matchAll(/^\s+id: "([^"]+)",$/gm)].map((match) => match[1]));
const playbookNames = new Set(playbooks.map((name) => name.replace(/\.md$/, "")));
const block = (name) => data.match(new RegExp(`export const ${name}[^=]*=\\s*\\[([\\s\\S]*?)\\n\\];`))?.[1] ?? "";
const quoted = (text) => [...text.matchAll(/"([a-z][a-z-]*)"/g)].map((match) => match[1]);
const categories = new Set(quoted(skills.match(/export const categoryOrder = \[([\s\S]*?)\]/)?.[1] ?? ""));

for (const name of ["lifecycleCommands", "featuredSkills"]) {
  const ids = quoted(block(name));
  if (ids.length === 0) throw new Error(`${name} is empty.`);
  for (const id of ids) {
    if (!skillIds.has(id)) throw new Error(`${name} names an unknown skill: ${id}`);
  }
}
for (const id of quoted(block("lifecyclePhases"))) {
  if (!skillIds.has(id) && !categories.has(id)) {
    throw new Error(`lifecyclePhases names an unknown skill or category: ${id}`);
  }
}
const groups = quoted(block("routerGroups"));
if (groups.length === 0) throw new Error("routerGroups is empty.");
for (const name of groups) {
  if (!playbookNames.has(name)) throw new Error(`routerGroups names an unknown playbook: ${name}`);
}

// Copy arrays are indexed by the data arrays above.
for (const locale of ["ko", "en", "jp", "cn"]) {
  const { landing } = JSON.parse(await read("src", "i18n", "content", `${locale}.json`));
  const expected = [
    ["lifecycle.commands", landing.lifecycle.commands, quoted(block("lifecycleCommands")).length],
    ["why.items", landing.why.items, 4],
    ["router.groups", landing.router.groups, 4],
  ];
  for (const [field, items, length] of expected) {
    if (!Array.isArray(items) || items.length !== length) {
      throw new Error(`${locale}: landing.${field} must contain exactly ${length} items.`);
    }
  }
}

const hero = app.match(/<section className="n-hero"[\s\S]*?<\/section>/)?.[0] ?? "";
if ((hero.match(/n-button--primary/g) ?? []).length !== 1) {
  throw new Error("The new hero must contain exactly one primary action.");
}
for (const snippet of ['<LanguageSwitcher locale={locale} labels={content.language} preview />', 'id="install"']) {
  if (!app.includes(snippet)) throw new Error(`NewApp is missing ${snippet}`);
}

// The preview keeps the main page's metadata and stays out of search results.
if (!html.includes('<meta name="robots" content="noindex" />')) {
  throw new Error("new/index.html must be noindex while it is a preview.");
}
if (!html.includes('<script type="module" src="/src/new/main.tsx"></script>')) {
  throw new Error("new/index.html must load the new entry.");
}
const withoutPreviewLines = html
  .replace('    <meta name="robots" content="noindex" />\n', "")
  .replace("/src/new/main.tsx", "/src/main.tsx");
if (withoutPreviewLines !== mainHtml) {
  throw new Error("new/index.html must match index.html apart from noindex and its entry script.");
}

console.log(`New landing page verified: ${declared} playbooks, ${skillIds.size} skills.`);
