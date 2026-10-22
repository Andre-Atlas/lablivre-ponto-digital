import { useEffect, useId, useRef, useState } from 'react';
import type { ReactNode } from 'react';
import { cn } from './cn';

export interface MenuProps {
  /** The trigger label (text + optional caret handled by caller). */
  label: ReactNode;
  children: (close: () => void) => ReactNode;
  /** Visual style of the trigger. */
  triggerClassName?: string;
  align?: 'left' | 'right';
}

/**
 * Accessible dropdown menu: click/Enter/Space to open, Esc or outside-click to
 * close, `aria-haspopup`/`aria-expanded` on the trigger. Menu items are provided
 * via the render prop and should be `<MenuItem>`s (or links) that call `close()`.
 */
export function Menu({ label, children, triggerClassName, align = 'left' }: MenuProps) {
  const [open, setOpen] = useState(false);
  const ref = useRef<HTMLDivElement>(null);
  const menuId = useId();

  useEffect(() => {
    if (!open) return;
    const onDocClick = (e: MouseEvent) => {
      if (ref.current && !ref.current.contains(e.target as Node)) setOpen(false);
    };
    const onKey = (e: KeyboardEvent) => {
      if (e.key === 'Escape') setOpen(false);
    };
    document.addEventListener('mousedown', onDocClick);
    document.addEventListener('keydown', onKey);
    return () => {
      document.removeEventListener('mousedown', onDocClick);
      document.removeEventListener('keydown', onKey);
    };
  }, [open]);

  return (
    <div ref={ref} className="relative">
      <button
        type="button"
        aria-haspopup="menu"
        aria-expanded={open}
        aria-controls={menuId}
        onClick={() => setOpen((o) => !o)}
        className={triggerClassName}
      >
        {label}
      </button>
      {open && (
        <div
          id={menuId}
          role="menu"
          className={cn(
            'absolute top-full z-40 mt-1 min-w-52 rounded-card border border-border/60 bg-surface p-1.5 shadow-pop',
            align === 'right' ? 'right-0' : 'left-0',
          )}
        >
          {children(() => setOpen(false))}
        </div>
      )}
    </div>
  );
}

export function MenuItem({
  onClick,
  children,
  icon,
}: {
  onClick?: () => void;
  children: ReactNode;
  icon?: ReactNode;
}) {
  return (
    <button
      type="button"
      role="menuitem"
      onClick={onClick}
      className="flex w-full items-center gap-2.5 rounded-lg px-3 py-2 text-left text-sm font-medium text-text transition-colors hover:bg-primary/5 hover:text-primary"
    >
      {icon && <span className="text-muted">{icon}</span>}
      {children}
    </button>
  );
}
