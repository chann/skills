import { readFile } from "node:fs/promises";
import path from "node:path";
import { fileURLToPath } from "node:url";

const websiteRoot = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..");
const sources = {
  app: await readFile(path.join(websiteRoot, "src", "App.tsx"), "utf8"),
  githubMark: await readFile(
    path.join(websiteRoot, "src", "components", "GitHubMark.tsx"),
    "utf8",
  ),
  metadata: await readFile(path.join(websiteRoot, "index.html"), "utf8"),
  notFound: await readFile(path.join(websiteRoot, "public", "404.html"), "utf8"),
};

const required = {
  app: [
    'const repositoryName = "chann/skills";',
    "<span>{repositoryName} / workspace</span>",
    '<p className="hero__brand">{repositoryName}</p>',
    'repositoryName.split("")',
    "<GitHubMark size={18} />",
  ],
  githubMark: [
    'viewBox="0 0 24 24"',
    'fill="currentColor"',
    "M10.226 17.284c-2.965-.36-5.054-2.493-5.054-5.256",
  ],
  metadata: [
    '<meta property="og:site_name" content="chann/skills" />',
    '<meta property="og:title" content="chann/skills - 어제의 반복이, 오늘의 스킬로" />',
    '<meta name="twitter:title" content="chann/skills - 어제의 반복이, 오늘의 스킬로" />',
    '<title>chann/skills - 어제의 반복이, 오늘의 스킬로</title>',
  ],
  notFound: [
    '<title>404 - chann/skills</title>',
    '<span class="kicker">chann/skills · 404</span>',
  ],
};

for (const [surface, snippets] of Object.entries(required)) {
  for (const snippet of snippets) {
    if (!sources[surface].includes(snippet)) {
      throw new Error(`Missing chann/skills branding in ${surface}: ${snippet}`);
    }
  }
}

if (sources.app.includes("GithubLogo")) {
  throw new Error("Phosphor GithubLogo must not replace the official GitHub Mark.");
}

const repeatedAppBranding = {
  'aria-label={`${repositoryName} 홈`}': 2,
  "<span>{repositoryName}</span>": 2,
};

for (const [snippet, expectedCount] of Object.entries(repeatedAppBranding)) {
  const actualCount = sources.app.split(snippet).length - 1;
  if (actualCount !== expectedCount) {
    throw new Error(
      `Expected ${expectedCount} app occurrences of ${snippet}, found ${actualCount}`,
    );
  }
}

console.log("chann/skills branding verified across app, metadata, and 404.");
