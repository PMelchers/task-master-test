'use client';

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { Loading } from '@/components/ui/loading';
import { useWebSocket } from '@/hooks/useWebSocket';
import { getCookie } from 'cookies-next';
import { Line } from 'react-chartjs-2';
import {
  Chart as ChartJS,
  LineElement,
  PointElement,
  LinearScale,
  CategoryScale,
  Tooltip,
  Legend,
} from 'chart.js';

ChartJS.register(LineElement, PointElement, LinearScale, CategoryScale, Tooltip, Legend);

interface MarketData {
  symbol: string;
  last: number;
  high: number;
  low: number;
  volume: number;
  change: number;
}

interface WebSocketMessage {
  type: string;
  symbol: string;
  data: {
    price: number;
    high: number;
    low: number;
    volume: number;
    timestamp?: string;
  };
}

interface PriceHistory {
  [symbol: string]: { price: number; timestamp: string }[];
}

export default function MarketPage() {
  const router = useRouter();
  const [marketData, setMarketData] = useState<Record<string, MarketData>>({});
  const [loading, setLoading] = useState(true);
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedSymbol, setSelectedSymbol] = useState<string>('BTC/USDT');
  const [priceHistory, setPriceHistory] = useState<PriceHistory>({});

  const { lastMessage, isConnected } = useWebSocket<WebSocketMessage>('ws://localhost:8080/ws/market-data');

  useEffect(() => {
    const token = getCookie('token');
    if (!token) {
      router.push('/login');
      return;
    }

    const fetchInitialMarketData = async () => {
      try {
        const response = await fetch('http://localhost:8080/market-data/trading-pairs', {
          headers: {
            'Authorization': `Bearer ${token}`,
          },
        });

        if (!response.ok) {
          throw new Error('Failed to fetch market data');
        }

        const data = await response.json();
        const initialData: Record<string, MarketData> = {};
        data.forEach((symbol: string) => {
          initialData[symbol] = {
            symbol,
            last: 0,
            high: 0,
            low: 0,
            volume: 0,
            change: 0
          };
        });
        setMarketData(initialData);
        if (data.length > 0) setSelectedSymbol(data[0]);
      } catch (error) {
        console.error('Error fetching market data:', error);
      } finally {
        setLoading(false);
      }
    };

    fetchInitialMarketData();
  }, [router]);

  useEffect(() => {
    if (lastMessage && lastMessage.type === 'market_data') {
      const { symbol, data } = lastMessage;
      setMarketData(prev => ({
        ...prev,
        [symbol]: {
          ...prev[symbol],
          last: data.price,
          high: data.high,
          low: data.low,
          volume: data.volume
        }
      }));
      if (typeof data.timestamp === 'string') {
        setPriceHistory(prev => {
          const history = prev[symbol] ? [...prev[symbol]] : [];
          history.push({ price: data.price, timestamp: data.timestamp! });
          // Keep only the last 50 points
          return { ...prev, [symbol]: history.slice(-50) };
        });
      }
    }
  }, [lastMessage]);

  const filteredData = Object.values(marketData).filter((data) =>
    data.symbol.toLowerCase().includes(searchQuery.toLowerCase())
  );

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <Loading size="lg" />
      </div>
    );
  }

  const chartData = priceHistory[selectedSymbol] || [];
  const lineData = {
    labels: chartData.map((d) => new Date(d.timestamp).toLocaleTimeString()),
    datasets: [
      {
        label: `${selectedSymbol} Price`,
        data: chartData.map((d) => d.price),
        borderColor: 'rgb(59, 130, 246)',
        backgroundColor: 'rgba(59, 130, 246, 0.2)',
        tension: 0.3,
      },
    ],
  };

  return (
    <div className="min-h-screen bg-gray-50 p-8">
      <div className="max-w-7xl mx-auto">
        <div className="flex justify-between items-center mb-8">
          <div>
            <h1 className="text-3xl font-bold">Market Data</h1>
            <p className="text-sm text-gray-500 mt-1">
              {isConnected ? 'Connected to real-time updates' : 'Disconnected from real-time updates'}
            </p>
          </div>
          <div className="w-64">
            <Input
              placeholder="Search trading pairs..."
              value={searchQuery}
              onChange={(e: React.ChangeEvent<HTMLInputElement>) => setSearchQuery(e.target.value)}
            />
          </div>
        </div>

        <div className="mb-8">
          <div className="flex items-center space-x-4 mb-2">
            <span className="font-semibold">Select Pair:</span>
            <select
              className="border rounded px-2 py-1"
              value={selectedSymbol}
              onChange={(e) => setSelectedSymbol(e.target.value)}
            >
              {Object.keys(marketData).map((symbol) => (
                <option key={symbol} value={symbol}>{symbol}</option>
              ))}
            </select>
          </div>
          <div className="bg-white rounded-lg shadow p-4">
            <Line data={lineData} options={{ responsive: true, plugins: { legend: { display: true } } }} />
          </div>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {filteredData.map((data) => (
            <Card key={data.symbol}>
              <CardHeader>
                <CardTitle>{data.symbol}</CardTitle>
                <CardDescription>
                  Last Price: ${data.last.toFixed(2)}
                </CardDescription>
              </CardHeader>
              <CardContent>
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <p className="text-sm text-gray-500">24h High</p>
                    <p>${data.high.toFixed(2)}</p>
                  </div>
                  <div>
                    <p className="text-sm text-gray-500">24h Low</p>
                    <p>${data.low.toFixed(2)}</p>
                  </div>
                  <div>
                    <p className="text-sm text-gray-500">24h Volume</p>
                    <p>{data.volume.toFixed(2)}</p>
                  </div>
                  <div>
                    <p className="text-sm text-gray-500">24h Change</p>
                    <p className={data.change >= 0 ? 'text-green-500' : 'text-red-500'}>
                      {data.change >= 0 ? '+' : ''}{data.change.toFixed(2)}%
                    </p>
                  </div>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      </div>
    </div>
  );
} 