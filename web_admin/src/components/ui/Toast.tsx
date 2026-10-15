import { createContext, useCallback, useContext, useRef, useState } from 'react';
import type { ReactNode } from 'react';
import { Alert } from './Alert';
import type { AlertTone } from './Alert';

interface ToastItem {
  id: number;
  tone: AlertTone;
  title?: string;
  message: ReactNode;
}

interface ToastApi {
  toast: (opts: { tone?: AlertTone; title?: string; message: ReactNode; duration?: number }) => void;
}

const ToastContext = createContext<ToastApi | null>(null);

export function useToast(): ToastApi {
  const ctx = useContext(ToastContext);
  if (!ctx) throw new Error('useToast must be used within <ToastProvider>');
  return ctx;
}

export function ToastProvider({ children }: { children: ReactNode }) {
  const [items, setItems] = useState<ToastItem[]>([]);
  const counter = useRef(0);

  const remove = useCallback((id: number) => {
    setItems((prev) => prev.filter((t) => t.id !== id));
  }, []);

  const toast = useCallback<ToastApi['toast']>(
    ({ tone = 'info', title, message, duration = 4000 }) => {
      const id = ++counter.current;
      setItems((prev) => [...prev, { id, tone, title, message }]);
      if (duration > 0) {
        window.setTimeout(() => remove(id), duration);
      }
    },
    [remove],
  );

  return (
    <ToastContext.Provider value={{ toast }}>
      {children}
      <div
        className="fixed top-4 right-4 z-[60] flex w-[min(92vw,22rem)] flex-col gap-2"
        role="region"
        aria-live="polite"
        aria-label="Notificações"
      >
        {items.map((t) => (
          <div key={t.id} className="shadow-pop rounded-lg">
            <Alert tone={t.tone} title={t.title} onDismiss={() => remove(t.id)} className="bg-surface">
              {t.message}
            </Alert>
          </div>
        ))}
      </div>
    </ToastContext.Provider>
  );
}
