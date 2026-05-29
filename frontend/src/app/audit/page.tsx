"use client";

import { useState } from "react";
import { Navbar } from "@/components/navbar";
import { Card, CardTitle, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { auditSite } from "@/lib/api";

export default function AuditPage() {
  const [url, setUrl] = useState("");
  const [result, setResult] = useState<any>(null);
  const [loading, setLoading] = useState(false);

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setLoading(true);
    try {
      const data = await auditSite(url);
      setResult(data);
    } catch (err) {
      alert("Audit failed");
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
        <h2 className="text-2xl font-bold mb-6">Site Audit</h2>
        <Card className="mb-6">
          <CardContent>
            <form onSubmit={handleSubmit} className="flex gap-4">
              <Input
                placeholder="https://example.com"
                value={url}
                onChange={(e) => setUrl(e.target.value)}
                className="flex-1"
              />
              <Button type="submit" disabled={loading}>
                {loading ? "Auditing..." : "Run Audit"}
              </Button>
            </form>
          </CardContent>
        </Card>
        {result && (
          <Card>
            <CardTitle>Results for {result.url}</CardTitle>
            <CardContent>
              <div className="flex items-baseline gap-4 mb-3">
                <p className="text-3xl font-bold text-brand">Score: {result.score}</p>
                <span className="text-sm text-fg-2">{result.pages_crawled} page(s) crawled</span>
              </div>
              {result.summary && (
                <p className="mb-4 p-3 bg-bg-muted rounded-md text-sm text-fg-1">{result.summary}</p>
              )}
              <ul className="space-y-2">
                {result.issues.map((issue: any, i: number) => (
                  <li
                    key={i}
                    className={`p-3 rounded-md ${
                      issue.severity === "error"
                        ? "bg-danger-bg text-danger"
                        : issue.severity === "warning"
                        ? "bg-warning-bg text-warning"
                        : "bg-info-bg text-info"
                    }`}
                  >
                    <span className="font-semibold uppercase text-xs">{issue.severity}</span>:{" "}
                    {issue.message}
                    {issue.url && (
                      <span className="block text-xs opacity-70 mt-0.5 break-all">{issue.url}</span>
                    )}
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
