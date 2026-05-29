"use client";

import { useState } from "react";
import { Navbar } from "@/components/navbar";
import { Card, CardTitle, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input, TextArea } from "@/components/ui/input";
import { analyzeBacklinks } from "@/lib/api";

export default function BacklinksPage() {
  const [target, setTarget] = useState("");
  const [raw, setRaw] = useState("");
  const [result, setResult] = useState<any>(null);
  const [loading, setLoading] = useState(false);

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setLoading(true);
    // Each line: "source_url" or "source_url, anchor text"
    const links = raw
      .split("\n")
      .map((l) => l.trim())
      .filter(Boolean)
      .map((l) => {
        const [source_url, ...rest] = l.split(",");
        return { source_url: source_url.trim(), anchor_text: rest.join(",").trim() || undefined };
      });
    try {
      setResult(await analyzeBacklinks(target, links));
    } catch {
      alert("Analysis failed");
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
        <h2 className="text-2xl font-bold mb-6">Backlink Analysis</h2>
        <Card className="mb-6">
          <CardContent>
            <form onSubmit={handleSubmit} className="space-y-4">
              <Input
                placeholder="Target URL (your site)"
                value={target}
                onChange={(e) => setTarget(e.target.value)}
              />
              <TextArea
                rows={6}
                placeholder={"One backlink per line:\nhttps://referring-site.com/page, anchor text"}
                value={raw}
                onChange={(e) => setRaw(e.target.value)}
              />
              <Button type="submit" disabled={loading}>
                {loading ? "Analyzing..." : "Analyze"}
              </Button>
            </form>
            <p className="text-xs text-fg-2 mt-3">
              Paste backlinks to score toxicity. Connect a backlink-data provider for automatic
              discovery; configure an LLM in Settings for AI-refined scoring.
            </p>
          </CardContent>
        </Card>

        {result && (
          <Card>
            <CardTitle>
              {result.total} backlink(s) for &quot;{result.target_url}&quot;
            </CardTitle>
            <CardContent>
              {result.note && (
                <div className="mb-3 p-3 bg-info-bg text-info rounded-md text-sm">{result.note}</div>
              )}
              <div className="flex gap-6 text-sm mb-4">
                <span><b className="text-danger">{result.toxic_count}</b> toxic</span>
                <span><b className="text-success">{result.new_count}</b> new</span>
                <span><b className="text-fg-2">{result.lost_count}</b> lost</span>
              </div>
              <ul className="space-y-2">
                {result.backlinks.map((b: any, i: number) => (
                  <li key={i} className="p-3 rounded-md border border-border">
                    <div className="flex items-center justify-between gap-2">
                      <span className="text-sm break-all">{b.source_url}</span>
                      <div className="flex items-center gap-2 shrink-0">
                        {b.status === "lost" && (
                          <span className="text-xs px-2 py-0.5 rounded-pill bg-bg-muted text-fg-2">
                            lost
                          </span>
                        )}
                        <span
                          className={`text-xs font-bold px-2 py-0.5 rounded-pill ${
                            (b.toxic_score ?? 0) >= 60
                              ? "bg-danger-bg text-danger"
                              : (b.toxic_score ?? 0) >= 30
                              ? "bg-warning-bg text-warning"
                              : "bg-success-bg text-success"
                          }`}
                        >
                          toxicity {b.toxic_score ?? "—"}
                        </span>
                      </div>
                    </div>
                    {b.anchor_text && (
                      <p className="text-xs text-fg-2 mt-1">anchor: {b.anchor_text}</p>
                    )}
                    {b.toxic_reason && <p className="text-xs text-fg-2 mt-0.5">{b.toxic_reason}</p>}
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
