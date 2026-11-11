import React from 'react';
import { Sparkles, AlertTriangle } from 'lucide-react';
import { cn } from '../../utilities/cn';

export interface AIAdvisoryCalloutProps {
  title?: string;
  confidenceScore?: number;
  entities?: Record<string, any>;
  rationale?: string;
  suggestedPriority?: string;
  className?: string;
}

/**
 * AI Advisory Callout Component
 * CRITICAL SAFETY REQUIREMENT:
 * Visibly distinguishes unverified AI suggestions from verified facts and authorized human decisions.
 */
export const AIAdvisoryCallout: React.FC<AIAdvisoryCalloutProps> = ({
  title = 'AI Decision Support — Advisory Only',
  confidenceScore,
  entities,
  rationale,
  suggestedPriority,
  className,
}) => {
  return (
    <div
      className={cn(
        'p-3.5 bg-bg-warm border-l-4 border-sage rounded-r border-y border-r border-line text-ink-primary',
        className
      )}
      role="note"
      aria-label="AI Advisory Decision Support"
    >
      <div className="flex items-center justify-between pb-1.5 border-b border-line mb-2">
        <div className="flex items-center gap-2">
          <Sparkles className="w-4 h-4 text-sage flex-shrink-0" />
          <span className="text-xs font-mono font-semibold uppercase tracking-wider text-sage">
            {title}
          </span>
        </div>
        {confidenceScore !== undefined && (
          <span className="text-xs font-mono text-sage">
            Confidence: <strong className="text-ink-primary">{Math.round(confidenceScore * 100)}%</strong>
          </span>
        )}
      </div>

      <div className="text-xs text-ink-secondary space-y-1.5">
        {suggestedPriority && (
          <div className="flex items-center gap-1.5">
            <span className="font-semibold text-ink-primary">Suggested Priority:</span>
            <span className="font-mono px-1.5 py-0.5 rounded bg-bg-subtle border border-line text-ink-primary uppercase text-[11px]">
              {suggestedPriority}
            </span>
          </div>
        )}

        {rationale && <p className="leading-relaxed">{rationale}</p>}

        {entities && Object.keys(entities).length > 0 && (
          <div className="mt-2 pt-2 border-t border-line/60">
            <span className="font-medium text-ink-primary block mb-1">Extracted Vulnerability Entities:</span>
            <div className="flex flex-wrap gap-1.5">
              {Object.entries(entities).map(([key, val]) => {
                if (val === undefined || val === false || val === null) return null;
                const formattedKey = key
                  .replace(/([A-Z])/g, ' $1')
                  .replace(/^./, (str) => str.toUpperCase());
                return (
                  <span
                    key={key}
                    className="inline-flex items-center gap-1 font-mono text-[11px] bg-white px-2 py-0.5 rounded border border-line"
                  >
                    <span className="text-sage">{formattedKey}:</span>
                    <span className="font-semibold text-ink-primary">{String(val)}</span>
                  </span>
                );
              })}
            </div>
          </div>
        )}

        <div className="flex items-center gap-1 mt-2 text-[11px] text-sage font-sans italic">
          <AlertTriangle className="w-3.5 h-3.5 flex-shrink-0 text-amber-dark" />
          <span>Requires review and explicit authorization by a verified human officer before dispatch.</span>
        </div>
      </div>
    </div>
  );
};
