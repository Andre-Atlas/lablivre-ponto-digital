export function LabLivreLogo({ className = "", isDark = true }: { className?: string, isDark?: boolean }) {
  const textColor = isDark ? "#ffffff" : "#000000";
  const lineColor = isDark ? "#ffffff" : "#000000";

  return (
    <svg viewBox="0 0 240 100" className={className} xmlns="http://www.w3.org/2000/svg">
      <g className="transition-colors duration-500" transform="translate(5, 5)">
        {/* Slanted Line */}
        <path d="M 15 25 L 22 80" stroke={lineColor} strokeWidth="3.5" strokeLinecap="round" />
        
        {/* Magenta Wing */}
        <polygon points="30,35 75,15 70,65 30,75" fill="#C2185B" />
        
        {/* Orange Piece */}
        <polygon points="32,74 55,85 35,95 20,85" fill="#F57C00" />

        {/* Cyan Piece */}
        <polygon points="32,68 50,78 45,84 27,74" fill="#00B0FF" />
      </g>
      
      {/* Text Lab Livre */}
      {/* Usando path tracejado ou fonte com aparência similar ao logo */}
      <g fill={textColor} fontFamily='"Orbitron", "Space Grotesk", sans-serif' fontWeight="400" className="transition-colors duration-500">
        <text x="100" y="48" fontSize="38" letterSpacing="0">Lab</text>
        <text x="100" y="88" fontSize="38" letterSpacing="0">Livre</text>
      </g>
    </svg>
  );
}
