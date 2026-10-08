const fs = require('fs');

const svgStr = fs.readFileSync('logo_traced.svg', 'utf8');
const dMatch = svgStr.match(/d="([^"]+)"/);
if (!dMatch) throw new Error("No path found");

const d = dMatch[1];
const subpaths = d.split(' M ');

// First subpath doesn't have an M at the beginning because we split by ' M ', but wait, the string starts with 'M '
// Actually: d="M 209... M 214... M 634..."
const pieces = d.split('M ');
// pieces[0] = ""
// pieces[1] = "209.500 ..."
// pieces[2] = "214.414 ..."

const iconPath = "M " + pieces[1] + "M " + pieces[2];

const faviconSvg = `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 450 571" version="1.1">
  <style>
    path { fill: #0f172a; }
    @media (prefers-color-scheme: dark) {
      path { fill: #ffffff; }
    }
  </style>
  <path d="${iconPath}" stroke="none" fill-rule="evenodd"/>
</svg>`;

fs.writeFileSync('public/favicon.svg', faviconSvg);
console.log('Saved public/favicon.svg');
