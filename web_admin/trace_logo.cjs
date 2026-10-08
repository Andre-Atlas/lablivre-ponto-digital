const potrace = require('potrace');
const fs = require('fs');

const imagePath = '/Users/andreatlas/.gemini/antigravity/brain/ae607236-2a49-487b-9962-29f90f0d4f78/.user_uploaded/media_1790875925152.jpg';

potrace.trace(imagePath, function(err, svg) {
  if (err) throw err;
  
  // Make SVG clean and responsive
  let cleanSvg = svg.replace(/width=".*?"/, 'viewBox="0 0 1024 571"').replace(/height=".*?"/, '');
  cleanSvg = cleanSvg.replace(/fill=".*?"/g, 'fill="currentColor"');
  
  fs.writeFileSync('logo_traced.svg', cleanSvg);
  console.log('Saved logo_traced.svg');
});
