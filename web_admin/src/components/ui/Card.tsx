import type { HTMLAttributes, ReactNode } from 'react';
import { cn } from './cn';

type Padding = 'none' | 'sm' | 'md' | 'lg';
const PAD: Record<Padding, string> = { none: '', sm: 'p-4', md: 'p-6', lg: 'p-8' };

export interface CardProps extends HTMLAttributes<HTMLDivElement> {
  padding?: Padding;
  interactive?: boolean;
  children?: ReactNode;
}

export function Card({ padding = 'md', interactive = false, className, children, ...rest }: CardProps) {
  return (
    <div
      className={cn(
        'bg-surface rounded-card border border-border/60 shadow-card',
        interactive && 'transition-shadow duration-200 hover:shadow-pop',
        PAD[padding],
        className,
      )}
      {...rest}
    >
      {children}
    </div>
  );
}

Card.Header = function CardHeader({ className, children, ...rest }: HTMLAttributes<HTMLDivElement>) {
  return (
    <div className={cn('mb-4 flex items-start justify-between gap-4', className)} {...rest}>
      {children}
    </div>
  );
};

Card.Body = function CardBody({ className, children, ...rest }: HTMLAttributes<HTMLDivElement>) {
  return <div className={cn('text-text', className)} {...rest}>{children}</div>;
};

Card.Footer = function CardFooter({ className, children, ...rest }: HTMLAttributes<HTMLDivElement>) {
  return <div className={cn('mt-6 flex items-center justify-end gap-3', className)} {...rest}>{children}</div>;
};
