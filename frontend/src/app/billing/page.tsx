"use client";

import { useEffect, useState } from "react";
import { Navbar } from "@/components/navbar";
import { Card, CardTitle, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import {
  getBillingAccount,
  getInvoicePreview,
  getPlans,
  subscribe,
} from "@/lib/api";

export default function BillingPage() {
  const [plans, setPlans] = useState<any[]>([]);
  const [account, setAccount] = useState<any>(null);
  const [invoice, setInvoice] = useState<any>(null);
  const [seats, setSeats] = useState(1);

  async function refresh() {
    try {
      setPlans(await getPlans());
      const acct = await getBillingAccount();
      setAccount(acct);
      setSeats(acct.seats);
      setInvoice(await getInvoicePreview());
    } catch {
      /* 401 -> redirect handled in apiFetch */
    }
  }
  useEffect(() => {
    refresh();
  }, []);

  async function choose(plan: string) {
    await subscribe(plan, seats);
    refresh();
  }

  return (
    <div className="flex min-h-screen">
      <aside className="hidden md:flex">
        <Navbar />
      </aside>
      <main className="flex-1 p-8 space-y-6">
        <h2 className="text-2xl font-bold">Billing</h2>

        {account && (
          <p className="text-sm text-fg-2">
            Current plan: <b className="text-fg-1">{account.plan}</b> · {account.seats} seat(s) ·
            Stripe {account.stripe_enabled ? "connected" : "not configured (local invoicing)"}
          </p>
        )}

        <div className="flex items-center gap-3">
          <span className="text-sm text-fg-2">Seats:</span>
          <Input type="number" min={1} value={seats} onChange={(e) => setSeats(Number(e.target.value))} className="max-w-[100px]" />
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          {plans.map((p) => (
            <Card key={p.key} className={account?.plan === p.key ? "border-brand" : ""}>
              <CardTitle>{p.name}</CardTitle>
              <CardContent>
                <p className="text-2xl font-bold mb-1">${p.monthly_price_usd}<span className="text-sm font-normal text-fg-2">/mo</span></p>
                <ul className="text-sm text-fg-2 space-y-1 mb-4">
                  <li>{p.included_seats} seats included</li>
                  <li>${p.price_per_extra_seat_usd}/extra seat</li>
                  <li>${p.included_usage_usd} LLM usage included</li>
                </ul>
                <Button onClick={() => choose(p.key)} disabled={account?.plan === p.key} className="w-full">
                  {account?.plan === p.key ? "Current" : "Choose"}
                </Button>
              </CardContent>
            </Card>
          ))}
        </div>

        {invoice && (
          <Card>
            <CardTitle>Invoice preview — {invoice.period}</CardTitle>
            <CardContent>
              {invoice.note && <div className="p-3 bg-info-bg text-info rounded-md text-sm mb-3">{invoice.note}</div>}
              <table className="text-sm w-full max-w-md">
                <tbody>
                  {invoice.lines.length === 0 && (
                    <tr><td className="py-1 text-fg-2">No charges this period</td></tr>
                  )}
                  {invoice.lines.map((l: any, i: number) => (
                    <tr key={i} className="border-b border-border">
                      <td className="py-1 text-fg-2">{l.description}</td>
                      <td className="py-1 text-right">${l.amount_usd.toFixed(2)}</td>
                    </tr>
                  ))}
                  <tr className="font-bold">
                    <td className="py-2">Total</td>
                    <td className="py-2 text-right">${invoice.total_usd.toFixed(2)}</td>
                  </tr>
                </tbody>
              </table>
              <p className="text-xs text-fg-2 mt-2">Metered LLM usage this month: ${invoice.usage_cost_usd.toFixed(4)}</p>
            </CardContent>
          </Card>
        )}
      </main>
    </div>
  );
}
