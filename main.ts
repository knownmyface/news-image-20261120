// make.fun news-image-20261120 entry program.
//
// The front page is pre-rendered by render.py into entry.png (1024x1024,
// under 1 MiB, byte-identical on every run). This program validates that
// file against the competition limits and copies it byte-for-byte into
// MAKEFUN_OUTPUT_DIR/entry.png. Node standard library only; no network,
// no installs, deterministic output. package.json marks this folder as an
// ES module so Node loads main.ts without the typeless-module warning.
//
// Run it outside the grader's container with:
//   mkdir -p out && MAKEFUN_OUTPUT_DIR=out node main.ts

import { mkdirSync, readFileSync, writeFileSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";

const LIMIT_BYTES = 1048576;
const LIMIT_SIDE = 1024;
const PNG_SIG = Buffer.from([0x89, 0x50, 0x4e, 0x47, 0x0d, 0x0a, 0x1a, 0x0a]);

function die(why) {
  throw new Error(`entry.png check failed: ${why}`);
}

function main() {
  const outDir = process.env.MAKEFUN_OUTPUT_DIR;
  if (!outDir) die("MAKEFUN_OUTPUT_DIR is not set");

  const here = dirname(fileURLToPath(import.meta.url));
  const png = readFileSync(join(here, "entry.png"));

  if (png.length < 33 || !png.subarray(0, 8).equals(PNG_SIG)) {
    die("entry.png does not start with the PNG signature");
  }
  if (png.subarray(png.length - 12).indexOf(Buffer.from("IEND")) === -1) {
    die("entry.png has no IEND chunk — the file looks truncated");
  }

  // IHDR stores width at byte 16 and height at byte 20, big-endian uint32.
  const width = png.readUInt32BE(16);
  const height = png.readUInt32BE(20);
  if (width !== LIMIT_SIDE || height !== LIMIT_SIDE) {
    die(`entry.png is ${width}x${height}, expected ${LIMIT_SIDE}x${LIMIT_SIDE}`);
  }
  if (png.length > LIMIT_BYTES) {
    die(`entry.png is ${png.length} bytes, over the ${LIMIT_BYTES} limit`);
  }

  mkdirSync(outDir, { recursive: true });
  const dest = join(outDir, "entry.png");
  writeFileSync(dest, png);
  console.log(`wrote ${dest}: ${png.length} bytes, ${width}x${height} PNG`);
  console.log("front page: FRIDAY 20 NOVEMBER 2026, 60 stories, 13 pins");
}

main();
