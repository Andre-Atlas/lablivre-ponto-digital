import { LabLivreLogo } from './LabLivreLogo';

/** Shared navy footer with brand mark. */
export function AppFooter() {
  return (
    <footer className="mt-16 bg-ink text-white/80">
      <div className="mx-auto flex max-w-6xl flex-col gap-4 px-6 py-10 sm:flex-row sm:items-center sm:justify-between lg:px-8">
        <div className="flex items-center gap-3">
          <LabLivreLogo variant="light" className="w-24" />
          <span className="text-sm text-white/80">Ponto Digital</span>
        </div>
        <p className="text-xs text-white/70">
          Lab Livre · Laboratório de Software Livre — UnB
        </p>
      </div>
    </footer>
  );
}
