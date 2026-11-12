import React from 'react';
import { cn } from '../../utilities/cn';

export interface GovSelectProps extends React.SelectHTMLAttributes<HTMLSelectElement> {
  label?: string;
  error?: string;
  helperText?: string;
  options: { label: string; value: string | number }[];
}

export const GovSelect = React.forwardRef<HTMLSelectElement, GovSelectProps>(
  ({ className, label, error, helperText, options, id, ...props }, ref) => {
    const selectId = id || (label ? label.toLowerCase().replace(/\s+/g, '-') : undefined);

    return (
      <div className="w-full flex flex-col gap-1.5">
        {label && (
          <label htmlFor={selectId} className="text-xs font-semibold text-ink-primary tracking-tight">
            {label}
            {props.required && <span className="text-emergency ml-1">*</span>}
          </label>
        )}
        <select
          ref={ref}
          id={selectId}
          className={cn(
            'w-full h-9 px-3 text-sm bg-white border border-line rounded-md text-ink-primary transition-all duration-150 focus:outline-none focus:ring-1 focus:ring-forest focus:border-forest shadow-2xs disabled:bg-bg-subtle disabled:cursor-not-allowed',
            error && 'border-emergency focus:ring-emergency focus:border-emergency',
            className
          )}
          {...props}
        >
          {options.map((opt) => (
            <option key={String(opt.value)} value={opt.value}>
              {opt.label}
            </option>
          ))}
        </select>
        {error && <span className="text-xs text-emergency font-medium leading-none">{error}</span>}
        {helperText && !error && (
          <span className="text-xs text-sage leading-none">{helperText}</span>
        )}
      </div>
    );
  }
);

GovSelect.displayName = 'GovSelect';

