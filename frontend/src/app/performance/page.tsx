"use client";

import { useState } from "react";
import { Navbar } from "@/components/navbar";
import { Card, CardTitle, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { checkPerformance } from "@/lib/api";
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
} from "recharts";

export default function PerformancePage() {
  const [url, setUrl] = useState("");
  const [strategy, setStrategy] = useState("mobile");
  const [result, setResult] = useState<any>(null);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setLoading(true);
    setError(null);
    setResult(null);
    try {
      setResult(await checkPerformance(url, strategy));
    } catch {
      setError(
        "PageSpeed Insights is unavailable (often the shared free quota). Set PAGESPEED_API_KEY in backend/.env for reliable access."
      );
    } finally {
      setLoading(false);
    }
  }

  const cards = result
    ? [
        { label: "Score", value: result.score ?? "—" },
        { label: "LCP", value: result.lcp_ms ? `${(result.lcp_ms / 1000).toFixed(1)}s` : "—" },
        { label: "CLS", value: result.cls ?? "—" },
        { label: "FCP", value: result.fcp_ms ? `${(result.fcp_ms / 1000).toFixed(1)}s` : "—" },
        { label: "TBT", value: result.tbt_ms ? `${result.tbt_ms}ms` : "—" },
      ]
    : [];

  return (
    <div className="flex min-h-screen">
      <aside className="hidden md:flex">
        <Navbar />
      </aside>
      <main className="flex-1 p-8">
        <h2 className="text-2xl font-bold mb-6">Core Web Vitals</h2>
        <Card className="mb-6">
          <CardContent>
            <form onSubmit={handleSubmit} className="flex gap-4">
              <Input
                placeholder="https://example.com"
                value={url}
                onChange={(e) => setUrl(e.target.value)}
                className="flex-1"
              />
              <select
                value={strategy}
                onChange={(e) => setStrategy(e.target.value)}
                className="px-4 py-2 rounded-md border border-border-strong bg-bg"
              >
                <option value="mobile">Mobile</option>
                <option value="desktop">Desktop</option>
              </select>
              <Button type="submit" disabled={loading}>
                {loading ? "Measuring..." : "Measure"}
              </Button>
            </form>
            <p className="text-xs text-fg-2 mt-3">
              Real Lighthouse data via Google PageSpeed Insights. This can take 10–30s.
            </p>
          </CardContent>
        </Card>

        {error && (
          <div className="mb-6 p-3 bg-warning-bg text-warning rounded-md text-sm">{error}</div>
        )}

        {result && (
          <div className="space-y-6">
            <div className="grid grid-cols-2 md:grid-cols-5 gap-4">
              {cards.map((c) => (
                <Card key={c.label}>
                  <CardContent>
                    <p className="text-3xl font-bold text-brand">{c.value}</p>
                    <p className="text-xs text-fg-2">{c.label}</p>
                  </CardContent>
                </Card>
              ))}
            </div>

            <Card>
              <CardTitle>Recommendations</CardTitle>
              <CardContent>
                <ul className="space-y-2 text-sm list-disc list-inside text-fg-1">
                  {result.recommendations.map((r: string, i: number) => (
                    <li key={i}>{r}</li>
                  ))}
                </ul>
              </CardContent>
            </Card>

            {result.history.length > 1 && (
              <Card>
                <CardTitle>Performance score trend</CardTitle>
                <CardContent>
                  <div className="h-72 mt-4">
                    <ResponsiveContainer width="100%" height="100%">
                      <LineChart
                        data={result.history.map((h: any) => ({
                          date: String(h.fetched_at).slice(0, 10),
                          score: h.score,
                        }))}
                      >
                        <CartesianGrid strokeDasharray="3 3" />
                        <XAxis dataKey="date" />
                        <YAxis domain={[0, 100]} />
                        <Tooltip />
                        <Line
                          type="monotone"
                          dataKey="score"
                          name="Score"
                          stroke="var(--dk-purple-700)"
                          strokeWidth={2}
                        />
                      </LineChart>
                    </ResponsiveContainer>
                  </div>
                </CardContent>
              </Card>
            )}
          </div>
        )}
      </main>
    </div>
  );
}
