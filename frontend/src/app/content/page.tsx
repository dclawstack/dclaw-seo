"use client";

import { useState } from "react";
import { Navbar } from "@/components/navbar";
import { Card, CardTitle, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input, TextArea } from "@/components/ui/input";
import { optimizeContent } from "@/lib/api";

export default function ContentPage() {
  const [keyword, setKeyword] = useState("");
  const [content, setContent] = useState("");
  const [result, setResult] = useState<any>(null);
  const [loading, setLoading] = useState(false);

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setLoading(true);
    try {
      const data = await optimizeContent(keyword, content);
      setResult(data);
    } catch (err) {
      alert("Optimization failed");
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
        <h2 className="text-2xl font-bold mb-6">Content Optimizer</h2>
        <Card className="mb-6">
          <CardContent>
            <form onSubmit={handleSubmit} className="space-y-4">
              <Input
                placeholder="Target keyword"
                value={keyword}
                onChange={(e) => setKeyword(e.target.value)}
              />
              <TextArea
                placeholder="Paste your content here..."
                rows={6}
                value={content}
                onChange={(e) => setContent(e.target.value)}
              />
              <Button type="submit" disabled={loading}>
                {loading ? "Optimizing..." : "Optimize"}
              </Button>
            </form>
          </CardContent>
        </Card>
        {result && (
          <div className="space-y-6">
            <Card>
              <CardTitle>Optimized Content</CardTitle>
              <CardContent>
                <div className="whitespace-pre-wrap bg-bg-muted p-4 rounded-md text-sm">
                  {result.optimized_content}
                </div>
              </CardContent>
            </Card>
            <Card>
              <CardTitle>Suggestions</CardTitle>
              <CardContent>
                <ul className="space-y-2">
                  {result.suggestions.map((s: any, i: number) => (
                    <li key={i} className="p-3 bg-brand-soft text-brand-press rounded-md text-sm">
                      <span className="font-semibold capitalize">{s.type}</span>: {s.message}
                    </li>
                  ))}
                </ul>
              </CardContent>
            </Card>
          </div>
        )}
      </main>
    </div>
  );
}
