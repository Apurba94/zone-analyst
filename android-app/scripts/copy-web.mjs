// Copy ../website into www/, the folder Capacitor packs into the APK.
//
// One change on the way: Android's WebView can't save a file the page offers
// for download, so the workbook link points at the live site instead, where
// the phone's browser downloads it.

import { cpSync, existsSync, readFileSync, rmSync, writeFileSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";

const here = dirname(fileURLToPath(import.meta.url));
const site = join(here, "..", "..", "website");
const www = join(here, "..", "www");
const LIVE = "https://zoneanalyst.vercel.app/";

if (!existsSync(join(site, "index.html"))) {
  console.error(`website not found at ${site}`);
  process.exit(1);
}

rmSync(www, { recursive: true, force: true });
cpSync(site, www, {
  recursive: true,
  filter: (src) => !/[\\/](\.htaccess|robots\.txt)$/.test(src),
});

const index = join(www, "index.html");
const html = readFileSync(index, "utf8");
const patched = html.replace(
  /href="(downloads\/[^"]+)" download/g,
  (_, file) => `href="${LIVE}${file}"`,
);
if (patched === html) {
  console.error("copy-web: workbook link not found in index.html; update scripts/copy-web.mjs");
  process.exit(1);
}
writeFileSync(index, patched);
console.log(`copied website/ to www/ (workbook link -> ${LIVE})`);
