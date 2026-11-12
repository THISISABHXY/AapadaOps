import React from 'react';
import { cn } from '../../utilities/cn';

export interface GovButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: 'primary' | 'secondary' | 'danger' | 'ghost' | 'outline';
  size?: 'sm' | 'md' | 'lg';
  isLoading?: boolean;
  leftIcon?: React.ReactNode;
  rightIcon?: React.ReactNode;
}

export const GovButton = React.forwardRef<HTMLButtonElement, GovButtonProps>(
  (
    {
      className,
      variant = 'primary',
      size = 'md',
      isLoading = false,
      leftIcon,
      rightIcon,
      children,
      disabled,
      ...props
    },
    ref
  ) => {
    const baseStyles =
      'inline-flex items-center justify-center font-medium transition-all duration-150 ease-out focus:outline-none focus-visible:ring-2 focus-visible:ring-forest/50 focus-visible:ring-offset-1 disabled:opacity-50 disabled:pointer-events-none rounded-md select-none cursor-pointer active:scale-[0.985]';

    const variants = {
      primary:
        'bg-forest hover:bg-forest-dark active:bg-forest-dark text-white border border-forest-dark/30 shadow-xs hover:shadow-sm',
      secondary:
        'bg-white hover:bg-bg-subtle active:bg-bg-subtle text-ink-primary border border-line hover:border-line-dark shadow-xs',
      danger:
        'bg-emergency hover:bg-emergency-dark active:bg-emergency-dark text-white border border-emergency-dark/30 shadow-xs hover:shadow-sm',
      outline:
        'bg-transparent hover:bg-forest-subtle text-forest border border-forest/60 active:bg-forest-subtle',
      ghost:
        'bg-transparent hover:bg-bg-subtle active:bg-bg-subtle text-ink-primary border-transparent',
    };

    const sizes = {
      sm: 'text-xs h-7 px-2.5 gap-1.5 font-medium',
      md: 'text-xs sm:text-sm h-9 px-3.5 gap-2 font-medium',
      lg: 'text-sm sm:text-base h-11 px-5 gap-2.5 font-semibold',
    };

    return (
      <button
        ref={ref}
        className={cn(baseStyles, variants[variant], sizes[size], className)}
        disabled={disabled || isLoading}
        {...props}
      >
        {isLoading ? (
          <span className="inline-block w-4 h-4 border-2 border-current border-t-transparent rounded-full animate-spin mr-1.5" />
        ) : (
          leftIcon
        )}
        {children}
        {!isLoading && rightIcon}
      </button>
    );
  }
);

GovButton.displayName = 'GovButton';


