"use client";

import { useState } from "react";
import { Navbar } from "@/components/navbar";
import { Card, CardTitle, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { competitorGap } from "@/lib/api";

export default function CompetitorPage() {
  const [seed, setSeed] = useState("");
  const [url, setUrl] = useState("");
  const [result, setResult] = useState<any>(null);
  const [loading, setLoading] = useState(false);

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setLoading(true);
    try {
      setResult(await competitorGap(seed, url));
    } catch {
      alert("Analysis failed — check the competitor URL.");
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
        <h2 className="text-2xl font-bold mb-6">Competitor Gap Analysis</h2>
        <Card className="mb-6">
          <CardContent>
            <form onSubmit={handleSubmit} className="space-y-4">
              <Input
                placeholder="Your seed topic (e.g. cold brew coffee)"
                value={seed}
                onChange={(e) => setSeed(e.target.value)}
              />
              <Input
                placeholder="Competitor URL (https://competitor.com)"
                value={url}
                onChange={(e) => setUrl(e.target.value)}
              />
              <Button type="submit" disabled={loading}>
                {loading ? "Analyzing..." : "Find Gaps"}
              </Button>
            </form>
          </CardContent>
        </Card>

        {result && (
          <Card>
            <CardTitle>
              {result.gaps.length} content gap(s) vs {result.competitor_url}
            </CardTitle>
            <CardContent>
              {result.note && (
                <div className="mb-3 p-3 bg-info-bg text-info rounded-md text-sm">{result.note}</div>
              )}
              <p className="text-sm text-fg-2 mb-4">
                Your keywords: {result.your_keyword_count} · Competitor topics:{" "}
                {result.competitor_term_count}
              </p>
              <ul className="space-y-2">
                {result.gaps.map((g: any, i: number) => (
                  <li
                    key={i}
                    className="p-3 rounded-md border border-border flex items-start justify-between gap-3"
                  >
                    <div>
                      <span className="font-medium">{g.term}</span>
                      {g.reason && <p className="text-xs text-fg-2 mt-0.5">{g.reason}</p>}
                    </div>
                    <span
                      className={`shrink-0 text-xs font-bold px-2 py-0.5 rounded-pill ${
                        g.opportunity >= 70
                          ? "bg-success-bg text-success"
                          : g.opportunity >= 40
                          ? "bg-warning-bg text-warning"
                          : "bg-bg-muted text-fg-2"
                      }`}
                    >
                      opp {g.opportunity}
                    </span>
                  </li>
                ))}
              </ul>
            </CardContent>
          </Card>
        )}
      </main>
    </div>
  );
}
