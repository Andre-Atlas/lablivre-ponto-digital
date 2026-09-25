const { chromium } = require('playwright');
(async () => {
  const browser = await chromium.launch();
  const context = await browser.newContext();
  const page = await context.newPage();
  
  await page.addInitScript(() => {
    localStorage.setItem('token', 'fake_token');
  });

  await page.goto('http://localhost:5173');
  await page.waitForTimeout(1500);
  
  await page.screenshot({ path: 'dashboard_with_export.png' });
  await browser.close();
})();
