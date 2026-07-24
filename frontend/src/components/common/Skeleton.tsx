import React from 'react';

/**
 * Skeleton loading primitives for content placeholders.
 */

interface SkeletonProps {
  className?: string;
}

/** A single animated line placeholder. */
export const SkeletonLine: React.FC<SkeletonProps> = ({ className = 'h-4 w-full' }) => (
  <div className={`animate-pulse rounded bg-gray-200 ${className}`} />
);

/** A card-shaped placeholder. */
export const SkeletonCard: React.FC<SkeletonProps> = ({ className = '' }) => (
  <div className={`animate-pulse rounded-lg bg-gray-200 h-28 ${className}`} />
);

/** A table with N skeleton rows. */
export const SkeletonTable: React.FC<{ rows?: number; cols?: number }> = ({
  rows = 5,
  cols = 4,
}) => (
  <div className="bg-white border border-gray-200 rounded-lg shadow-sm overflow-hidden">
    {/* Header */}
    <div className="bg-gray-50 px-6 py-3 flex gap-4">
      {Array.from({ length: cols }).map((_, i) => (
        <SkeletonLine key={`h-${i}`} className="h-3 flex-1" />
      ))}
    </div>
    {/* Rows */}
    <div className="divide-y divide-gray-200">
      {Array.from({ length: rows }).map((_, rowIdx) => (
        <div key={rowIdx} className="px-6 py-4 flex gap-4">
          {Array.from({ length: cols }).map((_, colIdx) => (
            <SkeletonLine key={`r-${rowIdx}-c-${colIdx}`} className="h-4 flex-1" />
          ))}
        </div>
      ))}
    </div>
  </div>
);

/** A grid of skeleton stat cards. */
export const SkeletonCards: React.FC<{ count?: number }> = ({ count = 4 }) => (
  <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-4">
    {Array.from({ length: count }).map((_, i) => (
      <SkeletonCard key={i} />
    ))}
  </div>
);
