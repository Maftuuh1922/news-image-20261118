// The World Today — v3, "The Day in World News", 18 November 2026.
// A one-page newspaper front page drawn as a 1024x1024 PNG. It takes the
// 43 verified stories gathered in research-notes.md and lays them out in
// four columns, so one picture can hold the whole day: lead, two second
// stories, 28 column stories, and a 12-item brief strip, plus a date-check
// line saying what was left out and why.
//
// How to run it (Bun):
//   bun main.ts
// That writes entry.png next to this file. The build is deterministic:
// the same inputs always produce the same bytes, because every string is
// fixed here and the PNG writer uses no clock or random value.
//
// What main.ts itself does is small on purpose. The drawing lives in
// render.py; this file only checks that the input is what it expects,
// hands it over, and confirms the output is a real PNG of the right size.

import { spawnSync } from "bun";

const SCRIPT_DIR = import.meta.dir;
const PY = new URL("./render.py", import.meta.url).pathname;
const OUT = new URL("./entry.png", import.meta.url).pathname;

function fail(message: string): never {
  console.error(`[news-image] ${message}`);
  process.exit(1);
}

if (!Bun.file(PY).size) fail("render.py is missing from " + SCRIPT_DIR);

const run = spawnSync(["python3", PY, OUT], {
  cwd: SCRIPT_DIR,
  stdout: "pipe",
  stderr: "pipe",
});

if (run.exitCode !== 0) {
  fail(`render.py exited ${run.exitCode}: ${run.stderr.toString().trim()}`);
}
const renderLog = run.stdout.toString().trim();
if (renderLog) console.log(renderLog);

const bytes = Bun.file(OUT);
const size = await bytes.size;
if (size > 1_048_576) fail(`entry.png is ${size} bytes, over the 1 MiB cap`);

const head = new Uint8Array(await bytes.slice(0, 24).arrayBuffer());
const pngMagic = [0x89, 0x50, 0x4e, 0x47, 0x0d, 0x0a, 0x1a, 0x0a];
if (!pngMagic.every((b, i) => head[i] === b)) {
  fail("entry.png does not start with the PNG signature");
}
const width = new DataView(head.buffer).getUint32(16, false);
const height = new DataView(head.buffer).getUint32(20, false);
if (width !== 1024 || height !== 1024) {
  fail(`entry.png is ${width}x${height}, expected 1024x1024`);
}

console.log(`[news-image] wrote entry.png (${size} bytes, ${width}x${height})`);
