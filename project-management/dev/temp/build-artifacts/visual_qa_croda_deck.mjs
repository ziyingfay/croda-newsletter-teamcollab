import { createRequire } from "node:module";
import { writeFileSync } from "node:fs";

const require = createRequire("/Users/fangziying/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/playwright/package.json");
const { chromium } = require("playwright");
const deckPath = "/Users/fangziying/Documents/trae_projects/claudecodeinstall/newsletter 字典/outputs/禾大Croda/方案介绍PPT/style-b/index.html";
const browser = await chromium.launch({ headless: true });
const page = await browser.newPage({ viewport: { width: 1440, height: 900 }, deviceScaleFactor: 1 });
await page.goto(`file://${deckPath}`, { waitUntil: "networkidle" });
await page.waitForTimeout(1600);

const total = await page.locator("section.slide").count();
const checks = [];

for (const slideNo of [3, 4, 8, 9, 15]) {
  await page.goto(`file://${deckPath}?slide=${slideNo}`, { waitUntil: "networkidle" });
  await page.waitForTimeout(1400);
  checks.push(await page.evaluate((slideNoArg) => {
    const active = [...document.querySelectorAll(".slide")][slideNoArg - 1];
    const elems = active.querySelectorAll("h1,h2,h3,p,.flow-node,.sub-card,.confirm-card,.four-card,.mini-cell");
    const visible = [...elems].filter((el) => {
      const r = el.getBoundingClientRect();
      const st = getComputedStyle(el);
      return r.width > 0 && r.height > 0 && st.visibility !== "hidden" && st.display !== "none" && r.bottom > 0 && r.top < innerHeight;
    }).length;
    const overflow = [...elems].filter((el) => {
      const r = el.getBoundingClientRect();
      return r.bottom > innerHeight - 45 || r.right > innerWidth - 20 || r.left < -20 || r.top < -20;
    }).map((el) => {
      const r = el.getBoundingClientRect();
      return {
        tag: el.tagName,
        cls: String(el.className),
        text: el.textContent.trim().slice(0, 40),
        rect: [r.left, r.top, r.right, r.bottom].map(Math.round)
      };
    });
    return {
      slideNo: slideNoArg,
      visible,
      overflow,
      text: active.innerText.slice(0, 180).replace(/\s+/g, " ")
    };
  }, slideNo));
}

await page.goto(`file://${deckPath}?slide=15`, { waitUntil: "networkidle" });
await page.waitForTimeout(1400);
const screenshot = await page.screenshot({ type: "png", fullPage: false });
writeFileSync("/Users/fangziying/Documents/trae_projects/claudecodeinstall/newsletter 字典/dev/temp/croda-deck-slide-15.png", screenshot);
await browser.close();

console.log(JSON.stringify({ total, checks }, null, 2));
