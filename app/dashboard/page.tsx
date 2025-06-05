'use client';

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Loading } from '@/components/ui/loading';
import { Line, Pie } from 'react-chartjs-2';
import {
  Chart as ChartJS,
  LineElement,
  PointElement,
  LinearScale,
  CategoryScale,
  Tooltip,
  Legend,
  ArcElement,
} from 'chart.js';
import { getCookie } from 'cookies-next';

ChartJS.register(
  LineElement,
  PointElement,
  LinearScale,
  CategoryScale,
  Tooltip,
  Legend,
  ArcElement
);

interface PortfolioData {
  totalValue: number;
  history: { timestamp: string; value: number }[];
  assets: { symbol: string; value: number; percentage: number }[];
}

interface TradeMetrics {
  totalTrades: number;
  successfulTrades: number;
  winRate: number;
  averageReturn: number;
  totalProfit: number;
}

interface RecentTrade {
  id: string;
  symbol: string;
  side: 'buy' | 'sell';
  amount: number;
  price: number;
  timestamp: string;
  status: string;
}

export default function DashboardPage() {
  const router = useRouter();
  const [loading, setLoading] = useState(true);
  const [portfolioData, setPortfolioData] = useState<PortfolioData>({
    totalValue: 0,
    history: [],
    assets: []
  });
  const [tradeMetrics, setTradeMetrics] = useState<TradeMetrics>({
    totalTrades: 0,
    successfulTrades: 0,
    winRate: 0,
    averageReturn: 0,
    totalProfit: 0
  });
  const [recentTrades, setRecentTrades] = useState<RecentTrade[]>([]);

  useEffect(() => {
    const token = getCookie('token');
    console.log("Token from cookie:", token);

    if (!token) {
      console.warn("No token found, redirecting to login.");
      router.push('/login');
      return;
    }

    const fetchDashboardData = async () => {
      try {
        // Fetch portfolio data
        console.log("Fetching portfolio data...");
        const portfolioResponse = await fetch('http://localhost:8084/trades/portfolio', {
          headers: { 'Authorization': `Bearer ${token}` }
        });
        console.log("Portfolio response status:", portfolioResponse.status);
        if (portfolioResponse.ok) {
          const portfolioData = await portfolioResponse.json();
          console.log("Portfolio data:", portfolioData);
          setPortfolioData(portfolioData);
        } else {
          const errorData = await portfolioResponse.json().catch(() => ({}));
          console.error("Portfolio fetch error:", errorData);
        }

        // Fetch trade metrics
        console.log("Fetching trade metrics...");
        const metricsResponse = await fetch('http://localhost:8084/trades/metrics', {
          headers: { 'Authorization': `Bearer ${token}` }
        });
        console.log("Metrics response status:", metricsResponse.status);
        if (metricsResponse.ok) {
          const metricsData = await metricsResponse.json();
          console.log("Trade metrics data:", metricsData);
          setTradeMetrics(metricsData);
        } else {
          const errorData = await metricsResponse.json().catch(() => ({}));
          console.error("Metrics fetch error:", errorData);
        }

        // Fetch recent trades
        console.log("Fetching recent trades...");
        const tradesResponse = await fetch('http://localhost:8084/trades/recent', {
          headers: { 'Authorization': `Bearer ${token}` }
        });
        console.log("Recent trades response status:", tradesResponse.status);
        if (tradesResponse.ok) {
          const tradesData = await tradesResponse.json();
          console.log("Recent trades data:", tradesData);
          setRecentTrades(tradesData);
        } else {
          const errorData = await tradesResponse.json().catch(() => ({}));
          console.error("Recent trades fetch error:", errorData);
        }
      } catch (error) {
        console.error('Error fetching dashboard data:', error);
      } finally {
        setLoading(false);
        console.log("Dashboard loading complete.");
      }
    };

    fetchDashboardData();
  }, [router]);

  useEffect(() => {
    console.log("PortfolioData state updated:", portfolioData);
  }, [portfolioData]);

  useEffect(() => {
    console.log("TradeMetrics state updated:", tradeMetrics);
  }, [tradeMetrics]);

  useEffect(() => {
    console.log("RecentTrades state updated:", recentTrades);
  }, [recentTrades]);

  if (loading) {
    console.log("Loading dashboard...");
    return (
      <div className="min-h-screen flex items-center justify-center">
        <Loading size="lg" />
      </div>
    );
  }

  const portfolioChartData = {
    labels: portfolioData.history.map(h => new Date(h.timestamp).toLocaleDateString()),
    datasets: [{
      label: 'Portfolio Value',
      data: portfolioData.history.map(h => h.value),
      borderColor: 'rgb(59, 130, 246)',
      backgroundColor: 'rgba(59, 130, 246, 0.2)',
      tension: 0.3,
    }]
  };

  const assetAllocationData = {
    labels: portfolioData.assets.map(a => a.symbol),
    datasets: [{
      data: portfolioData.assets.map(a => a.value),
      backgroundColor: [
        'rgba(59, 130, 246, 0.8)',
        'rgba(16, 185, 129, 0.8)',
        'rgba(245, 158, 11, 0.8)',
        'rgba(239, 68, 68, 0.8)',
        'rgba(139, 92, 246, 0.8)',
      ],
    }]
  };

  console.log("Rendering dashboard with data:", {
    portfolioData,
    tradeMetrics,
    recentTrades
  });

  return (
    <div className="min-h-screen bg-gray-50 p-8">
      <div className="max-w-7xl mx-auto">
        <h1 className="text-3xl font-bold mb-8">Dashboard</h1>

        {/* Portfolio Overview */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
          <Card>
            <CardHeader>
              <CardTitle>Total Portfolio Value</CardTitle>
            </CardHeader>
            <CardContent>
              <p className="text-2xl font-bold">${portfolioData.totalValue.toFixed(2)}</p>
            </CardContent>
          </Card>
          <Card>
            <CardHeader>
              <CardTitle>Total Trades</CardTitle>
            </CardHeader>
            <CardContent>
              <p className="text-2xl font-bold">{tradeMetrics.totalTrades}</p>
            </CardContent>
          </Card>
          <Card>
            <CardHeader>
              <CardTitle>Win Rate</CardTitle>
            </CardHeader>
            <CardContent>
              <p className="text-2xl font-bold">{tradeMetrics.winRate.toFixed(1)}%</p>
            </CardContent>
          </Card>
          <Card>
            <CardHeader>
              <CardTitle>Total Profit</CardTitle>
            </CardHeader>
            <CardContent>
              <p className={`text-2xl font-bold ${tradeMetrics.totalProfit >= 0 ? 'text-green-500' : 'text-red-500'}`}>
                ${tradeMetrics.totalProfit.toFixed(2)}
              </p>
            </CardContent>
          </Card>
        </div>

        {/* Charts */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
          <Card>
            <CardHeader>
              <CardTitle>Portfolio Value Over Time</CardTitle>
            </CardHeader>
            <CardContent>
              <Line data={portfolioChartData} options={{ responsive: true }} />
            </CardContent>
          </Card>
          <Card>
            <CardHeader>
              <CardTitle>Asset Allocation</CardTitle>
            </CardHeader>
            <CardContent>
              <Pie data={assetAllocationData} options={{ responsive: true }} />
            </CardContent>
          </Card>
        </div>

        {/* Recent Trades */}
        <Card>
          <CardHeader>
            <CardTitle>Recent Trades</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="overflow-x-auto">
              <table className="min-w-full divide-y divide-gray-200">
                <thead>
                  <tr>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Symbol</th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Side</th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Amount</th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Price</th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Status</th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Time</th>
                  </tr>
                </thead>
                <tbody className="bg-white divide-y divide-gray-200">
                  {recentTrades.map((trade) => (
                    <tr key={trade.id}>
                      <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">{trade.symbol}</td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm">
                        <span className={`px-2 inline-flex text-xs leading-5 font-semibold rounded-full ${
                          trade.side === 'buy' ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'
                        }`}>
                          {trade.side.toUpperCase()}
                        </span>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">{trade.amount}</td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">${trade.price.toFixed(2)}</td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm">
                        <span className={`px-2 inline-flex text-xs leading-5 font-semibold rounded-full ${
                          trade.status === 'executed' ? 'bg-green-100 text-green-800' :
                          trade.status === 'failed' ? 'bg-red-100 text-red-800' :
                          'bg-yellow-100 text-yellow-800'
                        }`}>
                          {trade.status.toUpperCase()}
                        </span>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                        {new Date(trade.timestamp).toLocaleString()}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}