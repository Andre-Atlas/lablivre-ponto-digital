export function LabLivreLogo({ className = "" }: { className?: string }) {
  // O CSS puro (Tailwind) cuida da troca de imagem entre claro e escuro
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
