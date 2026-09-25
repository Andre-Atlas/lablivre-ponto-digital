const { chromium } = require('playwright');
(async () => {
  const browser = await chromium.launch();
  const page = await browser.newPage();
  await page.goto('http://localhost:5173');
  await page.waitForTimeout(1000);
  
  // By default it's light mode
  await page.screenshot({ path: 'screenshot_light.png' });
  
  // Click the theme toggle (assuming it's a button)
  await page.click('button:has(svg)');
  await page.waitForTimeout(500);
  await page.screenshot({ path: 'screenshot_dark.png' });
  
  await browser.close();
})();
