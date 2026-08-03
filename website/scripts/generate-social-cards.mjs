import { execFileSync, spawn } from "node:child_process";
import { mkdir } from "node:fs/promises";
import path from "node:path";
import { fileURLToPath } from "node:url";

const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..");
const outputDirectory = path.join(root, "public", "assets");
const cards = [
  { locale: "ko", lang: "ko", font: "Apple SD Gothic Neo", lines: ["어제의 반복이,", "오늘의 스킬로."] },
  { locale: "en", lang: "en", font: "Arial", lines: ["Yesterday’s repetition", "becomes today’s skill."] },
  { locale: "jp", lang: "ja", font: "Hiragino Sans", lines: ["昨日の繰り返しを、", "今日のスキルへ。"] },
  { locale: "cn", lang: "zh-CN", font: "PingFang SC", lines: ["把昨天的重复，", "变成今天的技能。"] },
];

function escapeXml(value) {
  return value
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;");
}

function svgFor(card) {
  const [first, second] = card.lines.map(escapeXml);
  return `<svg xmlns="http://www.w3.org/2000/svg" width="1200" height="630" viewBox="0 0 1200 630" lang="${card.lang}">
    <rect width="1200" height="630" fill="#000000"/>
    <rect x="72" y="64" width="1056" height="502" rx="24" fill="#181818"/>
    <rect x="72" y="64" width="8" height="502" fill="#0044ff"/>
    <text x="128" y="148" fill="#85a2ff" font-size="30" font-weight="650">chann/skills</text>
    <text x="128" y="306" fill="#f7f8ff" font-size="70" font-weight="700">${first}</text>
    <text x="128" y="390" fill="#f7f8ff" font-size="70" font-weight="700">${second}</text>
    <text x="128" y="500" fill="#b4bad0" font-size="26">20 packaged skills · Claude Code + Codex · MIT</text>
  </svg>`;
}

function resolveFont(family) {
  try {
    const font = execFileSync("fc-match", ["-f", "%{file}", family], {
      encoding: "utf8",
    }).trim();
    if (font) return font;
  } catch {
    // The explicit error below explains the required local dependency.
  }
  throw new Error(`A local font matching '${family}' is required to regenerate social cards.`);
}

function render(svg, font, output) {
  return new Promise((resolve, reject) => {
    const child = spawn("magick", ["-font", font, "svg:-", output], {
      stdio: ["pipe", "inherit", "inherit"],
    });
    child.on("error", () =>
      reject(new Error("ImageMagick 'magick' is required to regenerate social cards.")),
    );
    child.on("exit", (code) =>
      code === 0
        ? resolve()
        : reject(new Error(`magick exited with ${code}`)),
    );
    child.stdin.end(svg);
  });
}

await mkdir(outputDirectory, { recursive: true });
for (const card of cards) {
  await render(
    svgFor(card),
    resolveFont(card.font),
    path.join(outputDirectory, `skills-social-card-${card.locale}.png`),
  );
}

console.log("Generated localized social cards for ko, en, jp, cn.");
