const { chromium } = require('playwright');
(async () => {
  const browser = await chromium.launch();
  const page = await browser.newPage();
  await page.goto('http://localhost:5173');
  // Wait a moment for rendering and fonts
  await page.waitForTimeout(1000);
  await page.screenshot({ path: 'screenshot.png' });
  await browser.close();
})();
