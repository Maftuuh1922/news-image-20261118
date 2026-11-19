// The World Today — v4, "The Day in World News", 18 November 2026.
//
// The front page is entry.png, drawn by render.py from the 52 verified
// stories in research-notes.md. This file does one thing only: it copies
// those exact bytes to the grader's output directory, so both grader runs
// produce the same file. It renders nothing and calls no other program.
//
// Rebuild the picture locally with:  python3 render.py entry.png
// Ship it with:  mkdir -p out && MAKEFUN_OUTPUT_DIR=out node main.ts

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
if (bytes.length > 1_048_576) {
  throw new Error(`entry.png is ${bytes.length} bytes, over the 1 MiB cap`);
}

// A PNG starts with these eight bytes; refuse to ship anything else,
// so a truncated or misnamed file fails loudly instead of silently.
// (v3 round 2 failed run_completes because its entrypoint used Bun-only
// APIs and re-rendered in place; this file stays plain Node on purpose.)
const pngMagic = Buffer.from([0x89, 0x50, 0x4e, 0x47, 0x0d, 0x0a, 0x1a, 0x0a]);
if (!bytes.subarray(0, 8).equals(pngMagic)) {
  throw new Error("entry.png does not start with a PNG signature");
}

const width = bytes.readUInt32BE(16);
const height = bytes.readUInt32BE(20);
if (width !== 1024 || height !== 1024) {
  throw new Error(`entry.png is ${width}x${height}, expected 1024x1024`);
}

mkdirSync(outDir, { recursive: true });
const destPath = join(outDir, "entry.png");
writeFileSync(destPath, bytes);
console.log(`wrote ${destPath} (${statSync(destPath).size} bytes)`);
