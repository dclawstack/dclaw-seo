"use client";

import { useEffect, useState } from "react";
import { Navbar } from "@/components/navbar";
import { Card, CardTitle, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import {
  createSchedule,
  downloadReport,
  listSchedules,
  reportPreview,
} from "@/lib/api";

export default function ReportsPage() {
  const [brand, setBrand] = useState({ title: "SEO Performance Report", brand_company: "", brand_color: "#6E56CF" });
  const [preview, setPreview] = useState<any>(null);
  const [schedules, setSchedules] = useState<any[]>([]);
  const [sched, setSched] = useState({ site_url: "", frequency: "weekly", recipient: "" });
  const [loading, setLoading] = useState(false);

  async function refresh() {
    setSchedules(await listSchedules());
  }
  useEffect(() => {
    refresh();
  }, []);

  async function handlePreview() {
    setLoading(true);
    try {
      setPreview(await reportPreview(brand));
    } finally {
      setLoading(false);
    }
  }
  async function handleSchedule(e: React.FormEvent) {
    e.preventDefault();
    await createSchedule({ ...sched, brand_company: brand.brand_company, brand_color: brand.brand_color });
    setSched({ site_url: "", frequency: "weekly", recipient: "" });
    refresh();
  }

  return (
    <div className="flex min-h-screen">
      <aside className="hidden md:flex">
        <Navbar />
      </aside>
      <main className="flex-1 p-8 space-y-6">
        <h2 className="text-2xl font-bold">White-Label Reports</h2>

        <Card>
          <CardTitle>Branding</CardTitle>
          <CardContent>
            <div className="flex flex-wrap gap-3 items-center">
              <Input placeholder="Report title" value={brand.title} onChange={(e) => setBrand({ ...brand, title: e.target.value })} className="min-w-[200px]" />
              <Input placeholder="Company name" value={brand.brand_company} onChange={(e) => setBrand({ ...brand, brand_company: e.target.value })} className="min-w-[180px]" />
              <input type="color" value={brand.brand_color} onChange={(e) => setBrand({ ...brand, brand_color: e.target.value })} className="h-9 w-12 rounded border border-border" />
              <Button onClick={handlePreview} disabled={loading}>{loading ? "..." : "Preview"}</Button>
              <Button onClick={() => downloadReport("pdf", brand)}>Download PDF</Button>
              <Button onClick={() => downloadReport("csv", brand)}>Download CSV</Button>
            </div>
          </CardContent>
        </Card>

        {preview && (
          <Card>
            <CardTitle>{preview.title}</CardTitle>
            <CardContent>
              {preview.note && <div className="p-3 bg-info-bg text-info rounded-md text-sm mb-3">{preview.note}</div>}
              <table className="text-sm w-full max-w-md mb-4">
                <tbody>
                  {preview.metrics.map((m: any, i: number) => (
                    <tr key={i} className="border-b border-border">
                      <td className="py-1 text-fg-2">{m.label}</td>
                      <td className="py-1 text-right font-medium">{m.value}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
              <p className="text-sm text-fg-1">
                <b>Executive summary {preview.summary_ai ? "(AI)" : "(templated)"}:</b> {preview.executive_summary}
              </p>
            </CardContent>
          </Card>
        )}

        <Card>
          <CardTitle>Scheduled Delivery</CardTitle>
          <CardContent>
            <form onSubmit={handleSchedule} className="flex flex-wrap gap-3 mb-4">
              <Input placeholder="Site URL" value={sched.site_url} onChange={(e) => setSched({ ...sched, site_url: e.target.value })} className="flex-1 min-w-[200px]" />
              <select value={sched.frequency} onChange={(e) => setSched({ ...sched, frequency: e.target.value })} className="rounded-md border border-border bg-bg px-3 text-sm">
                <option value="daily">Daily</option>
                <option value="weekly">Weekly</option>
                <option value="monthly">Monthly</option>
              </select>
              <Input placeholder="Recipient email" value={sched.recipient} onChange={(e) => setSched({ ...sched, recipient: e.target.value })} className="min-w-[200px]" />
              <Button type="submit">Schedule</Button>
            </form>
            <ul className="space-y-1 text-sm">
              {schedules.map((s) => (
                <li key={s.id} className="flex gap-2">
                  <span className="text-fg-1">{s.site_url}</span>
                  <span className="text-fg-2">· {s.frequency} → {s.recipient}</span>
                </li>
              ))}
            </ul>
            <p className="text-xs text-fg-2 mt-2">
              Email delivery activates when SMTP is configured in backend env; reports are generated either way.
            </p>
          </CardContent>
        </Card>
      </main>
    </div>
  );
}
