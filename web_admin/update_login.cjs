const fs = require('fs');

let content = fs.readFileSync('src/pages/Login.tsx', 'utf8');

// 1. Container Principal
content = content.replace(
  /<div className="min-h-screen flex relative overflow-hidden/g,
  '<div className="min-h-screen flex flex-col lg:flex-row relative overflow-x-hidden overflow-y-auto lg:overflow-hidden'
);

// 2. Brand Context container
content = content.replace(
  /<div className="hidden lg:flex flex-1 flex-col justify-center px-24 relative z-10 selection:bg-\[#D12A6A\] selection:text-white">/g,
  '<div className="w-full lg:flex-1 flex flex-col justify-center px-6 sm:px-12 lg:px-24 pt-16 lg:pt-0 pb-8 lg:pb-0 relative z-10 selection:bg-[#D12A6A] selection:text-white">'
);

// 3. max-w-xl
content = content.replace(
  /<div className="max-w-xl">/g,
  '<div className="max-w-xl mx-auto lg:mx-0 w-full text-center lg:text-left">'
);

// 4. Logo class
content = content.replace(
  /<LabLivreLogo className="w-64 mb-12 drop-shadow-xl" \/>/g,
  '<LabLivreLogo className="w-48 sm:w-56 lg:w-64 mb-8 lg:mb-12 mx-auto lg:mx-0 drop-shadow-xl" />'
);

// 5. h1
content = content.replace(
  /<h1 className="text-5xl md:text-6xl tracking-tighter leading-\[1.1\] mb-8 font-medium">/g,
  '<h1 className="text-4xl sm:text-5xl md:text-6xl tracking-tighter leading-[1.1] mb-6 lg:mb-8 font-medium">'
);
content = content.replace(
  /O hub central de<br\/>/g,
  'O hub central de<br className="hidden lg:block"/>'
);

// 6. p
content = content.replace(
  /<p className="text-lg text-slate-600 dark:text-white\/50 font-light leading-relaxed max-w-\[45ch\] transition-colors duration-500">/g,
  '<p className="text-base sm:text-lg text-slate-600 dark:text-white/50 font-light leading-relaxed max-w-[45ch] mx-auto lg:mx-0 transition-colors duration-500 mb-8 lg:mb-12">'
);

// 7. Remove existing mt-12 in Download flex container
content = content.replace(
  /<div className="mt-12 flex items-center gap-6 opacity-90">/g,
  '<div className="flex flex-col sm:flex-row flex-wrap items-center justify-center lg:justify-start gap-4 lg:gap-6 opacity-90">'
);
// Make spans inside Download text visible on mobile if needed, but it's fine.
content = content.replace(
  /<span>Baixar App Desktop<\/span>/g,
  '<span className="text-xs sm:text-sm">Baixar App Desktop</span>'
);

// 8. Login Interface container
content = content.replace(
  /<div className="flex-1 flex items-center justify-center p-6 sm:p-12 relative z-10">/g,
  '<div className="w-full lg:flex-1 flex items-center justify-center p-6 sm:p-12 pb-16 lg:py-0 relative z-10">'
);

fs.writeFileSync('src/pages/Login.tsx', content);
console.log('Login.tsx updated for responsiveness');
