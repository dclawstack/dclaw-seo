"use client";

import { Navbar } from "@/components/navbar";
import { Card, CardTitle, CardContent } from "@/components/ui/card";

export default function SettingsPage() {
  return (
    <div className="flex min-h-screen">
      <aside className="hidden md:flex">
        <Navbar />
      </aside>
      <main className="flex-1 p-8">
        <h2 className="text-2xl font-bold mb-6">Settings</h2>
        <div className="space-y-6 max-w-2xl">
          <Card>
            <CardTitle>API Configuration</CardTitle>
            <CardContent>
              <p className="text-sm text-fg-1 mb-2">Backend API Base URL</p>
              <div className="p-3 bg-bg-muted rounded-md text-sm font-mono">
                {process.env.NEXT_PUBLIC_API_URL || "http://localhost:8095"}
              </div>
            </CardContent>
          </Card>
          <Card>
            <CardTitle>About</CardTitle>
            <CardContent>
              <p className="text-sm text-fg-1">
                DClaw SEO v0.1.0 — Rank higher with AI. Part of the DClaw Stack.
              </p>
            </CardContent>
          </Card>
        </div>
      </main>
    </div>
  );
}
