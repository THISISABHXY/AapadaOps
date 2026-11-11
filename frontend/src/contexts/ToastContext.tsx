import React, { createContext, useContext, useState, useCallback } from 'react';
import { AlertCircle, CheckCircle2, Info, X } from 'lucide-react';

export type ToastType = 'success' | 'error' | 'warning' | 'info';

export interface Toast {
  id: string;
  type: ToastType;
  title: string;
  message?: string;
  duration?: number;
}

interface ToastContextType {
  toasts: Toast[];
  showToast: (type: ToastType, title: string, message?: string, duration?: number) => void;
  removeToast: (id: string) => void;
}

const ToastContext = createContext<ToastContextType | undefined>(undefined);

export const ToastProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [toasts, setToasts] = useState<Toast[]>([]);

  const removeToast = useCallback((id: string) => {
    setToasts((prev) => prev.filter((t) => t.id !== id));
  }, []);

  const showToast = useCallback(
    (type: ToastType, title: string, message?: string, duration = 4500) => {
      const id = 'toast_' + Math.random().toString(36).substring(2, 9);
      const newToast: Toast = { id, type, title, message, duration };
      setToasts((prev) => [...prev, newToast]);

      if (duration > 0) {
        setTimeout(() => {
          removeToast(id);
        }, duration);
      }
    },
    [removeToast]
  );

  return (
    <ToastContext.Provider value={{ toasts, showToast, removeToast }}>
      {children}
      {/* Toast Render Container */}
      <div
        aria-live="assertive"
        className="fixed bottom-4 right-4 z-50 flex flex-col gap-2 max-w-sm w-full pointer-events-none"
      >
        {toasts.map((toast) => {
          const typeStyles = {
            success: 'border-forest/40 bg-white text-ink-primary',
            error: 'border-emergency/40 bg-white text-ink-primary',
            warning: 'border-amber/50 bg-white text-ink-primary',
            info: 'border-line-dark bg-white text-ink-primary',
          }[toast.type];

          const IconComponent = {
            success: <CheckCircle2 className="w-5 h-5 text-forest flex-shrink-0" />,
            error: <AlertCircle className="w-5 h-5 text-emergency flex-shrink-0" />,
            warning: <AlertCircle className="w-5 h-5 text-amber-dark flex-shrink-0" />,
            info: <Info className="w-5 h-5 text-sage flex-shrink-0" />,
          }[toast.type];

          return (
            <div
              key={toast.id}
              className={`pointer-events-auto flex items-start gap-3 p-3.5 rounded border shadow-sm transition-all animate-in fade-in slide-in-from-bottom-2 ${typeStyles}`}
              role="alert"
            >
              {IconComponent}
              <div className="flex-1 min-w-0">
                <div className="font-semibold text-sm leading-tight text-ink-primary">
                  {toast.title}
                </div>
                {toast.message && (
                  <div className="text-xs text-ink-secondary mt-1 leading-normal">
                    {toast.message}
                  </div>
                )}
              </div>
              <button
                onClick={() => removeToast(toast.id)}
                className="text-sage hover:text-ink-primary p-0.5 rounded focus:outline-none"
                aria-label="Close notification"
              >
                <X className="w-4 h-4" />
              </button>
            </div>
          );
        })}
      </div>
    </ToastContext.Provider>
  );
};

export const useToast = () => {
  const context = useContext(ToastContext);
  if (!context) {
    throw new Error('useToast must be used within a ToastProvider');
  }
  return context;
};

