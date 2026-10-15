import type { HTMLAttributes, ReactNode } from 'react';
import { cn } from './cn';

export type BadgeTone = 'neutral' | 'primary' | 'success' | 'danger' | 'accent';
type Size = 'sm' | 'md';

const TONES: Record<BadgeTone, string> = {
  neutral: 'bg-ink/5 text-ink',
  primary: 'bg-primary/10 text-primary',
  success: 'bg-success/15 text-success-dark',
  danger: 'bg-danger/10 text-danger',
  accent: 'bg-accent/15 text-accent-darker',
};

const SIZES: Record<Size, string> = {
  sm: 'text-[10px] px-2 py-0.5',
  md: 'text-xs px-2.5 py-1',
};

export interface BadgeProps extends HTMLAttributes<HTMLSpanElement> {
  tone?: BadgeTone;
  size?: Size;
  children: ReactNode;
}

export function Badge({ tone = 'neutral', size = 'md', className, children, ...rest }: BadgeProps) {
  return (
    <span
      className={cn('inline-flex items-center gap-1 rounded-pill font-semibold uppercase tracking-wider', TONES[tone], SIZES[size], className)}
      {...rest}
    >
      {children}
    </span>
  );
}
