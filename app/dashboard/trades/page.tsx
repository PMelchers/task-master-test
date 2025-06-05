'use client';

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import Link from 'next/link';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Loading } from '@/components/ui/loading';
import { useWebSocket } from '@/hooks/useWebSocket';
import { getCookie } from 'cookies-next';

interface ScheduledTrade {
  id: string;
  trading_pair: string;
  amount: number;
  buy_time: string;
  sell_time: string;
  created_at: string;
  status?: string;
  price?: number;
}

interface WebSocketMessage {
  type: string;
  trade_id: string;
  data: {
    status: ScheduledTrade['status'];
    executed_price?: number;
    executed_time?: string;
  };
}

export default function TradesPage() {
  const router = useRouter();
  const [trades, setTrades] = useState<ScheduledTrade[]>([]);
  const [loading, setLoading] = useState(true);

  const token = getCookie('token');
  const wsUrl = token
    ? `ws://localhost:8084/ws/trade-updates?token=${token}`
    : 'ws://localhost:8084/ws/trade-updates';

  const { lastMessage, isConnected } = useWebSocket<WebSocketMessage>(wsUrl);

  useEffect(() => {
    if (!token) {
      router.push('/login');
      return;
    }

    const fetchTrades = async () => {
      try {
        const response = await fetch('http://localhost:8084/trades/scheduled', {
          headers: {
            'Authorization': `Bearer ${token}`,
          },
        });

        if (!response.ok) {
          throw new Error('Failed to fetch scheduled trades');
        }

        const data = await response.json();
        setTrades(data);
      } catch (error) {
        console.error('Error fetching scheduled trades:', error);
      } finally {
        setLoading(false);
      }
    };

    fetchTrades();
  }, [router, token]);

  useEffect(() => {
    if (lastMessage && lastMessage.type === 'trade_update') {
      const { trade_id, data } = lastMessage;
      setTrades(prev => prev.map(trade => 
        trade.id === trade_id
          ? {
              ...trade,
              status: data.status,
              price: data.executed_price || trade.price,
              executed_time: data.executed_time
            }
          : trade
      ));
    }
  }, [lastMessage]);

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <Loading size="lg" />
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50 p-8">
      <div className="max-w-7xl mx-auto">
        <div className="flex justify-between items-center mb-8">
          <div>
            <h1 className="text-3xl font-bold">Scheduled Trades</h1>
            <p className="text-sm text-gray-500 mt-1">
              {isConnected ? 'Connected to real-time updates' : 'Disconnected from real-time updates'}
            </p>
          </div>
          <Link
            href="/dashboard/trades/create"
            className="bg-blue-500 text-white px-4 py-2 rounded-md hover:bg-blue-600 transition-colors"
          >
            Create New Trade
          </Link>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {trades.map((trade) => (
            <Card key={trade.id}>
              <CardHeader>
                <CardTitle>{trade.trading_pair}</CardTitle>
                <CardDescription>
                  Scheduled Trade
                </CardDescription>
              </CardHeader>
              <CardContent>
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <p className="text-sm text-gray-500">Amount</p>
                    <p>{trade.amount}</p>
                  </div>
                  <div>
                    <p className="text-sm text-gray-500">Buy Time</p>
                    <p>{new Date(trade.buy_time).toLocaleString()}</p>
                  </div>
                  <div>
                    <p className="text-sm text-gray-500">Sell Time</p>
                    <p>{new Date(trade.sell_time).toLocaleString()}</p>
                  </div>
                  <div>
                    <p className="text-sm text-gray-500">Created At</p>
                    <p>{new Date(trade.created_at).toLocaleString()}</p>
                  </div>
                  {trade.status && (
                    <div>
                      <p className="text-sm text-gray-500">Status</p>
                      <p>{trade.status.toUpperCase()}</p>
                    </div>
                  )}
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      </div>
    </div>
  );
}