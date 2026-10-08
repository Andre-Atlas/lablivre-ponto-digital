const fs = require('fs');

let content = fs.readFileSync('src/pages/Login.tsx', 'utf8');

// 1. Container Principal
content = content.replace(
  /<div className="min-h-\[100dvh\] flex text-slate-900 dark:text-white relative overflow-hidden bg-\[#F0F2F5\] dark:bg-\[#0A0A0A\]/g,
  '<div className="min-h-[100dvh] flex flex-col lg:flex-row text-slate-900 dark:text-white relative overflow-x-hidden overflow-y-auto lg:overflow-hidden bg-[#F0F2F5] dark:bg-[#0A0A0A]'
);

fs.writeFileSync('src/pages/Login.tsx', content);
console.log('Login.tsx fixed');
