const { chromium } = require('playwright');

(async () => {
  const browser = await chromium.launch();
  const page = await browser.newPage();
  
  await page.goto('http://localhost:5173');
  
  // Wait for login page
  await page.waitForSelector('text=Entrar');
  
  // Click "Entrar"
  await page.click('text=Entrar');
  
  // Wait for network requests
  await page.waitForTimeout(2000);
  
  // See if there's an error message
  const error = await page.$('text=Falha no login');
  if (error) {
    console.log('Login failed!');
  } else {
    console.log('Login seems successful');
    await page.waitForTimeout(1000);
    // Find Aprovar button
    const aprovarBtn = await page.$('text=Aprovar');
    if (aprovarBtn) {
       console.log('Found Aprovar button! Clicking...');
       await aprovarBtn.click();
       await page.waitForTimeout(1000);
    } else {
       console.log('No Aprovar button found.');
    }
  }
  
  await page.screenshot({ path: '/Users/andreatlas/.gemini/antigravity/brain/a6116b10-edfe-474a-ad19-d72c1e5df16b/dashboard-real.png' });
  
  await browser.close();
})();
