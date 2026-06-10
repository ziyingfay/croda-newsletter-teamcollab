import { createRequire } from "node:module";
import { mkdirSync, writeFileSync } from "node:fs";
import path from "node:path";

const require = createRequire("/Users/fangziying/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/playwright/package.json");
const { chromium } = require("playwright");

const fileUrl = "file:///Users/fangziying/Documents/trae_projects/claudecodeinstall/croda-monthly-intel-ppt/index-v2.html";
const outDir = path.resolve("dev/temp/croda-v2-shots");
mkdirSync(outDir, { recursive: true });

const browser = await chromium.launch({ headless: true });
const page = await browser.newPage({ viewport: { width: 1600, height: 900 }, deviceScaleFactor: 1 });
const targets = [3, 4, 8, 9, 15];
const results = [];

for (const target of targets) {
  await page.goto(`${fileUrl}?slide=${target}`, { waitUntil: "networkidle" });
  await page.waitForTimeout(700);
  const shot = path.join(outDir, `slide-${String(target).padStart(2, "0")}.png`);
  await page.screenshot({ path: shot, fullPage: false });
  const active = await page.evaluate(() => {
    const index = (window.__currentSlideIndex ?? -1) + 1;
    const slide = document.querySelectorAll(".slide")[index - 1];
    const overflowing = [...document.querySelectorAll(".slide.active *")].filter((el) => {
      const rect = el.getBoundingClientRect();
      const parent = el.parentElement?.getBoundingClientRect();
      return parent && (rect.right > parent.right + 1 || rect.bottom > parent.bottom + 1);
    }).length;
    return {
      index,
      text: slide ? slide.innerText.slice(0, 260).replace(/\s+/g, " ") : "",
      overflowing,
    };
  });
  results.push({ target, shot, active });
}

await browser.close();
writeFileSync(path.join(outDir, "summary.json"), JSON.stringify(results, null, 2));
console.log(JSON.stringify(results, null, 2));
