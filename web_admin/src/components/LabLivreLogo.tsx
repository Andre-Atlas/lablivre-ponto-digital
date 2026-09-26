
export function LabLivreLogo({ className = "", isDark = true }: { className?: string, isDark?: boolean }) {
  const textColor = isDark ? "#ffffff" : "#221E1F";
  const lineColor = isDark ? "#ffffff" : "#221E1F";

  return (
    <svg viewBox="0 0 240 100" className={className} xmlns="http://www.w3.org/2000/svg">
      <defs>
        <clipPath id="magenta-clip">
          <path d="M 24 38 L 49 18 L 46 60 L 26 68 Z" />
        </clipPath>
      </defs>

      <g className="transition-colors duration-500" transform="translate(10, 0)">
        {/* Stick */}
        <line x1="14" y1="28" x2="18" y2="88" stroke={lineColor} strokeWidth="3.5" strokeLinecap="round" />
        
        {/* Orange Shape */}
        <path d="M 26 68 L 45 78 L 37 89 L 27 82 Z" fill="#f59321" stroke="#f59321" strokeWidth="1.5" strokeLinejoin="round" />

        {/* Magenta Shape */}
        <path d="M 24 38 L 49 18 L 46 60 L 26 68 Z" fill="#c42673" stroke="#c42673" strokeWidth="1.5" strokeLinejoin="round" />

        {/* Cyan Pill - Base */}
        <line x1="28" y1="67" x2="38" y2="75" stroke="#12bceb" strokeWidth="6" strokeLinecap="round" />

        {/* Cyan Pill - Overlap with Magenta */}
        <line x1="28" y1="67" x2="38" y2="75" stroke="#1b73a7" strokeWidth="6" strokeLinecap="round" clipPath="url(#magenta-clip)" />
      </g>
      
      <g fill={textColor} fontFamily='"Orbitron", "Space Grotesk", sans-serif' fontWeight="400" className="transition-colors duration-500">
        <text x="80" y="48" fontSize="38" letterSpacing="0">Lab</text>
        <text x="80" y="88" fontSize="38" letterSpacing="0">Livre</text>
      </g>
    </svg>
  );
}
