"use client";

import { useEffect, useState } from "react";
import { Navbar } from "@/components/navbar";
import { Card, CardTitle, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import {
  addCitation,
  addReview,
  createBusiness,
  listBusinesses,
  listReviews,
  napScan,
} from "@/lib/api";

export default function LocalPage() {
  const [businesses, setBusinesses] = useState<any[]>([]);
  const [selected, setSelected] = useState<number | null>(null);
  const [scan, setScan] = useState<any>(null);
  const [reviews, setReviews] = useState<any[]>([]);
  const [biz, setBiz] = useState({ name: "", address: "", phone: "" });
  const [cit, setCit] = useState({ source: "", listed_name: "", listed_address: "", listed_phone: "" });
  const [rev, setRev] = useState({ source: "google", author: "", rating: 5, text: "" });

  async function refresh() {
    setBusinesses(await listBusinesses());
  }
  useEffect(() => {
    refresh();
  }, []);

  async function refreshSelected(id: number) {
    setSelected(id);
    setScan(await napScan(id));
    setReviews(await listReviews(id));
  }

  async function handleCreateBiz(e: React.FormEvent) {
    e.preventDefault();
    await createBusiness(biz);
    setBiz({ name: "", address: "", phone: "" });
    refresh();
  }
  async function handleAddCitation(e: React.FormEvent) {
    e.preventDefault();
    if (!selected) return;
    await addCitation(selected, cit);
    setCit({ source: "", listed_name: "", listed_address: "", listed_phone: "" });
    refreshSelected(selected);
  }
  async function handleAddReview(e: React.FormEvent) {
    e.preventDefault();
    if (!selected) return;
    await addReview(selected, { ...rev, rating: Number(rev.rating) });
    setRev({ source: "google", author: "", rating: 5, text: "" });
    refreshSelected(selected);
  }

  return (
    <div className="flex min-h-screen">
      <aside className="hidden md:flex">
        <Navbar />
      </aside>
      <main className="flex-1 p-8 space-y-6">
        <h2 className="text-2xl font-bold">Local SEO Manager</h2>

        <Card>
          <CardTitle>Add a Business (canonical NAP)</CardTitle>
          <CardContent>
            <form onSubmit={handleCreateBiz} className="flex flex-wrap gap-3">
              <Input placeholder="Name" value={biz.name} onChange={(e) => setBiz({ ...biz, name: e.target.value })} className="min-w-[180px]" />
              <Input placeholder="Address" value={biz.address} onChange={(e) => setBiz({ ...biz, address: e.target.value })} className="flex-1 min-w-[220px]" />
              <Input placeholder="Phone" value={biz.phone} onChange={(e) => setBiz({ ...biz, phone: e.target.value })} className="min-w-[150px]" />
              <Button type="submit">Add</Button>
            </form>
          </CardContent>
        </Card>

        <Card>
          <CardTitle>Businesses</CardTitle>
          <CardContent>
            {businesses.length === 0 ? (
              <p className="text-sm text-fg-2">No businesses yet.</p>
            ) : (
              <ul className="space-y-2">
                {businesses.map((b) => (
                  <li key={b.id}>
                    <button
                      onClick={() => refreshSelected(b.id)}
                      className={`text-sm px-3 py-2 rounded-md w-full text-left ${
                        selected === b.id ? "bg-brand-soft text-brand-press" : "hover:bg-bg-muted"
                      }`}
                    >
                      <b>{b.name}</b> — {b.address} · {b.phone}
                    </button>
                  </li>
                ))}
              </ul>
            )}
          </CardContent>
        </Card>

        {selected && (
          <>
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              <Card>
                <CardTitle>Add Citation</CardTitle>
                <CardContent>
                  <form onSubmit={handleAddCitation} className="space-y-3">
                    <Input placeholder="Source (e.g. Yelp)" value={cit.source} onChange={(e) => setCit({ ...cit, source: e.target.value })} />
                    <Input placeholder="Listed name" value={cit.listed_name} onChange={(e) => setCit({ ...cit, listed_name: e.target.value })} />
                    <Input placeholder="Listed address" value={cit.listed_address} onChange={(e) => setCit({ ...cit, listed_address: e.target.value })} />
                    <Input placeholder="Listed phone" value={cit.listed_phone} onChange={(e) => setCit({ ...cit, listed_phone: e.target.value })} />
                    <Button type="submit">Add Citation</Button>
                  </form>
                </CardContent>
              </Card>

              <Card>
                <CardTitle>NAP Consistency</CardTitle>
                <CardContent>
                  {scan && (
                    <>
                      <p className="text-sm text-fg-2 mb-3">
                        Score: <b className="text-fg-1">{scan.consistency_score}%</b> ·{" "}
                        {scan.consistent}/{scan.total_citations} consistent
                      </p>
                      <ul className="space-y-1 text-sm">
                        {scan.citations.map((c: any) => (
                          <li key={c.id} className="flex items-center gap-2">
                            <span className={c.nap_consistent ? "text-success" : "text-danger"}>
                              {c.nap_consistent ? "✓" : "✗"}
                            </span>
                            <span>{c.source}</span>
                            {c.mismatch_fields.length > 0 && (
                              <span className="text-xs text-danger">
                                mismatch: {c.mismatch_fields.join(", ")}
                              </span>
                            )}
                          </li>
                        ))}
                      </ul>
                    </>
                  )}
                </CardContent>
              </Card>
            </div>

            <Card>
              <CardTitle>Reviews &amp; AI Responses</CardTitle>
              <CardContent>
                <form onSubmit={handleAddReview} className="flex flex-wrap gap-3 mb-4">
                  <Input placeholder="Author" value={rev.author} onChange={(e) => setRev({ ...rev, author: e.target.value })} className="min-w-[140px]" />
                  <select value={rev.rating} onChange={(e) => setRev({ ...rev, rating: Number(e.target.value) })} className="rounded-md border border-border bg-bg px-3 text-sm">
                    {[5, 4, 3, 2, 1].map((n) => (
                      <option key={n} value={n}>{n} ★</option>
                    ))}
                  </select>
                  <Input placeholder="Review text" value={rev.text} onChange={(e) => setRev({ ...rev, text: e.target.value })} className="flex-1 min-w-[200px]" />
                  <Button type="submit">Add &amp; Draft Reply</Button>
                </form>
                <ul className="space-y-3">
                  {reviews.map((r) => (
                    <li key={r.id} className="border-b border-border pb-2">
                      <p className="text-sm">
                        <b>{r.rating}★</b> {r.author && `· ${r.author}`} · {r.source}
                      </p>
                      {r.text && <p className="text-sm text-fg-1">{r.text}</p>}
                      {r.suggested_response && (
                        <p className="text-sm text-brand-press mt-1">
                          ↳ Suggested reply: {r.suggested_response}
                        </p>
                      )}
                    </li>
                  ))}
                </ul>
              </CardContent>
            </Card>
          </>
        )}
      </main>
    </div>
  );
}
