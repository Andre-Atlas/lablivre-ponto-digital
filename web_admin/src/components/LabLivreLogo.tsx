
export function LabLivreLogo({ className = "", isDark = true }: { className?: string, isDark?: boolean }) {
  const strokeColor = isDark ? "#ffffff" : "#0f172a";
  const textColor = isDark ? "#ffffff" : "#0f172a";

  return (
    <svg viewBox="0 0 240 100" className={className}>
      <g stroke={strokeColor} strokeWidth="2.5" strokeLinejoin="round" strokeLinecap="round" className="transition-colors duration-500">
        {/* Slanted Line */}
        <line x1="25" y1="20" x2="33" y2="85" />
        
        {/* Magenta Wing */}
        <path d="M 40,25 L 85,15 L 80,75 L 42,62 Z" fill="#D12A6A" />
        
        {/* Cyan Piece */}
        <path d="M 42,62 L 65,70 L 55,78 L 36,68 Z" fill="#00B9DE" /> 
        
        {/* Orange Piece */}
        <path d="M 55,78 L 65,70 L 85,82 L 60,95 L 45,86 Z" fill="#F39200" />
      </g>
      {/* Text Lab Livre */}
      <text x="110" y="45" fontFamily='"Space Grotesk", "Michroma", "Orbitron", system-ui, sans-serif' fontSize="32" fontWeight="400" fill={textColor} letterSpacing="1" className="transition-colors duration-500">Lab</text>
      <text x="110" y="85" fontFamily='"Space Grotesk", "Michroma", "Orbitron", system-ui, sans-serif' fontSize="32" fontWeight="400" fill={textColor} letterSpacing="1" className="transition-colors duration-500">Livre</text>
    </svg>
  );
}
