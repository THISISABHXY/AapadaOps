import React from 'react';
import { cn } from '../../utilities/cn';

export interface LoadingSkeletonProps {
  className?: string;
  count?: number;
  height?: string;
}

export const LoadingSkeleton: React.FC<LoadingSkeletonProps> = ({
  className,
  count = 1,
  height = 'h-4',
}) => {
  return (
    <div className="w-full space-y-2 animate-pulse">
      {Array.from({ length: count }).map((_, i) => (
        <div
          key={i}
          className={cn('bg-line/70 rounded w-full', height, className)}
        />
      ))}
    </div>
  );
};
