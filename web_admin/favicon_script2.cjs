const fs = require('fs');

const svgStr = fs.readFileSync('public/favicon.svg', 'utf8');
const newSvg = svgStr.replace(/viewBox="[^"]+"/, 'viewBox="170 130 220 320"');
fs.writeFileSync('public/favicon.svg', newSvg);
console.log('Updated viewBox');
