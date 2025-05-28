declare module '@/components/Loading' {
  const Loading: React.FC;
  export default Loading;
}

declare module '@/components/Navigation' {
  const Navigation: React.FC;
  export default Navigation;
}

declare module '@/lib/utils' {
  export function cn(...inputs: any[]): string;
} 