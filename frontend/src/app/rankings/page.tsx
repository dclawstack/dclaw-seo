"use client";

import { useState } from "react";
import { Navbar } from "@/components/navbar";
import { Card, CardTitle, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { trackRankings } from "@/lib/api";
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from "recharts";

export default function RankingsPage() {
  const [keyword, setKeyword] = useState("");
  const [url, setUrl] = useState("");
  const [position, setPosition] = useState("");
  const [result, setResult] = useState<any>(null);
  const [loading, setLoading] = useState(false);

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setLoading(true);
    try {
      const pos = position ? Number(position) : undefined;
      const data = await trackRankings(keyword, url, pos);
      setResult(data);
    } catch (err) {
      alert("Tracking failed");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="flex min-h-screen">
      <aside className="hidden md:flex">
        <Navbar />
      </aside>
      <main className="flex-1 p-8">
        <h2 className="text-2xl font-bold mb-6">Rankings Tracker</h2>
        <Card className="mb-6">
          <CardContent>
            <form onSubmit={handleSubmit} className="flex gap-4">
              <Input
                placeholder="Keyword"
                value={keyword}
                onChange={(e) => setKeyword(e.target.value)}
                className="flex-1"
              />
              <Input
                placeholder="URL"
                value={url}
                onChange={(e) => setUrl(e.target.value)}
                className="flex-1"
              />
              <Input
                type="number"
                min={1}
                placeholder="Position (optional)"
                value={position}
                onChange={(e) => setPosition(e.target.value)}
                className="w-44"
              />
              <Button type="submit" disabled={loading}>
                {loading ? "Tracking..." : "Track"}
              </Button>
            </form>
            <p className="text-xs text-fg-2 mt-3">
              Enter an observed SERP position to record a real data point. (A SERP-data provider can
              be configured to fetch positions automatically.)
            </p>
          </CardContent>
        </Card>
        {result && (
          <Card>
            <CardTitle>
              Rankings for &quot;{result.keyword}&quot;
            </CardTitle>
            <CardContent>
              {result.note && (
                <div className="p-3 bg-info-bg text-info rounded-md text-sm">{result.note}</div>
              )}
              {result.alerts?.length > 0 && (
                <ul className="mt-3 space-y-1">
                  {result.alerts.map((a: string, i: number) => (
                    <li key={i} className="p-2 bg-warning-bg text-warning rounded-md text-sm">
                      ⚠ {a}
                    </li>
                  ))}
                </ul>
              )}
              {result.history.length > 0 && (
              <div className="h-80 mt-4">
                <ResponsiveContainer width="100%" height="100%">
                  <LineChart data={result.history}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="date" />
                    <YAxis reversed domain={[1, "dataMax + 5"]} />
                    <Tooltip />
                    <Legend />
                    <Line
                      type="monotone"
                      dataKey="position"
                      name="Your Position"
                      stroke="var(--dk-purple-700)"
                      strokeWidth={2}
                    />
                    <Line
                      type="monotone"
                      dataKey="competitor_position"
                      name="Competitor"
                      stroke="var(--dk-danger)"
                      strokeWidth={2}
                    />
                  </LineChart>
                </ResponsiveContainer>
              </div>
              )}
            </CardContent>
          </Card>
        )}
      </main>
    </div>
  );
}
