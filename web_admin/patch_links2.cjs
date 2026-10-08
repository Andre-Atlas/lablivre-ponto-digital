const fs = require('fs');

const latestReleaseUrl = "https://github.com/Andre-Atlas/lablivre-ponto-digital/releases/latest/download";
const windowsUrl = `${latestReleaseUrl}/PontoDigital-Windows.exe`;
const macUrl = `${latestReleaseUrl}/PontoDigital-Mac.tar.gz`;
const linuxUrl = `${latestReleaseUrl}/PontoDigital-Linux`;

let content = fs.readFileSync('src/pages/Login.tsx', 'utf8');

// The links are:
// <a href="#" ...>Client (Windows)</a>
// Since there's newlines, let's just replace href="#" with the URLs. 
// We know they appear in order: Windows, Mac, Linux
content = content.replace(/href="#"/, `href="${windowsUrl}"`);
content = content.replace(/href="#"/, `href="${macUrl}"`);
content = content.replace(/href="#"/, `href="${linuxUrl}"`);
// If there are other href="#" (like the terms/privacy), they come AFTER.
// Wait, is "Esqueceu a senha" href="#"?
// Yes! 
// Let's replace the whole anchor blocks more carefully using split.

const parts = content.split('Client (Windows)');
content = parts[0].replace(/href="#"([^"]*)$/, `href="${windowsUrl}"$1`) + 'Client (Windows)' + parts[1];

const parts2 = content.split('Client (Mac)');
content = parts2[0].replace(/href="#"([^"]*)$/, `href="${macUrl}"$1`) + 'Client (Mac)' + parts2[1];

const parts3 = content.split('Client (Linux)');
content = parts3[0].replace(/href="#"([^"]*)$/, `href="${linuxUrl}"$1`) + 'Client (Linux)' + parts3[1];

fs.writeFileSync('src/pages/Login.tsx', content);
console.log('Links updated manually');
