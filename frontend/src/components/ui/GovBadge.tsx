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
  size?: 'sm' | 'md';
}

export const GovBadge: React.FC<GovBadgeProps> = ({
  className,
  variant = 'neutral',
  size = 'md',
  children,
  ...props
}) => {
  const base =
    'inline-flex items-center font-medium font-mono uppercase tracking-wider rounded border select-none';

  const variants = {
    forest: 'bg-forest-subtle text-forest border-forest/30',
    sage: 'bg-sage-subtle text-sage border-sage/30',
    amber: 'bg-amber-subtle text-amber-dark border-amber/40',
    emergency: 'bg-emergency-subtle text-emergency border-emergency/30',
    outline: 'bg-transparent text-ink-primary border-line',
    neutral: 'bg-bg-subtle text-ink-secondary border-line',
  };

  const sizes = {
    sm: 'text-[10px] px-1.5 py-0.5 leading-none',
    md: 'text-xs px-2 py-0.5 leading-tight',
  };

  return (
    <span className={cn(base, variants[variant], sizes[size], className)} {...props}>
      {children}
    </span>
  );
};

