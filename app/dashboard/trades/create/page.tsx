'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '../../../../app/components/ui/button';
import { Input } from '../../../../app/components/ui/input';
import { Label } from '../../../../app/components/ui/label';
import { Alert, AlertDescription } from '../../../../app/components/ui/alert';
import { getCookie } from 'cookies-next';

export default function CreateTradePage() {
  const router = useRouter();
  const [symbol, setSymbol] = useState('');
  const [buyTime, setBuyTime] = useState('');
  const [sellTime, setSellTime] = useState('');
  const [amount, setAmount] = useState(1);
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    const token = getCookie('token');
    if (!token) {
      router.push('/login');
      return;
    }

    try {
      const response = await fetch('http://localhost:8084/trades/scheduled', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`,
        },
        body: JSON.stringify({
          trading_pair: symbol,
          amount,
          buy_time: buyTime,
          sell_time: sellTime,
        }),
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.detail || 'Failed to create trade');
      }

      router.push('/dashboard/trades');
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An error occurred');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gray-50 p-8">
      <div className="max-w-2xl mx-auto">
        <Card>
          <CardHeader>
            <CardTitle>Create Scheduled Trade</CardTitle>
            <CardDescription>Schedule a new cryptocurrency trade</CardDescription>
          </CardHeader>
          <form onSubmit={handleSubmit}>
            <CardContent>
              <div className="grid w-full items-center gap-4">
                <div className="flex flex-col space-y-1.5">
                  <Label htmlFor="symbol">Trading Pair</Label>
                  <Input
                    id="symbol"
                    placeholder="e.g., BTC/USDT"
                    value={symbol}
                    onChange={(e) => setSymbol(e.target.value)}
                    required
                  />
                </div>
                <div className="flex flex-col space-y-1.5">
                  <Label htmlFor="amount">Amount</Label>
                  <Input
                    id="amount"
                    type="number"
                    min="0"
                    step="any"
                    value={amount}
                    onChange={(e) => setAmount(Number(e.target.value))}
                    required
                  />
                </div>
                <div className="flex flex-col space-y-1.5">
                  <Label htmlFor="buyTime">Buy Time</Label>
                  <Input
                    id="buyTime"
                    type="datetime-local"
                    value={buyTime}
                    onChange={(e) => setBuyTime(e.target.value)}
                    required
                  />
                </div>
                <div className="flex flex-col space-y-1.5">
                  <Label htmlFor="sellTime">Sell Time</Label>
                  <Input
                    id="sellTime"
                    type="datetime-local"
                    value={sellTime}
                    onChange={(e) => setSellTime(e.target.value)}
                    required
                  />
                </div>
                {error && (
                  <Alert variant="destructive">
                    <AlertDescription>{error}</AlertDescription>
                  </Alert>
                )}
              </div>
            </CardContent>
            <CardFooter className="flex justify-between">
              <Button
                type="button"
                variant="outline"
                onClick={() => router.push('/dashboard/trades')}
              >
                Cancel
              </Button>
              <Button type="submit" disabled={loading}>
                {loading ? 'Creating...' : 'Create Trade'}
              </Button>
            </CardFooter>
          </form>
        </Card>
      </div>
    </div>
  );
}