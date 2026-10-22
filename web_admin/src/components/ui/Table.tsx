import type { ReactNode } from 'react';
import { cn } from './cn';

export interface Column<Row> {
  key: string;
  header: ReactNode;
  align?: 'left' | 'center' | 'right';
  width?: string;
  render?: (row: Row, index: number) => ReactNode;
}

export interface TableProps<Row> {
  columns: Column<Row>[];
  data: Row[];
  rowKey: (row: Row, index: number) => string | number;
  empty?: ReactNode;
  stickyHeader?: boolean;
  className?: string;
}

const alignCls = { left: 'text-left', center: 'text-center', right: 'text-right' } as const;

export function Table<Row>({ columns, data, rowKey, empty, stickyHeader, className }: TableProps<Row>) {
  if (data.length === 0 && empty) {
    return <>{empty}</>;
  }
  return (
    <div className={cn('w-full overflow-x-auto', className)}>
      <table className="w-full border-collapse text-left">
        <thead className={cn('bg-peach/60', stickyHeader && 'sticky top-0 z-10')}>
          <tr>
            {columns.map((c) => (
              <th
                key={c.key}
                scope="col"
                style={c.width ? { width: c.width } : undefined}
                className={cn(
                  'px-5 py-3 text-[11px] font-bold uppercase tracking-wider text-ink whitespace-nowrap',
                  alignCls[c.align ?? 'left'],
                )}
              >
                {c.header}
              </th>
            ))}
          </tr>
        </thead>
        <tbody className="divide-y divide-border/50">
          {data.map((row, i) => (
            <tr key={rowKey(row, i)} className="hover:bg-bg/60 transition-colors">
              {columns.map((c) => (
                <td
                  key={c.key}
                  className={cn('px-5 py-4 text-sm text-text align-middle', alignCls[c.align ?? 'left'])}
                >
                  {c.render ? c.render(row, i) : (row as Record<string, ReactNode>)[c.key]}
                </td>
              ))}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
