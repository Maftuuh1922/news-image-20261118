// news-image-20261118 entry (Node 22, standard library only).
//
// The front page itself is entry.png, rendered by render.py from the
// verified stories in research-notes.md. This program only copies those
// bytes to the grader's output directory, so both grader runs write
// exactly the same file.
//
// Outside the grader's container, MAKEFUN_OUTPUT_DIR stands in for
// /output:
//   mkdir -p out && MAKEFUN_OUTPUT_DIR=out node main.ts

import { copyFileSync, existsSync, mkdirSync, statSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";

const outDir = process.env.MAKEFUN_OUTPUT_DIR ?? "/output";
mkdirSync(outDir, { recursive: true });

const here = dirname(fileURLToPath(import.meta.url));
const source = join(here, "entry.png");
if (!existsSync(source)) {
  throw new Error("entry.png is missing from the repository");
}
const dest = join(outDir, "entry.png");
copyFileSync(source, dest);
console.log(`wrote ${dest} (${statSync(dest).size} bytes)`);
