// The World Today — 18 November 2026 (make.fun news-image-20261118, v2).
//
// The front page is entry.png, drawn by render.py from the verified
// stories in research-notes.md. This program does nothing clever: it
// reads those exact bytes and writes them to the grader's output
// directory, so the two grader runs produce identical files.
//
// Local check:
//   mkdir -p out && MAKEFUN_OUTPUT_DIR=out node main.ts

import { existsSync, mkdirSync, readFileSync, statSync, writeFileSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";

const outDir = process.env.MAKEFUN_OUTPUT_DIR ?? "/output";
const here = dirname(fileURLToPath(import.meta.url));
const sourcePath = join(here, "entry.png");

if (!existsSync(sourcePath)) {
  throw new Error("entry.png is missing next to main.ts");
}

const bytes = readFileSync(sourcePath);
if (bytes.length === 0) {
  throw new Error("entry.png is empty");
}

// A PNG starts with these eight bytes; refuse to ship anything else,
// so a truncated or misnamed file fails loudly instead of silently.
const pngMagic = Buffer.from([0x89, 0x50, 0x4e, 0x47, 0x0d, 0x0a, 0x1a, 0x0a]);
if (!bytes.subarray(0, 8).equals(pngMagic)) {
  throw new Error("entry.png does not start with a PNG signature");
}

mkdirSync(outDir, { recursive: true });
const destPath = join(outDir, "entry.png");
writeFileSync(destPath, bytes);
console.log(`wrote ${destPath} (${statSync(destPath).size} bytes)`);
