'use client';

import { useEffect, useState } from 'react';
import { getCookie } from 'cookies-next';
import { Card, CardHeader, CardTitle, CardContent, CardFooter } from '@/components/ui/card';
import { Button } from '../../components/ui/button';
import { Input } from '@/components/ui/input';
import { Alert, AlertDescription } from '../../components/ui/alert';

interface Strategy {
  id: number;
  name: string;
  description: string;
}

export default function StrategiesPage() {
  const [strategies, setStrategies] = useState<Strategy[]>([]);
  const [myStrategies, setMyStrategies] = useState<number[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [name, setName] = useState('');
  const [description, setDescription] = useState('');
  const [creating, setCreating] = useState(false);
  const token = getCookie('token');

  useEffect(() => {
    if (!token) return;
    const fetchStrategies = async () => {
      try {
        const [allRes, myRes] = await Promise.all([
          fetch('http://localhost:8084/strategies/', { headers: { Authorization: `Bearer ${token}` } }),
          fetch('http://localhost:8084/strategies/my', { headers: { Authorization: `Bearer ${token}` } }),
        ]);
        if (!allRes.ok || !myRes.ok) throw new Error('Failed to fetch strategies');
        const all = await allRes.json();
        const mine = await myRes.json();
        setStrategies(all);
        setMyStrategies(mine.map((s: Strategy) => s.id));
      } catch (e) {
        setError('Could not load strategies.');
      } finally {
        setLoading(false);
      }
    };
    fetchStrategies();
  }, [token]);

  const handleSubscribe = async (id: number) => {
    if (!token) return;
    try {
      const res = await fetch(`http://localhost:8084/strategies/${id}/subscribe`, {
        method: 'POST',
        headers: { Authorization: `Bearer ${token}` },
      });
      if (!res.ok) throw new Error();
      setMyStrategies((prev) => [...prev, id]);
    } catch {
      setError('Failed to subscribe.');
    }
  };

  const handleCreate = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    setCreating(true);
    try {
      const res = await fetch('http://localhost:8084/strategies/', {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ name, description }),
      });
      if (!res.ok) {
        const data = await res.json();
        throw new Error(data.detail || 'Failed to create strategy');
      }
      setName('');
      setDescription('');
      // Refresh strategies list
      const allRes = await fetch('http://localhost:8084/strategies/', { headers: { Authorization: `Bearer ${token}` } });
      if (allRes.ok) {
        setStrategies(await allRes.json());
      }
    } catch (e: any) {
      setError(e.message || 'Failed to create strategy');
    } finally {
      setCreating(false);
    }
  };

  if (loading) return <div>Loading...</div>;
  if (error) return <Alert variant="destructive"><AlertDescription>{error}</AlertDescription></Alert>;

  return (
    <div className="max-w-2xl mx-auto mt-8">
      <h1 className="text-2xl font-bold mb-4">Strategies</h1>

      <form onSubmit={handleCreate} className="mb-8 bg-white rounded-lg shadow p-4 space-y-4">
        <div>
          <label className="block font-medium mb-1" htmlFor="strategy-name">Name</label>
          <Input
            id="strategy-name"
            value={name}
            onChange={e => setName(e.target.value)}
            required
            placeholder="Strategy Name"
          />
        </div>
        <div>
          <label className="block font-medium mb-1" htmlFor="strategy-description">Description</label>
          <Input
            id="strategy-description"
            value={description}
            onChange={e => setDescription(e.target.value)}
            required
            placeholder="Strategy Description"
          />
        </div>
        <Button type="submit" disabled={creating || !name || !description}>
          {creating ? 'Creating...' : 'Add Strategy'}
        </Button>
      </form>

      <div className="grid gap-4">
        {strategies.map((strategy) => (
          <Card key={strategy.id}>
            <CardHeader>
              <CardTitle>{strategy.name}</CardTitle>
            </CardHeader>
            <CardContent>
              <p>{strategy.description}</p>
            </CardContent>
            <CardFooter>
              {myStrategies.includes(strategy.id) ? (
                <span className="text-green-600 font-semibold">Subscribed</span>
              ) : (
                <Button onClick={() => handleSubscribe(strategy.id)}>Subscribe</Button>
              )}
            </CardFooter>
          </Card>
        ))}
      </div>
    </div>
  );
}