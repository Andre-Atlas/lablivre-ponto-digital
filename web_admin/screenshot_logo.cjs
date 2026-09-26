const { chromium } = require('playwright');
(async () => {
  const browser = await chromium.launch();
  const page = await browser.newPage();
  await page.goto('http://localhost:5173/login');
  // Wait for the SVG to load
  const svg = await page.waitForSelector('svg[viewBox="0 0 240 100"]');
  await svg.screenshot({ path: 'current_logo.png' });
  await browser.close();
  console.log('Screenshot saved to current_logo.png');
})();
