export function LabLivreLogo({ className = "" }: { className?: string }) {
  return (
    <img 
      src="/logo-lablivre.png" 
      alt="Lab Livre Logo" 
      className={`object-contain ${className} dark:drop-shadow-[0_0_8px_rgba(255,255,255,0.8)]`} 
    />
  );
}
