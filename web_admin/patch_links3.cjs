const fs = require('fs');

const latestReleaseUrl = "https://github.com/Andre-Atlas/lablivre-ponto-digital/releases/latest/download";
const windowsUrl = `${latestReleaseUrl}/PontoDigital-Windows.exe`;
const macUrl = `${latestReleaseUrl}/PontoDigital-Mac.tar.gz`;
const linuxUrl = `${latestReleaseUrl}/PontoDigital-Linux`;

let content = fs.readFileSync('src/pages/Login.tsx', 'utf8');

// Use parts
const parts = content.split('Client (Windows)');
parts[0] = parts[0].replace(/href="[^"]*"([^"]*)$/, `href="${windowsUrl}"$1`);

const parts2 = parts.join('Client (Windows)').split('Client (Mac)');
parts2[0] = parts2[0].replace(/href="[^"]*"([^"]*)$/, `href="${macUrl}"$1`);

const parts3 = parts2.join('Client (Mac)').split('Client (Linux)');
parts3[0] = parts3[0].replace(/href="[^"]*"([^"]*)$/, `href="${linuxUrl}"$1`);

fs.writeFileSync('src/pages/Login.tsx', parts3.join('Client (Linux)'));
console.log('Links updated manually');
