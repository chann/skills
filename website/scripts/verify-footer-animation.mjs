import { readFile } from "node:fs/promises";
import path from "node:path";
import { fileURLToPath } from "node:url";

const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..");
const app = await readFile(path.join(root, "src", "App.tsx"), "utf8");
const footerWordmark =
  app.match(/<div className="site-footer__word"[\s\S]*?<\/div>/)?.[0] ?? "";

for (const snippet of [
  'initial={reduceMotion ? false : { y: "0.42em", opacity: 0 }}',
  "whileInView={{ y: 0, opacity: 1 }}",
  "viewport={{ once: false, amount: 0.2 }}",
]) {
  if (!footerWordmark.includes(snippet)) {
    throw new Error(`Footer wordmark animation is missing ${snippet}.`);
  }
}

if (footerWordmark.includes("once: true")) {
  throw new Error("Footer wordmark animation must reset after leaving the viewport.");
}

console.log("Footer wordmark replay and reduced-motion contract verified.");
