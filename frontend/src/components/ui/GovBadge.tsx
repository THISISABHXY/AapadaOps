import React from 'react';
import { cn } from '../../utilities/cn';

export interface GovBadgeProps extends React.HTMLAttributes<HTMLSpanElement> {
  variant?:
    | 'forest'
    | 'sage'
    | 'amber'
    | 'emergency'
    | 'outline'
    | 'neutral';
  size?: 'sm' | 'md' | 'lg';
  dot?: boolean;
  pulse?: boolean;
}

export const GovBadge: React.FC<GovBadgeProps> = ({
  className,
  variant = 'neutral',
  size = 'md',
  dot = false,
  pulse = false,
  children,
  ...props
}) => {
  const base =
    'inline-flex items-center font-mono uppercase tracking-wider rounded-md border select-none transition-colors duration-150 font-medium';

  const variants = {
    forest: 'bg-forest/10 text-forest border-forest/25',
    sage: 'bg-sage/15 text-ink-primary border-sage/30',
    amber: 'bg-amber/15 text-amber-dark border-amber/40',
    emergency: 'bg-emergency/10 text-emergency border-emergency/30',
    outline: 'bg-transparent text-ink-primary border-line',
    neutral: 'bg-bg-subtle text-ink-secondary border-line',
  };

  const dotColors = {
    forest: 'bg-forest',
    sage: 'bg-sage',
    amber: 'bg-amber-dark',
    emergency: 'bg-emergency',
    outline: 'bg-ink-primary',
    neutral: 'bg-ink-secondary',
  };

  const sizes = {
    sm: 'text-[10px] px-2 py-0.5 leading-none gap-1',
    md: 'text-[11px] px-2.5 py-0.5 leading-tight gap-1.5',
    lg: 'text-xs px-3 py-1 leading-normal gap-2',
  };

  return (
    <span className={cn(base, variants[variant], sizes[size], className)} {...props}>
      {dot && (
        <span
          className={cn(
            'w-1.5 h-1.5 rounded-full inline-block flex-shrink-0',
            dotColors[variant],
            pulse && 'animate-pulse'
          )}
        />
      )}
      {children}
    </span>
  );
};


