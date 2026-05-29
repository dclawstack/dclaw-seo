"use client";

import { useState } from "react";
import { Navbar } from "@/components/navbar";
import { Card, CardTitle, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { forecastRank } from "@/lib/api";

const TREND_COLOR: Record<string, string> = {
  improving: "text-success",
  declining: "text-danger",
  stable: "text-fg-1",
  insufficient_data: "text-fg-2",
};

export default function ForecastPage() {
  const [keyword, setKeyword] = useState("");
  const [url, setUrl] = useState("");
  const [result, setResult] = useState<any>(null);
  const [loading, setLoading] = useState(false);

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setLoading(true);
    try {
      setResult(await forecastRank(keyword, url));
    } catch {
      alert("Forecast failed");
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
        <h2 className="text-2xl font-bold mb-6">Predictive Rank Forecasting</h2>
        <Card className="mb-6">
          <CardContent>
            <form onSubmit={handleSubmit} className="flex flex-wrap gap-4">
              <Input placeholder="Keyword" value={keyword} onChange={(e) => setKeyword(e.target.value)} className="flex-1 min-w-[200px]" />
              <Input placeholder="URL" value={url} onChange={(e) => setUrl(e.target.value)} className="flex-1 min-w-[220px]" />
              <Button type="submit" disabled={loading}>{loading ? "..." : "Forecast"}</Button>
            </form>
          </CardContent>
        </Card>

        {result && (
          <div className="space-y-6">
            {result.note && <div className="p-3 bg-info-bg text-info rounded-md text-sm">{result.note}</div>}
            <Card>
              <CardTitle>Outlook for &quot;{result.keyword}&quot;</CardTitle>
              <CardContent>
                <div className="flex flex-wrap gap-6 text-sm mb-4">
                  <span>Trend: <b className={TREND_COLOR[result.trend] || ""}>{result.trend.replace("_", " ")}</b></span>
                  <span>Confidence: <b>{result.confidence}</b></span>
                  <span>Data points: <b>{result.data_points}</b></span>
                  {result.current_position != null && <span>Current: <b>#{result.current_position}</b></span>}
                  {result.competitor_pressure && <span>Competitor: <b>{result.competitor_pressure}</b></span>}
                </div>
                {result.forecast.length > 0 && (
                  <table className="text-sm w-full max-w-sm">
                    <thead>
                      <tr className="text-fg-2 text-left"><th className="py-1">Check ahead</th><th className="py-1 text-right">Projected position</th></tr>
                    </thead>
                    <tbody>
                      {result.forecast.map((p: any) => (
                        <tr key={p.step} className="border-b border-border">
                          <td className="py-1">+{p.step}</td>
                          <td className="py-1 text-right font-medium">#{p.position}</td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                )}
              </CardContent>
            </Card>
          </div>
        )}
      </main>
    </div>
  );
}
