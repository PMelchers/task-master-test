'use client';

import { useEffect } from 'react';
import { Loading } from '@/components/ui/loading';
import { cn } from '@/lib/utils';

export default function Error({
  error,
  reset,
}: {
  error: Error & { digest?: string };
  reset: () => void;
}) {
  useEffect(() => {
    console.error(error);
  }, [error]);

  return (
    <div className={cn(
      'min-h-screen flex flex-col items-center justify-center p-4',
      'bg-background text-foreground'
    )}>
      <div className="w-full max-w-md space-y-8">
        <div className="text-center">
          <h2 className="text-2xl font-bold text-destructive">Something went wrong!</h2>
          <p className="mt-2 text-muted-foreground">
            {error.message || 'An unexpected error occurred'}
          </p>
        </div>
        <button
          onClick={reset}
          className={cn(
            'w-full py-2 px-4 rounded-md',
            'bg-primary text-primary-foreground',
            'hover:bg-primary/90',
            'focus:outline-none focus:ring-2 focus:ring-primary focus:ring-offset-2',
            'transition-colors'
          )}
        >
          Try again
        </button>
      </div>
    </div>
  );
} 