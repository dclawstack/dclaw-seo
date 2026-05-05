"use client";

import { Navbar } from "@/components/navbar";
import { Card, CardTitle, CardContent } from "@/components/ui/card";

export default function DashboardPage() {
  return (
    <div className="flex min-h-screen">
      <aside className="hidden md:flex">
        <Navbar />
      </aside>
      <main className="flex-1 p-8">
        <h2 className="text-2xl font-bold mb-6">Dashboard</h2>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <Card>
            <CardTitle>SEO Score</CardTitle>
            <CardContent>
              <p className="text-4xl font-bold text-emerald-600">87</p>
              <p className="text-sm text-gray-500">Last audit: 2 hours ago</p>
            </CardContent>
          </Card>
          <Card>
            <CardTitle>Tracked Keywords</CardTitle>
            <CardContent>
              <p className="text-4xl font-bold text-emerald-600">24</p>
              <p className="text-sm text-gray-500">+3 this week</p>
            </CardContent>
          </Card>
          <Card>
            <CardTitle>Recent Audits</CardTitle>
            <CardContent>
              <p className="text-4xl font-bold text-emerald-600">5</p>
              <p className="text-sm text-gray-500">All passed</p>
            </CardContent>
          </Card>
        </div>
      </main>
    </div>
  );
}
