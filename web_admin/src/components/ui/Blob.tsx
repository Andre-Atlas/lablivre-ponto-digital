import { cn } from './cn';

export type BlobVariant = 'navy' | 'purple' | 'purple-ring' | 'green' | 'orange' | 'pink';

const FILL: Record<BlobVariant, string> = {
  navy: 'text-ink',
  purple: 'text-primary',
  'purple-ring': 'text-primary-light',
  green: 'text-success',
  orange: 'text-accent',
  pink: 'text-accent-pink',
};

/**
 * Decorative organic brand shape. Purely presentational — hidden from
 * assistive tech and never interactive. Used on entry/empty surfaces only.
 */
export function Blob({
  variant = 'purple',
  ring = false,
  className,
}: {
  variant?: BlobVariant;
  ring?: boolean;
  className?: string;
}) {
  return (
    <svg
      viewBox="0 0 200 200"
      aria-hidden="true"
      focusable="false"
      className={cn('pointer-events-none select-none', FILL[variant], className)}
    >
      <path
        fill={ring ? 'none' : 'currentColor'}
        stroke={ring ? 'currentColor' : 'none'}
        strokeWidth={ring ? 26 : 0}
        d="M44.3,-64.6C56.3,-55.3,64,-41.1,69.4,-25.9C74.9,-10.7,78,5.5,73.6,19.6C69.2,33.7,57.2,45.8,43.6,55.4C30,65,14.9,72.1,-1.4,74C-17.7,75.9,-35.4,72.6,-48.9,62.8C-62.4,53,-71.7,36.7,-75.3,19.4C-78.9,2,-76.8,-16.4,-68.8,-31.3C-60.8,-46.2,-46.9,-57.6,-32.3,-66C-17.7,-74.4,-2.4,-79.8,11.6,-77.3C25.6,-74.8,32.3,-73.9,44.3,-64.6Z"
        transform="translate(100 100)"
      />
    </svg>
  );
}
