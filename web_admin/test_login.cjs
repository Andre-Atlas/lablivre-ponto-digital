const { chromium } = require('playwright');
(async () => {
  const browser = await chromium.launch();
  const context = await browser.newContext();
  const page = await context.newPage();
  
  await page.goto('http://localhost:5173');
  
  // Fill email and password
  await page.fill('input[type="email"]', 'admin@example.com');
  await page.fill('input[type="password"]', 'admin123');
  
  // Click login
  await page.click('button[type="submit"]');
  
  // Wait for network idle or navigation
  await page.waitForTimeout(2000);
  
  // Take screenshot to see if it's on dashboard
  await page.screenshot({ path: 'after_login.png' });
  
  // Check if we are on dashboard by looking for "Painel Administrativo"
  const text = await page.textContent('body');
  if (text.includes('Painel Administrativo')) {
    console.log('LOGIN SUCCESSFUL');
  } else {
    console.log('LOGIN FAILED');
  }
  
  await browser.close();
})();
