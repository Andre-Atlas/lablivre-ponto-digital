import { cn } from './cn';

export type StatTone = 'primary' | 'accent' | 'ink' | 'success';

const TONE: Record<StatTone, string> = {
  primary: 'text-primary',
  accent: 'text-accent',
  ink: 'text-ink',
  success: 'text-success-dark',
};

export interface StatCalloutProps {
  value: string | number;
  label: string;
  tone?: StatTone;
  className?: string;
}

export function StatCallout({ value, label, tone = 'primary', className }: StatCalloutProps) {
  return (
    <div className={cn('flex flex-col', className)}>
      <span className={cn('font-display font-bold leading-none text-4xl sm:text-5xl', TONE[tone])}>{value}</span>
      <span className="eyebrow mt-2">{label}</span>
    </div>
  );
}
