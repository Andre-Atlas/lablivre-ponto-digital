export function LabLivreLogo({ className = "", isDark = false }: { className?: string, isDark?: boolean }) {
  // Se isDark for passado ou se a classe 'dark' estiver ativa no tailwind, aplica a sombra
  return (
    <img 
      src="/logo-lablivre.png" 
      alt="Lab Livre Logo" 
      className={`object-contain ${className} ${isDark ? 'drop-shadow-[0_0_8px_rgba(255,255,255,0.8)]' : 'dark:drop-shadow-[0_0_8px_rgba(255,255,255,0.8)]'}`} 
    />
  );
}
