"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { Navbar } from "@/components/navbar";
import { Card, CardTitle, CardContent } from "@/components/ui/card";
import { getStats } from "@/lib/api";

const QUICK_ACTIONS = [
  { href: "/audit", label: "Run a site audit" },
  { href: "/keywords", label: "Research keywords" },
  { href: "/content", label: "Optimize content" },
  { href: "/rankings", label: "Track rankings" },
];

export default function DashboardPage() {
  const [stats, setStats] = useState<any>(null);
  const [error, setError] = useState(false);

  useEffect(() => {
    getStats().then(setStats).catch(() => setError(true));
  }, []);

  const cards = [
    { label: "Latest SEO Score", value: stats?.latest_audit_score ?? "—", sub: "from most recent audit" },
    { label: "Keywords Researched", value: stats?.keywords ?? "—", sub: "total searches" },
    { label: "Audits Run", value: stats?.audits ?? "—", sub: "total" },
    { label: "Rank Observations", value: stats?.rank_observations ?? "—", sub: "recorded" },
  ];

  return (
    <div className="flex min-h-screen">
      <aside className="hidden md:flex">
        <Navbar />
      </aside>
      <main className="flex-1 p-8">
        <h2 className="text-2xl font-bold mb-6">Dashboard</h2>

        {error && (
          <div className="mb-6 p-3 bg-warning-bg text-warning rounded-md text-sm">
            Could not reach the API. Is the backend running on port 8095?
          </div>
        )}

        <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
          {cards.map((c) => (
            <Card key={c.label}>
              <CardTitle>{c.label}</CardTitle>
              <CardContent>
                <p className="text-4xl font-bold text-brand">{c.value}</p>
                <p className="text-sm text-fg-2">{c.sub}</p>
              </CardContent>
            </Card>
          ))}
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mt-6">
          <Card>
            <CardTitle>Recent Activity</CardTitle>
            <CardContent>
              {stats?.recent?.length ? (
                <ul className="space-y-2">
                  {stats.recent.map((a: any, i: number) => (
                    <li key={i} className="flex items-center justify-between text-sm">
                      <span>
                        <span className="inline-block w-20 text-xs uppercase tracking-wide text-brand-press font-semibold">
                          {a.type}
                        </span>
                        <span className="text-fg-1">{a.label}</span>
                      </span>
                      <span className="text-xs text-fg-2">{String(a.at).slice(0, 10)}</span>
                    </li>
                  ))}
                </ul>
              ) : (
                <p className="text-sm text-fg-2">No activity yet — run a tool to get started.</p>
              )}
            </CardContent>
          </Card>

          <Card>
            <CardTitle>Quick Actions</CardTitle>
            <CardContent>
              <div className="grid grid-cols-2 gap-3">
                {QUICK_ACTIONS.map((q) => (
                  <Link
                    key={q.href}
                    href={q.href}
                    className="block text-center px-4 py-3 rounded-md bg-brand-soft text-brand-press font-medium text-sm hover:bg-brand-200 transition-colors"
                  >
                    {q.label}
                  </Link>
                ))}
              </div>
            </CardContent>
          </Card>
        </div>
      </main>
    </div>
  );
}
