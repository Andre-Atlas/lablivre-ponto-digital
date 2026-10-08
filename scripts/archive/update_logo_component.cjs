const fs = require('fs');

let content = fs.readFileSync('src/components/LabLivreLogo.tsx', 'utf8');
content = content.replace(/viewBox="0 0 1024 571"/, 'viewBox="170 130 660 320"');
fs.writeFileSync('src/components/LabLivreLogo.tsx', content);
console.log('Updated LabLivreLogo.tsx viewBox');
