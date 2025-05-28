import Link from 'next/link';
import { cn } from '@/lib/utils';

export default function NotFound() {
  return (
    <div className={cn(
      'min-h-screen flex flex-col items-center justify-center p-4',
      'bg-background text-foreground'
    )}>
      <div className="w-full max-w-md space-y-8 text-center">
        <h2 className="text-2xl font-bold">Page Not Found</h2>
        <p className="text-muted-foreground">
          The page you're looking for doesn't exist or has been moved.
        </p>
        <Link
          href="/"
          className={cn(
            'inline-block py-2 px-4 rounded-md',
            'bg-primary text-primary-foreground',
            'hover:bg-primary/90',
            'focus:outline-none focus:ring-2 focus:ring-primary focus:ring-offset-2',
            'transition-colors'
          )}
        >
          Return Home
        </Link>
      </div>
    </div>
  );
} 