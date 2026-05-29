"use client";

import { useState } from "react";
import { Navbar } from "@/components/navbar";
import { Card, CardTitle, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { writeArticle } from "@/lib/api";

export default function WriterPage() {
  const [keyword, setKeyword] = useState("");
  const [tone, setTone] = useState("professional");
  const [result, setResult] = useState<any>(null);
  const [loading, setLoading] = useState(false);

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setLoading(true);
    try {
      setResult(await writeArticle(keyword, { tone }));
    } catch {
      alert("Article generation failed");
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
        <h2 className="text-2xl font-bold mb-6">AI Content Writer</h2>
        <Card className="mb-6">
          <CardContent>
            <form onSubmit={handleSubmit} className="flex flex-wrap gap-4">
              <Input
                placeholder="Topic / target keyword"
                value={keyword}
                onChange={(e) => setKeyword(e.target.value)}
                className="flex-1 min-w-[240px]"
              />
              <select
                value={tone}
                onChange={(e) => setTone(e.target.value)}
                className="rounded-md border border-border bg-bg px-3 text-sm"
              >
                <option value="professional">Professional</option>
                <option value="casual">Casual</option>
                <option value="persuasive">Persuasive</option>
                <option value="technical">Technical</option>
              </select>
              <Button type="submit" disabled={loading}>
                {loading ? "Writing..." : "Generate Article"}
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
              <CardTitle>{result.title}</CardTitle>
              <CardContent>
                <div className="flex flex-wrap gap-4 text-sm text-fg-2 mb-4">
                  <span>
                    Words: <b className="text-fg-1">{result.word_count}</b>
                  </span>
                  <span>
                    Originality: <b className="text-fg-1">{result.originality_score}%</b>
                  </span>
                  <span>
                    {result.llm_generated ? "AI-generated" : "Scaffold (no LLM)"}
                  </span>
                </div>
                <article className="space-y-5">
                  {result.sections.map((s: any, i: number) => (
                    <section key={i}>
                      <h4 className="font-semibold text-fg-1 mb-1">{s.heading}</h4>
                      <p className="text-sm text-fg-1 whitespace-pre-line">{s.body}</p>
                    </section>
                  ))}
                </article>
              </CardContent>
            </Card>
            {result.fact_check_notes?.length > 0 && (
              <Card>
                <CardTitle>Fact-Check Notes</CardTitle>
                <CardContent>
                  <ul className="space-y-1 text-sm list-disc list-inside text-fg-1">
                    {result.fact_check_notes.map((n: string, i: number) => (
                      <li key={i}>{n}</li>
                    ))}
                  </ul>
                </CardContent>
              </Card>
            )}
          </div>
        )}
      </main>
    </div>
  );
}
