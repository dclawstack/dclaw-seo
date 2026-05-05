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
              <p className="text-3xl font-bold text-emerald-600 mb-4">Score: {result.score}</p>
              <ul className="space-y-2">
                {result.issues.map((issue: any, i: number) => (
                  <li
                    key={i}
                    className={`p-3 rounded-lg ${
                      issue.severity === "error"
                        ? "bg-red-50 text-red-700"
                        : issue.severity === "warning"
                        ? "bg-yellow-50 text-yellow-700"
                        : "bg-blue-50 text-blue-700"
                    }`}
                  >
                    <span className="font-semibold uppercase text-xs">{issue.severity}</span>:{" "}
                    {issue.message}
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
