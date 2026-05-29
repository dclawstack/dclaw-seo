"use client";

import { useEffect, useState } from "react";
import { Navbar } from "@/components/navbar";
import { Card, CardTitle, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import {
  createProject,
  getMe,
  getUsage,
  listProjects,
  logout,
  setCostCap,
} from "@/lib/api";

export default function AccountPage() {
  const [me, setMe] = useState<any>(null);
  const [usage, setUsage] = useState<any>(null);
  const [projects, setProjects] = useState<any[]>([]);
  const [cap, setCap] = useState("");
  const [proj, setProj] = useState({ name: "", domain: "" });

  async function refresh() {
    try {
      setMe(await getMe());
      setUsage(await getUsage());
      setProjects(await listProjects());
    } catch {
      /* apiFetch redirects to /login on 401 */
    }
  }
  useEffect(() => {
    refresh();
  }, []);

  async function saveCap(e: React.FormEvent) {
    e.preventDefault();
    await setCostCap(cap === "" ? null : Number(cap));
    refresh();
  }
  async function addProject(e: React.FormEvent) {
    e.preventDefault();
    await createProject(proj.name, proj.domain || undefined);
    setProj({ name: "", domain: "" });
    refresh();
  }

  return (
    <div className="flex min-h-screen">
      <aside className="hidden md:flex">
        <Navbar />
      </aside>
      <main className="flex-1 p-8 space-y-6">
        <div className="flex items-center justify-between">
          <h2 className="text-2xl font-bold">Account &amp; Organization</h2>
          <Button onClick={logout} className="bg-bg-muted text-fg-1 hover:bg-border">Sign out</Button>
        </div>

        {me && (
          <Card>
            <CardTitle>Organization</CardTitle>
            <CardContent className="text-sm space-y-1">
              <p><b>{me.org.name}</b></p>
              <p className="text-fg-2">Signed in as {me.user.email} ({me.user.role})</p>
            </CardContent>
          </Card>
        )}

        {usage && (
          <Card>
            <CardTitle>LLM Usage &amp; Cost Cap</CardTitle>
            <CardContent>
              <div className="flex flex-wrap gap-6 text-sm mb-4">
                <span>Month-to-date: <b>${usage.month_to_date_cost_usd.toFixed(4)}</b></span>
                <span>Cap: <b>{usage.monthly_cost_cap_usd == null ? "none" : `$${usage.monthly_cost_cap_usd}`}</b></span>
                {usage.over_cap && <span className="text-danger font-medium">OVER CAP</span>}
              </div>
              <form onSubmit={saveCap} className="flex gap-3 items-center mb-4">
                <Input placeholder="Monthly cap (USD, blank = none)" value={cap} onChange={(e) => setCap(e.target.value)} className="max-w-[240px]" />
                <Button type="submit">Save cap</Button>
              </form>
              <p className="text-fg-2 text-sm mb-1">Recent metered calls</p>
              <ul className="text-sm space-y-1">
                {usage.recent.length === 0 && <li className="text-fg-2">No usage yet.</li>}
                {usage.recent.map((e: any) => (
                  <li key={e.id} className="flex gap-3">
                    <span className="text-fg-1">{e.feature}</span>
                    <span className="text-fg-2">{e.model}</span>
                    <span className="text-fg-2">{e.prompt_tokens + e.completion_tokens} tok</span>
                    <span className="text-fg-2">${e.cost_usd.toFixed(4)}</span>
                  </li>
                ))}
              </ul>
            </CardContent>
          </Card>
        )}

        <Card>
          <CardTitle>Projects</CardTitle>
          <CardContent>
            <form onSubmit={addProject} className="flex flex-wrap gap-3 mb-4">
              <Input placeholder="Project name" value={proj.name} onChange={(e) => setProj({ ...proj, name: e.target.value })} className="min-w-[180px]" />
              <Input placeholder="Domain (optional)" value={proj.domain} onChange={(e) => setProj({ ...proj, domain: e.target.value })} className="min-w-[180px]" />
              <Button type="submit">Add project</Button>
            </form>
            <ul className="text-sm space-y-1">
              {projects.map((p) => (
                <li key={p.id}><b>{p.name}</b>{p.domain && <span className="text-fg-2"> — {p.domain}</span>}</li>
              ))}
            </ul>
          </CardContent>
        </Card>
      </main>
    </div>
  );
}
