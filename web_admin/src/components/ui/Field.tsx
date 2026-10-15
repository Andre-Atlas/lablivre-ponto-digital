import type { ReactNode } from 'react';
import { cn } from './cn';

/** Shared label + hint + error scaffold for form controls. */
export function FieldShell({
  id,
  label,
  hint,
  error,
  className,
  children,
}: {
  id: string;
  label: string;
  hint?: string;
  error?: string;
  className?: string;
  children: ReactNode;
}) {
  const hintId = hint ? `${id}-hint` : undefined;
  const errorId = error ? `${id}-error` : undefined;
  return (
    <div className={cn('flex flex-col gap-1.5', className)}>
      <label htmlFor={id} className="eyebrow">
        {label}
      </label>
      {children}
      {hint && !error && (
        <p id={hintId} className="text-xs text-muted">
          {hint}
        </p>
      )}
      {error && (
        <p id={errorId} className="text-xs text-danger font-medium" role="alert">
          {error}
        </p>
      )}
    </div>
  );
}

/** Base control classes shared by Input/Select/Textarea. */
export function controlClasses(error?: string): string {
  return cn(
    'w-full rounded-lg bg-surface px-4 py-2.5 text-sm text-text placeholder-muted transition-colors',
    'border focus:outline-none',
    error ? 'border-danger focus-visible:outline-danger' : 'border-border focus:border-primary',
  );
}
