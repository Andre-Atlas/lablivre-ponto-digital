import type { ReactNode } from 'react';
import { AlertCircle, CheckCircle2, Info, XCircle, X } from 'lucide-react';
import { cn } from './cn';

export type AlertTone = 'info' | 'success' | 'warning' | 'danger';

const TONES: Record<AlertTone, { cls: string; Icon: typeof Info }> = {
  info: { cls: 'bg-primary/5 text-primary border-primary/20', Icon: Info },
  success: { cls: 'bg-success/10 text-success-dark border-success/25', Icon: CheckCircle2 },
  warning: { cls: 'bg-accent/10 text-accent-dark border-accent/25', Icon: AlertCircle },
  danger: { cls: 'bg-danger/10 text-danger border-danger/25', Icon: XCircle },
};

export interface AlertProps {
  tone?: AlertTone;
  title?: string;
  children?: ReactNode;
  onDismiss?: () => void;
  className?: string;
}

export function Alert({ tone = 'info', title, children, onDismiss, className }: AlertProps) {
  const { cls, Icon } = TONES[tone];
  return (
    <div role="alert" className={cn('flex items-start gap-2.5 rounded-lg border px-4 py-3 text-sm', cls, className)}>
      <Icon size={16} className="mt-0.5 shrink-0" />
      <div className="min-w-0 flex-1">
        {title && <p className="font-semibold">{title}</p>}
        {children && <div className={cn(title && 'mt-0.5')}>{children}</div>}
      </div>
      {onDismiss && (
        <button type="button" onClick={onDismiss} aria-label="Dispensar" className="shrink-0 opacity-70 hover:opacity-100">
          <X size={15} />
        </button>
      )}
    </div>
  );
}
