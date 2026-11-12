import React from 'react';
import { cn } from '../../utilities/cn';

export interface GovInputProps extends React.InputHTMLAttributes<HTMLInputElement> {
  label?: string;
  error?: string;
  helperText?: string;
}

export const GovInput = React.forwardRef<HTMLInputElement, GovInputProps>(
  ({ className, label, error, helperText, id, ...props }, ref) => {
    const inputId = id || (label ? label.toLowerCase().replace(/\s+/g, '-') : undefined);

    return (
      <div className="w-full flex flex-col gap-1.5">
        {label && (
          <label htmlFor={inputId} className="text-xs font-semibold text-ink-primary tracking-tight">
            {label}
            {props.required && <span className="text-emergency ml-1">*</span>}
          </label>
        )}
        <input
          ref={ref}
          id={inputId}
          className={cn(
            'w-full h-9 px-3 text-sm bg-white border border-line rounded-md text-ink-primary placeholder:text-sage transition-all duration-150 focus:outline-none focus:ring-1 focus:ring-forest focus:border-forest shadow-2xs disabled:bg-bg-subtle disabled:cursor-not-allowed',
            error && 'border-emergency focus:ring-emergency focus:border-emergency',
            className
          )}
          {...props}
        />
        {error && <span className="text-xs text-emergency font-medium leading-none">{error}</span>}
        {helperText && !error && (
          <span className="text-xs text-sage leading-none">{helperText}</span>
        )}
      </div>
    );
  }
);

GovInput.displayName = 'GovInput';

