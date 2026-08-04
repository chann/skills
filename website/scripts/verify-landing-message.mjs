import { readFile } from "node:fs/promises";
import path from "node:path";
import { fileURLToPath } from "node:url";

const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..");
const app = await readFile(path.join(root, "src", "App.tsx"), "utf8");
const html = await readFile(path.join(root, "index.html"), "utf8");
const content = JSON.parse(
  await readFile(path.join(root, "src", "i18n", "content", "ko.json"), "utf8"),
);
const localizedCopy = JSON.stringify(content);
const expectedBenefitsTitle = ["반복할수록,", "덜 설명하고", "더 선명하게."];

if (JSON.stringify(content.benefits.title) !== JSON.stringify(expectedBenefitsTitle)) {
  throw new Error("Korean benefits title must use the approved three-line composition.");
}

for (const text of [
  "어제의 반복이,",
  "오늘의 스킬로.",
  "같은 지침을 다시 만들지 않습니다.",
  "정해진 일은 스크립트가 처리합니다.",
  "LLM은 판단에 집중합니다.",
  "하지만 스킬로 만들면 기본기가 됩니다.",
  "스킬을 쓰면 토큰이 항상 줄어드나요?",
  "어떤 작업을 스크립트로 처리하나요?",
]) {
  if (!localizedCopy.includes(text)) {
    throw new Error(`Missing landing message: ${text}`);
  }
}

if (!app.includes('className="efficiency-layout"')) {
  throw new Error("Missing asymmetric efficiency layout.");
}

const hero = app.match(/<section className="hero"[\s\S]*?<\/section>/)?.[0] ?? "";
if ((hero.match(/button--primary/g) ?? []).length !== 1) {
  throw new Error("Hero must contain exactly one primary action.");
}

if (!html.includes(content.meta.title)) {
  throw new Error("Korean metadata title is stale.");
}

console.log("Approved landing message verified.");
