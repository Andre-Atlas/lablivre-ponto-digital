import type { ReactNode } from 'react';
import { Blob } from './Blob';
import type { BlobVariant } from './Blob';
import { cn } from './cn';

export interface EmptyStateProps {
  title: string;
  description?: string;
  icon?: ReactNode;
  blobVariant?: BlobVariant;
  action?: ReactNode;
  className?: string;
}

export function EmptyState({ title, description, icon, blobVariant = 'purple-ring', action, className }: EmptyStateProps) {
  return (
    <div className={cn('flex flex-col items-center justify-center text-center px-6 py-16', className)}>
      <div className="relative mb-5 flex h-20 w-20 items-center justify-center">
        <Blob variant={blobVariant} ring className="absolute inset-0 opacity-30" />
        <div className="relative text-primary">{icon}</div>
      </div>
      <h3 className="text-lg font-bold tracking-tight text-ink">{title}</h3>
      {description && <p className="mt-1 max-w-sm text-sm text-muted">{description}</p>}
      {action && <div className="mt-5">{action}</div>}
    </div>
  );
}
