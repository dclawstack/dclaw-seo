"use client";

import { useState } from "react";
import { Navbar } from "@/components/navbar";
import { Card, CardTitle, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { generateBrief } from "@/lib/api";

export default function BriefPage() {
  const [keyword, setKeyword] = useState("");
  const [result, setResult] = useState<any>(null);
  const [loading, setLoading] = useState(false);

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setLoading(true);
    try {
      setResult(await generateBrief(keyword));
    } catch {
      alert("Brief generation failed");
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
        <h2 className="text-2xl font-bold mb-6">AI Content Brief</h2>
        <Card className="mb-6">
          <CardContent>
            <form onSubmit={handleSubmit} className="flex gap-4">
              <Input
                placeholder="Target keyword"
                value={keyword}
                onChange={(e) => setKeyword(e.target.value)}
                className="flex-1"
              />
              <Button type="submit" disabled={loading}>
                {loading ? "Generating..." : "Generate Brief"}
              </Button>
            </form>
          </CardContent>
        </Card>

        {result && (
          <div className="space-y-6">
            {result.note && (
              <div className="p-3 bg-info-bg text-info rounded-md text-sm">{result.note}</div>
            )}
            <Card>
              <CardTitle>Brief for &quot;{result.keyword}&quot;</CardTitle>
              <CardContent>
                <p className="text-sm text-fg-2 mb-3">
                  Recommended length: <b className="text-fg-1">{result.recommended_words}</b> words
                </p>
                <div className="flex flex-wrap gap-2 mb-4">
                  {result.title_suggestions.map((t: string, i: number) => (
                    <span key={i} className="px-2 py-1 rounded-md bg-bg-muted text-sm">
                      {t}
                    </span>
                  ))}
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardTitle>Outline</CardTitle>
              <CardContent>
                <ol className="space-y-3 list-decimal list-inside">
                  {result.outline.map((s: any, i: number) => (
                    <li key={i} className="font-medium">
                      {s.h2}
                      {s.h3?.length > 0 && (
                        <ul className="mt-1 ml-5 list-disc list-inside font-normal text-sm text-fg-2">
                          {s.h3.map((h: string, j: number) => (
                            <li key={j}>{h}</li>
                          ))}
                        </ul>
                      )}
                    </li>
                  ))}
                </ol>
              </CardContent>
            </Card>

            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              <Card>
                <CardTitle>Questions to Answer</CardTitle>
                <CardContent>
                  <ul className="space-y-1 text-sm list-disc list-inside text-fg-1">
                    {result.questions.length ? (
                      result.questions.map((q: string, i: number) => <li key={i}>{q}</li>)
                    ) : (
                      <li className="text-fg-2 list-none">No question queries found.</li>
                    )}
                  </ul>
                </CardContent>
              </Card>
              <Card>
                <CardTitle>Secondary Keywords</CardTitle>
                <CardContent>
                  <div className="flex flex-wrap gap-2">
                    {result.secondary_keywords.map((k: string, i: number) => (
                      <span
                        key={i}
                        className="px-2 py-1 rounded-pill bg-brand-soft text-brand-press text-xs"
                      >
                        {k}
                      </span>
                    ))}
                  </div>
                </CardContent>
              </Card>
            </div>
          </div>
        )}
      </main>
    </div>
  );
}
