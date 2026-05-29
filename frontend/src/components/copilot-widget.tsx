"use client";

import { useState } from "react";
import { Bot, X, ArrowRight, Loader2 } from "lucide-react";
import { copilotAnalyze } from "@/lib/api";
import { cn } from "@/lib/utils";

export function CopilotWidget() {
  const [open, setOpen] = useState(false);
  const [url, setUrl] = useState("");
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<any>(null);
  const [error, setError] = useState<string | null>(null);

  async function analyze(e: React.FormEvent) {
    e.preventDefault();
    setLoading(true);
    setError(null);
    setResult(null);
    try {
      setResult(await copilotAnalyze(url));
    } catch {
      setError("Could not analyze that URL. Check the address and try again.");
    } finally {
      setLoading(false);
    }
  }

  return (
    <>
      <button
        aria-label="Open SEO Copilot"
        onClick={() => setOpen((v) => !v)}
        className="fixed bottom-6 right-6 z-50 w-14 h-14 rounded-full bg-brand text-fg-on-brand shadow-brand flex items-center justify-center hover:bg-brand-hover transition-colors duration-base ease-out-quart"
      >
        {open ? <X className="w-6 h-6" /> : <Bot className="w-6 h-6" />}
      </button>

      {open && (
        <div className="fixed bottom-24 right-6 z-50 w-[min(92vw,380px)] max-h-[70vh] overflow-y-auto rounded-xl border border-border bg-bg shadow-lg">
          <div className="p-4 border-b border-border bg-brand-soft rounded-t-xl">
            <div className="flex items-center gap-2 text-brand-press font-semibold">
              <Bot className="w-5 h-5" /> SEO Copilot
            </div>
            <p className="text-xs text-fg-2 mt-1">
              Analyze any page and get prioritized next actions.
            </p>
          </div>
          <form onSubmit={analyze} className="p-4 flex gap-2">
            <input
              type="url"
              required
              placeholder="https://example.com/page"
              value={url}
              onChange={(e) => setUrl(e.target.value)}
              className="flex-1 px-3 py-2 rounded-md border border-border-strong bg-bg text-sm focus:outline-none focus:ring-2 focus:ring-brand"
            />
            <button
              type="submit"
              disabled={loading}
              className="inline-flex items-center justify-center px-3 rounded-md bg-brand text-fg-on-brand hover:bg-brand-hover transition-colors disabled:opacity-60"
            >
              {loading ? <Loader2 className="w-4 h-4 animate-spin" /> : <ArrowRight className="w-4 h-4" />}
            </button>
          </form>

          <div className="px-4 pb-4 space-y-3">
            {error && <p className="text-sm text-danger">{error}</p>}
            {result && (
              <>
                <p className="text-xs text-fg-2">{result.summary}</p>
                {result.note && (
                  <p className="text-xs bg-info-bg text-info rounded-md p-2">{result.note}</p>
                )}
                <ul className="space-y-2">
                  {result.actions.map((a: any, i: number) => (
                    <li key={i} className="rounded-md border border-border p-3">
                      <div className="flex items-center gap-2">
                        <span
                          className={cn(
                            "text-[10px] font-bold px-1.5 py-0.5 rounded-pill",
                            a.priority <= 1
                              ? "bg-danger-bg text-danger"
                              : a.priority === 2
                              ? "bg-warning-bg text-warning"
                              : "bg-brand-soft text-brand-press"
                          )}
                        >
                          P{a.priority}
                        </span>
                        <span className="text-sm font-semibold text-fg">{a.title}</span>
                      </div>
                      <p className="text-xs text-fg-2 mt-1">{a.detail}</p>
                    </li>
                  ))}
                </ul>
              </>
            )}
          </div>
        </div>
      )}
    </>
  );
}
