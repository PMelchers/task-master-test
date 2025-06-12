'use client';

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import Link from 'next/link';
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
  last_price: number;
  '24h_high': number;
  '24h_low': number;
  '24h_volume': number;
  '24h_change': number;
  bid?: number | null;
  ask?: number | null;
  timestamp?: string;
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

  const token = getCookie('token');
  const wsUrl = token
    ? `ws://localhost:8084/ws/market-data?token=${token}`
    : 'ws://localhost:8084/ws/market-data';

  const { lastMessage, isConnected } = useWebSocket<WebSocketMessage>(wsUrl);

  useEffect(() => {
    const token = getCookie('token');
    if (!token) {
      router.push('/login');
      return;
    }

    const fetchInitialMarketData = async () => {
      try {
        const response = await fetch('http://localhost:8084/market-data/trading-pairs', {
          headers: { 'Authorization': `Bearer ${token}` }
        });

        if (!response.ok) {
          throw new Error('Failed to fetch market data');
        }

        let symbols = await response.json();
        symbols = symbols.slice(0, 6); // Limit to 5 coins

        const initialData: Record<string, MarketData> = {};

        // Fetch summary for each symbol in parallel
        await Promise.all(
          symbols.map(async (symbol: string) => {
            const summaryRes = await fetch(`http://localhost:8084/market-data/summary/${encodeURIComponent(symbol)}`, {
              headers: { 'Authorization': `Bearer ${token}` }
            });
            if (summaryRes.ok) {
              const summary = await summaryRes.json();
              initialData[symbol] = summary;
            } else {
              // fallback to zeros if error
              initialData[symbol] = {
                symbol,
                last_price: 0,
                '24h_high': 0,
                '24h_low': 0,
                '24h_volume': 0,
                '24h_change': 0,
                bid: null,
                ask: null,
                timestamp: ''
              };
            }
          })
        );

        setMarketData(initialData);
        if (symbols.length > 0) setSelectedSymbol(symbols[0]);
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
          last_price: data.price,
          '24h_high': data.high,
          '24h_low': data.low,
          '24h_volume': data.volume
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
            <Link key={data.symbol} href={`/dashboard/market/${encodeURIComponent(data.symbol)}`}>
              <Card className="cursor-pointer hover:shadow-lg transition-shadow">
                <CardHeader>
                  <CardTitle>{data.symbol}</CardTitle>
                  <CardDescription>
                    Last Price: ${data.last_price !== undefined && data.last_price !== null ? data.last_price.toString() : '0'}
                  </CardDescription>
                </CardHeader>
                <CardContent>
                  <div className="grid grid-cols-2 gap-4">
                    <div>
                      <p className="text-sm text-gray-500">24h High</p>
                      <p>${data['24h_high'] !== undefined && data['24h_high'] !== null ? data['24h_high'].toString() : '0'}</p>
                    </div>
                    <div>
                      <p className="text-sm text-gray-500">24h Low</p>
                      <p>${data['24h_low'] !== undefined && data['24h_low'] !== null ? data['24h_low'].toString() : '0'}</p>
                    </div>
                    <div>
                      <p className="text-sm text-gray-500">24h Volume</p>
                      <p>{data['24h_volume'] !== undefined && data['24h_volume'] !== null ? data['24h_volume'].toString() : '0'}</p>
                    </div>
                  </div>
                </CardContent>
              </Card>
            </Link>
          ))}
        </div>
      </div>
    </div>
  );
}