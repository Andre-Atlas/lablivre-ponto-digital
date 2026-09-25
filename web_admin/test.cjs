const { chromium } = require('playwright');

(async () => {
  const browser = await chromium.launch();
  const page = await browser.newPage();
  
  await page.goto('http://localhost:5173');
  
  // wait for either login or dashboard
  await page.waitForLoadState('networkidle');
  
  const title = await page.title();
  console.log('Title:', title);
  
  // check if "Entrar" button is there
  const entrarBtn = await page.$('text=Entrar');
  if (entrarBtn) {
    console.log('Found Entrar button, clicking...');
    await entrarBtn.click();
    await page.waitForTimeout(2000); // wait for navigation/re-render
  } else {
    console.log('Entrar button not found');
  }
  
  await page.screenshot({ path: '/Users/andreatlas/.gemini/antigravity/brain/a6116b10-edfe-474a-ad19-d72c1e5df16b/dashboard.png' });
  
  await browser.close();
})();
