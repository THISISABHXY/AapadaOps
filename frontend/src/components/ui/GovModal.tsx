import React, { useEffect } from 'react';
import { X } from 'lucide-react';
import { cn } from '../../utilities/cn';

export interface GovModalProps {
  isOpen: boolean;
  onClose: () => void;
  title: string;
  description?: string;
  children: React.ReactNode;
  footer?: React.ReactNode;
  maxWidth?: 'sm' | 'md' | 'lg' | 'xl';
}

export const GovModal: React.FC<GovModalProps> = ({
  isOpen,
  onClose,
  title,
  description,
  children,
  footer,
  maxWidth = 'md',
}) => {
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key === 'Escape' && isOpen) {
        onClose();
      }
    };
    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [isOpen, onClose]);

  if (!isOpen) return null;

  const maxWidths = {
    sm: 'max-w-md',
    md: 'max-w-lg',
    lg: 'max-w-2xl',
    xl: 'max-w-4xl',
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 sm:p-6 animate-in fade-in duration-150">
      {/* Neutral dark overlay, zero blur */}
      <div
        className="fixed inset-0 bg-[#202B32]/40 transition-opacity"
        onClick={onClose}
        aria-hidden="true"
      />

      {/* Modal Dialog Card */}
      <div
        className={cn(
          'relative w-full bg-white rounded border border-line shadow-md overflow-hidden z-10 flex flex-col max-h-[90vh]',
          maxWidths[maxWidth]
        )}
        role="dialog"
        aria-modal="true"
        aria-labelledby="modal-title"
      >
        <div className="flex items-center justify-between px-5 py-3.5 border-b border-line bg-bg-warm/60">
          <div>
            <h3 id="modal-title" className="text-base font-semibold text-ink-primary leading-tight">
              {title}
            </h3>
            {description && (
              <p className="text-xs text-sage mt-0.5 leading-normal">{description}</p>
            )}
          </div>
          <button
            onClick={onClose}
            className="p-1 text-sage hover:text-ink-primary rounded focus:outline-none focus:ring-1 focus:ring-forest"
            aria-label="Close dialog"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        <div className="p-5 overflow-y-auto flex-1">{children}</div>

        {footer && (
          <div className="px-5 py-3 border-t border-line bg-bg-warm/30 flex items-center justify-end gap-2.5">
            {footer}
          </div>
        )}
      </div>
    </div>
  );
};

