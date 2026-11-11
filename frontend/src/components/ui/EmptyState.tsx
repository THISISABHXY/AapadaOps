import React from 'react';
import { ShieldAlert, CheckCircle2, FolderSearch } from 'lucide-react';
import { cn } from '../../utilities/cn';

export interface EmptyStateProps {
  icon?: 'check' | 'search' | 'shield';
  title: string;
  description?: string;
  action?: React.ReactNode;
  className?: string;
}

export const EmptyState: React.FC<EmptyStateProps> = ({
  icon = 'check',
  title,
  description,
  action,
  className,
}) => {
  const icons = {
    check: <CheckCircle2 className="w-8 h-8 text-forest" />,
    search: <FolderSearch className="w-8 h-8 text-sage" />,
    shield: <ShieldAlert className="w-8 h-8 text-amber-dark" />,
  };

  return (
    <div
      className={cn(
        'flex flex-col items-center justify-center p-8 text-center bg-white rounded border border-dashed border-line',
        className
      )}
    >
      <div className="p-3 bg-bg-warm rounded-full mb-3">{icons[icon]}</div>
      <h4 className="text-sm font-semibold text-ink-primary mb-1">{title}</h4>
      {description && <p className="text-xs text-sage max-w-sm mb-4">{description}</p>}
      {action && <div>{action}</div>}
    </div>
  );
};
