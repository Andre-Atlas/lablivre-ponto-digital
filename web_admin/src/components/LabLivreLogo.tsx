export function LabLivreLogo({ className = "", isDark = true }: { className?: string, isDark?: boolean }) {
  const textColor = isDark ? "#ffffff" : "#111111";
  const lineColor = isDark ? "#ffffff" : "#111111";

  return (
    <svg viewBox="0 0 240 100" className={className} xmlns="http://www.w3.org/2000/svg">
      <rect width="100%" height="100%" fill="#fae8eb" fillOpacity={isDark ? 0 : 1} rx="8" />
      <g className="transition-colors duration-500" transform="translate(10, 0)">
        {/* Stick */}
        <line x1="20" y1="28" x2="23" y2="88" stroke={lineColor} strokeWidth="5" />
        
        {/* Orange Shape */}
        <path d="M 26 68 L 45 78 L 37 89 L 27 82 Z" fill="#f59321" />

        {/* Magenta Shape */}
        <path d="M 24 38 L 49 18 L 46 60 L 26 68 Z" fill="#c42673" />

        {/* Cyan Fold */}
        <path d="M 26 68 L 46 60 L 42 70 L 28 73 Z" fill="#12bceb" />
      </g>
      
      <g fill={textColor} fontFamily='Helvetica, Arial, Inter, sans-serif' fontWeight="800" className="transition-colors duration-500">
        <text x="75" y="48" fontSize="42" letterSpacing="-2">Lab</text>
        <text x="75" y="88" fontSize="42" letterSpacing="-2">Livre</text>
      </g>
    </svg>
  );
}
