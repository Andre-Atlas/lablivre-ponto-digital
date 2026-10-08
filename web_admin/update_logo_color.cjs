const fs = require('fs');

let content = fs.readFileSync('src/components/LabLivreLogo.tsx', 'utf8');
content = content.replace(/className={`block \${className}`}/, 'className={`block text-slate-900 dark:text-white ${className}`}');
fs.writeFileSync('src/components/LabLivreLogo.tsx', content);
console.log('Updated LabLivreLogo.tsx text color');
