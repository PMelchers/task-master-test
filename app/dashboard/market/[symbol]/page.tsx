'use client';

import { useEffect, useState } from 'react';
import { useRouter, useParams } from 'next/navigation';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card';
import { getCookie } from 'cookies-next';
import { Alert, AlertTitle, AlertDescription } from '../../../../app/components/ui/alert';

interface OrderBook {
  symbol: string;
  bids: [number, number][];
  asks: [number, number][];
  timestamp: number;
  datetime: string;
  nonce: number;
}

interface MarketSummary {
  symbol: string;
  last_price: number;
  '24h_high': number;
  '24h_low': number;
  '24h_volume': number;
  bid?: number | null;
  ask?: number | null;
  timestamp?: string;
  order_book?: OrderBook;
}

export default function MarketDetailPage() {
  const router = useRouter();
  const params = useParams();
  const symbol = decodeURIComponent(params.symbol as string);
  const [data, setData] = useState<MarketSummary | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const token = getCookie('token');
    if (!token) {
      router.push('/login');
      return;
    }
    const fetchData = async () => {
      try {
        const res = await fetch(`http://localhost:8084/market-data/summary/${encodeURIComponent(symbol)}`, {
          headers: { 'Authorization': `Bearer ${token}` }
        });
        if (res.ok) {
          setData(await res.json());
        } else {
          setError(`Failed to fetch market summary for ${symbol}.`);
        }
      } catch (err) {
        setError('An error occurred while fetching market data.');
      } finally {
        setLoading(false);
      }
    };
    fetchData();
  }, [router, symbol]);

  if (loading) return <div>Loading...</div>;
  if (error) {
    return (
      <div className="max-w-xl mx-auto mt-8">
        <Alert variant="destructive">
          <AlertTitle>Error</AlertTitle>
          <AlertDescription>{error}</AlertDescription>
        </Alert>
      </div>
    );
  }
  if (!data) {
    return (
      <div className="max-w-xl mx-auto mt-8">
        <Alert variant="destructive">
          <AlertTitle>Not found</AlertTitle>
          <AlertDescription>No data available for this symbol.</AlertDescription>
        </Alert>
      </div>
    );
  }

  return (
    <div className="max-w-xl mx-auto mt-8">
      <Card>
        <CardHeader>
          <CardTitle>{data.symbol} Details</CardTitle>
          <CardDescription>Last updated: {data.timestamp}</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="space-y-2">
            <div>Last Price: ${data.last_price?.toFixed(6)}</div>
            <div>24h High: ${data['24h_high']?.toFixed(6)}</div>
            <div>24h Low: ${data['24h_low']?.toFixed(6)}</div>
            <div>24h Volume: {data['24h_volume']?.toFixed(2)}</div>
            <div>Bid: {data.bid ?? '-'}</div>
            <div>Ask: {data.ask ?? '-'}</div>
            <div>Timestamp: {data.timestamp}</div>
            {data.order_book && (
              <>
                <div className="font-semibold mt-4">Order Book</div>
                <div>Order Book Symbol: {data.order_book.symbol}</div>
                <div>Order Book Datetime: {data.order_book.datetime}</div>
                <div>Order Book Nonce: {data.order_book.nonce}</div>
                <div className="mt-2">
                  <div className="font-semibold">Top 5 Bids</div>
                  <ul>
                    {data.order_book.bids.slice(0, 5).map(([price, amount], idx) => (
                      <li key={idx}>Price: {price}, Amount: {amount}</li>
                    ))}
                  </ul>
                </div>
                <div className="mt-2">
                  <div className="font-semibold">Top 5 Asks</div>
                  <ul>
                    {data.order_book.asks.slice(0, 5).map(([price, amount], idx) => (
                      <li key={idx}>Price: {price}, Amount: {amount}</li>
                    ))}
                  </ul>
                </div>
              </>
            )}
          </div>
        </CardContent>
      </Card>
    </div>
  );
}