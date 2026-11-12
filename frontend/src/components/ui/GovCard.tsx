import React from 'react';
import { cn } from '../../utilities/cn';

export interface GovCardProps extends React.HTMLAttributes<HTMLDivElement> {
  header?: React.ReactNode;
  footer?: React.ReactNode;
  padding?: 'none' | 'xs' | 'sm' | 'md' | 'lg';
  hoverEffect?: boolean;
}

export const GovCard: React.FC<GovCardProps> = ({
  className,
  header,
  footer,
  padding = 'md',
  hoverEffect = false,
  children,
  ...props
}) => {
  const paddings = {
    none: '',
    xs: 'p-2.5',
    sm: 'p-3 sm:p-3.5',
    md: 'p-4 sm:p-5',
    lg: 'p-6 sm:p-7',
  };

  return (
    <div
      className={cn(
        'bg-white rounded-lg border border-line shadow-xs overflow-hidden flex flex-col transition-all duration-150',
        hoverEffect && 'hover:border-line-dark hover:shadow-sm cursor-pointer',
        className
      )}
      {...props}
    >
      {header && (
        <div className="border-b border-line bg-bg-warm/40 px-4 py-3 sm:px-5 flex items-center justify-between gap-3">
          {header}
        </div>
      )}
      <div className={cn('flex-1', paddings[padding])}>{children}</div>
      {footer && (
        <div className="border-t border-line bg-bg-warm/25 px-4 py-2.5 sm:px-5 flex items-center justify-between gap-3">
          {footer}
        </div>
      )}
    </div>
  );
};


