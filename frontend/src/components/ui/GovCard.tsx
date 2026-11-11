import React from 'react';
import { cn } from '../../utilities/cn';

export interface GovCardProps extends React.HTMLAttributes<HTMLDivElement> {
  header?: React.ReactNode;
  footer?: React.ReactNode;
  padding?: 'none' | 'sm' | 'md' | 'lg';
}

export const GovCard: React.FC<GovCardProps> = ({
  className,
  header,
  footer,
  padding = 'md',
  children,
  ...props
}) => {
  const paddings = {
    none: '',
    sm: 'p-3',
    md: 'p-4 sm:p-5',
    lg: 'p-6',
  };

  return (
    <div
      className={cn(
        'bg-white rounded border border-line shadow-sm overflow-hidden flex flex-col',
        className
      )}
      {...props}
    >
      {header && (
        <div className="border-b border-line bg-bg-warm/50 px-4 py-3 sm:px-5 flex items-center justify-between">
          {header}
        </div>
      )}
      <div className={cn('flex-1', paddings[padding])}>{children}</div>
      {footer && (
        <div className="border-t border-line bg-bg-warm/30 px-4 py-2.5 sm:px-5 flex items-center justify-between">
          {footer}
        </div>
      )}
    </div>
  );
};
