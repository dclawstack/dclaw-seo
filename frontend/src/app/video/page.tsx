"use client";

import { useState } from "react";
import { Navbar } from "@/components/navbar";
import { Card, CardTitle, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { optimizeVideo } from "@/lib/api";

export default function VideoPage() {
  const [topic, setTopic] = useState("");
  const [result, setResult] = useState<any>(null);
  const [loading, setLoading] = useState(false);

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setLoading(true);
    try {
      setResult(await optimizeVideo(topic));
    } catch {
      alert("Video optimization failed");
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
        <h2 className="text-2xl font-bold mb-6">Video SEO</h2>
        <Card className="mb-6">
          <CardContent>
            <form onSubmit={handleSubmit} className="flex gap-4">
              <Input
                placeholder="Video topic / working title"
                value={topic}
                onChange={(e) => setTopic(e.target.value)}
                className="flex-1"
              />
              <Button type="submit" disabled={loading}>
                {loading ? "Optimizing..." : "Optimize"}
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
              <CardTitle>Title Variants</CardTitle>
              <CardContent>
                <ul className="space-y-2">
                  {result.title_variants.map((v: any, i: number) => (
                    <li key={i} className="flex items-center gap-2">
                      <span className="px-2 py-0.5 rounded-pill bg-brand-soft text-brand-press text-xs">
                        {v.angle}
                      </span>
                      <span className="text-sm text-fg-1">{v.title}</span>
                    </li>
                  ))}
                </ul>
              </CardContent>
            </Card>
            <Card>
              <CardTitle>Description</CardTitle>
              <CardContent>
                <p className="text-sm text-fg-1 whitespace-pre-line">{result.description}</p>
              </CardContent>
            </Card>
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              <Card>
                <CardTitle>Tags</CardTitle>
                <CardContent>
                  <div className="flex flex-wrap gap-2">
                    {result.tags.map((t: string, i: number) => (
                      <span key={i} className="px-2 py-1 rounded-md bg-bg-muted text-xs">
                        {t}
                      </span>
                    ))}
                  </div>
                </CardContent>
              </Card>
              <Card>
                <CardTitle>Hashtags</CardTitle>
                <CardContent>
                  <div className="flex flex-wrap gap-2">
                    {result.hashtags.map((h: string, i: number) => (
                      <span
                        key={i}
                        className="px-2 py-1 rounded-pill bg-brand-soft text-brand-press text-xs"
                      >
                        {h}
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
