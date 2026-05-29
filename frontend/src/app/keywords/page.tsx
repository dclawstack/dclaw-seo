"use client";

import { useState } from "react";
import { Navbar } from "@/components/navbar";
import { Card, CardTitle, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { researchKeywords } from "@/lib/api";

export default function KeywordsPage() {
  const [seed, setSeed] = useState("");
  const [result, setResult] = useState<any>(null);
  const [loading, setLoading] = useState(false);

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setLoading(true);
    try {
      const data = await researchKeywords(seed);
      setResult(data);
    } catch (err) {
      alert("Keyword research failed");
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
        <h2 className="text-2xl font-bold mb-6">Keyword Research</h2>
        <Card className="mb-6">
          <CardContent>
            <form onSubmit={handleSubmit} className="flex gap-4">
              <Input
                placeholder="Enter a seed keyword"
                value={seed}
                onChange={(e) => setSeed(e.target.value)}
                className="flex-1"
              />
              <Button type="submit" disabled={loading}>
                {loading ? "Researching..." : "Research"}
              </Button>
            </form>
          </CardContent>
        </Card>
        {result && (
          <div className="space-y-4">
            <h3 className="text-lg font-semibold">Suggestions for &quot;{result.seed}&quot;</h3>
            {result.suggestions.map((kw: any, i: number) => (
              <Card key={i}>
                <CardContent className="flex items-center justify-between">
                  <span className="font-medium">{kw.term}</span>
                  <div className="flex gap-4 text-sm text-fg-2">
                    <span>Volume: {kw.search_volume.toLocaleString()}</span>
                    <span>Difficulty: {kw.difficulty}</span>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        )}
      </main>
    </div>
  );
}
