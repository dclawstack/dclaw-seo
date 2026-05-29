"use client";

import { useState } from "react";
import { Navbar } from "@/components/navbar";
import { Card, CardTitle, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { generateMetaTags } from "@/lib/api";

export default function MetaPage() {
  const [url, setUrl] = useState("");
  const [keyword, setKeyword] = useState("");
  const [result, setResult] = useState<any>(null);
  const [loading, setLoading] = useState(false);

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setLoading(true);
    try {
      setResult(await generateMetaTags({ url, keyword: keyword || undefined }));
    } catch {
      alert("Meta generation failed (could not fetch the URL?)");
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
        <h2 className="text-2xl font-bold mb-6">AI Meta Tags &amp; Schema</h2>
        <Card className="mb-6">
          <CardContent>
            <form onSubmit={handleSubmit} className="flex flex-wrap gap-4">
              <Input
                placeholder="Page URL (https://...)"
                value={url}
                onChange={(e) => setUrl(e.target.value)}
                className="flex-1 min-w-[260px]"
              />
              <Input
                placeholder="Target keyword (optional)"
                value={keyword}
                onChange={(e) => setKeyword(e.target.value)}
                className="flex-1 min-w-[200px]"
              />
              <Button type="submit" disabled={loading}>
                {loading ? "Generating..." : "Generate"}
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
              <CardTitle>Title &amp; Meta</CardTitle>
              <CardContent className="space-y-3 text-sm">
                <div>
                  <p className="text-fg-2">Title ({result.title_length} chars)</p>
                  <p className="font-medium text-fg-1">{result.title_tag}</p>
                </div>
                <div>
                  <p className="text-fg-2">Meta description ({result.meta_length} chars)</p>
                  <p className="text-fg-1">{result.meta_description}</p>
                </div>
                {result.title_variants?.length > 1 && (
                  <div>
                    <p className="text-fg-2">Title variants</p>
                    <ul className="list-disc list-inside text-fg-1">
                      {result.title_variants.map((t: string, i: number) => (
                        <li key={i}>{t}</li>
                      ))}
                    </ul>
                  </div>
                )}
              </CardContent>
            </Card>
            <Card>
              <CardTitle>JSON-LD Schema</CardTitle>
              <CardContent>
                <pre className="text-xs bg-bg-muted rounded-md p-3 overflow-x-auto">
                  {JSON.stringify(result.json_ld, null, 2)}
                </pre>
              </CardContent>
            </Card>
            <Card>
              <CardTitle>Open Graph &amp; Twitter</CardTitle>
              <CardContent>
                <pre className="text-xs bg-bg-muted rounded-md p-3 overflow-x-auto">
                  {JSON.stringify({ ...result.og_tags, ...result.twitter_tags }, null, 2)}
                </pre>
              </CardContent>
            </Card>
          </div>
        )}
      </main>
    </div>
  );
}
