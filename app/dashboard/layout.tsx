'use client';

import { Navigation } from '@/components/ui/navigation';

export default function DashboardLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <div className="min-h-screen bg-gray-50">
      <Navigation />
      <main className="py-10">
        {children}
      </main>
    </div>
  );
} 