import { chromium } from "/Users/fangziying/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/playwright/index.mjs";

const path = "/Users/fangziying/Documents/trae_projects/claudecodeinstall/newsletter 字典/outputs/禾大Croda/html-demo/croda-beauty-tag-driven-demo.html";
const browser = await chromium.launch({ headless: true });
const results = [];

for (const viewport of [
  { name: "desktop", width: 1440, height: 1100 },
  { name: "mobile", width: 390, height: 844 }
]) {
  const page = await browser.newPage({
    viewport: { width: viewport.width, height: viewport.height },
    deviceScaleFactor: 1
  });
  const errors = [];
  page.on("pageerror", e => errors.push(e.message));
  page.on("console", msg => {
    if (msg.type() === "error") errors.push(msg.text());
  });
  await page.goto("file://" + path, { waitUntil: "load" });
  const metrics = await page.evaluate(() => {
    const doc = document.documentElement;
    const ids = [
      "report-summary",
      "toc-toggle-btn",
      "toc-sidebar",
      "card-mode-btn",
      "sc-overlay",
      "edit-hotzone",
      "edit-toggle",
      "export-btn",
      "export-menu",
      "export-print",
      "export-png-desktop",
      "export-png-mobile",
      "export-im-share"
    ];
    return {
      title: document.title,
      scrollWidth: doc.scrollWidth,
      clientWidth: doc.clientWidth,
      scrollHeight: doc.scrollHeight,
      missingIds: ids.filter(id => !document.getElementById(id)),
      cards: document.querySelectorAll(".report-card").length,
      sections: document.querySelectorAll("section").length,
      summaryTitle: JSON.parse(document.getElementById("report-summary").textContent).title
    };
  });
  await page.screenshot({
    path: `/Users/fangziying/Documents/trae_projects/claudecodeinstall/newsletter 字典/dev/temp/croda-html-demo-${viewport.name}.png`,
    fullPage: false
  });
  results.push({
    viewport: viewport.name,
    errors,
    metrics,
    overflowX: metrics.scrollWidth > metrics.clientWidth + 2
  });
  await page.close();
}

await browser.close();
console.log(JSON.stringify(results, null, 2));
