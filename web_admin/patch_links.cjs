const fs = require('fs');

const latestReleaseUrl = "https://github.com/Andre-Atlas/lablivre-ponto-digital/releases/latest/download";
const windowsUrl = `${latestReleaseUrl}/PontoDigital-Windows.exe`;
const macUrl = `${latestReleaseUrl}/PontoDigital-Mac.tar.gz`;
const linuxUrl = `${latestReleaseUrl}/PontoDigital-Linux`;

function updateFile(filename) {
    let content = fs.readFileSync(filename, 'utf8');
    
    // In Login.tsx:
    content = content.replace(/<a href="#"([^>]*?)>\s*Client \(Windows\)\s*<\/a>/g, `<a href="${windowsUrl}"$1>Client (Windows)</a>`);
    content = content.replace(/<a href="#"([^>]*?)>\s*Client \(Mac\)\s*<\/a>/g, `<a href="${macUrl}"$1>Client (Mac)</a>`);
    content = content.replace(/<a href="#"([^>]*?)>\s*Client \(Linux\)\s*<\/a>/g, `<a href="${linuxUrl}"$1>Client (Linux)</a>`);

    // In Dashboard.tsx, the buttons are slightly different, I will replace all occurrence of Client (...) href="#"
    // But wait, in the previous replace it handles the anchor tag.
    fs.writeFileSync(filename, content);
}

updateFile('src/pages/Login.tsx');
try {
  // Check if Dashboard.tsx has these buttons
  let dContent = fs.readFileSync('src/pages/Dashboard.tsx', 'utf8');
  if (dContent.includes('Client (Windows)')) {
     updateFile('src/pages/Dashboard.tsx');
  }
} catch (e) {}

console.log('Links updated');
