'use client';

import React from 'react';

export const LoadingSkeleton = () => (
  <div className="animate-pulse space-y-4">
    {[...Array(3)].map((_, i) => (
      <div key={i} className="h-24 bg-gray-300 rounded"></div>
    ))}
  </div>
);

export const LoadingSpinner = () => (
  <div className="flex justify-center items-center h-64">
    <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-blue-500"></div>
  </div>
);

export const ErrorMessage = ({ message }: { message: string }) => (
  <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded relative">
    <strong>Error:</strong> {message}
  </div>
);

export const SuccessMessage = ({ message }: { message: string }) => (
  <div className="bg-green-100 border border-green-400 text-green-700 px-4 py-3 rounded relative">
    <strong>Success!</strong> {message}
  </div>
);

export const StarRating = ({ rating, count, onRate }: { rating: number; count?: number; onRate?: (rating: number) => void }) => (
  <div className="flex items-center gap-1">
    {[...Array(5)].map((_, i) => (
      <button
        key={i}
        onClick={() => onRate?.(i + 1)}
        className={`text-xl ${i < rating ? 'text-yellow-400' : 'text-gray-300'} ${onRate ? 'cursor-pointer' : ''}`}
      >
        ★
      </button>
    ))}
    {count && <span className="text-sm text-gray-600 ml-2">({count})</span>}
  </div>
);

export const Badge = ({ children, variant = 'default' }: { children: React.ReactNode; variant?: 'default' | 'success' | 'warning' | 'danger' }) => {
  const variants = {
    default: 'bg-blue-100 text-blue-800',
    success: 'bg-green-100 text-green-800',
    warning: 'bg-yellow-100 text-yellow-800',
    danger: 'bg-red-100 text-red-800',
  };

  return (
    <span className={`inline-block px-3 py-1 rounded-full text-sm font-semibold ${variants[variant]}`}>
      {children}
    </span>
  );
};
