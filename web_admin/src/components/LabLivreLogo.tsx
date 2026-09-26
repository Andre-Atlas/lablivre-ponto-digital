export function LabLivreLogo({ className = "", isDark = false }: { className?: string, isDark?: boolean }) {
  // Ignoramos a prop isDark e deixamos o CSS puro (Tailwind) cuidar da troca de imagem
  // Isso garante que funcione 100% sincronizado com a classe 'dark' do <html>
  return (
    <>
      <img 
        src="/logo-lablivre.png" 
        alt="Lab Livre Logo" 
        className={`object-contain block dark:hidden ${className}`} 
      />
      <img 
        src="/logo-lablivre-dark.png" 
        alt="Lab Livre Logo" 
        className={`object-contain hidden dark:block ${className}`} 
      />
    </>
  );
}
