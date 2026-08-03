import { readFile } from "node:fs/promises";
import path from "node:path";
import { fileURLToPath } from "node:url";

const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..");
const signature = Buffer.from([137, 80, 78, 71, 13, 10, 26, 10]);

for (const locale of ["ko", "en", "jp", "cn"]) {
  const file = `skills-social-card-${locale}.png`;
  const buffer = await readFile(path.join(root, "public", "assets", file));
  if (!buffer.subarray(0, 8).equals(signature)) {
    throw new Error(`${file} is not PNG`);
  }
  if (buffer.readUInt32BE(16) !== 1200 || buffer.readUInt32BE(20) !== 630) {
    throw new Error(`${file} must be 1200x630`);
  }
}

console.log("Localized social cards verified at 1200x630 PNG.");
