"use client";

import { useEffect, useState } from "react";
import { Navbar } from "@/components/navbar";
import { Card, CardTitle, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { getLLMSettings, updateLLMSettings, testLLM } from "@/lib/api";

export default function SettingsPage() {
  const [view, setView] = useState<any>(null);
  const [form, setForm] = useState({
    provider: "auto",
    ollama_url: "",
    ollama_model: "",
    openrouter_model: "",
    openrouter_api_key: "",
  });
  const [saving, setSaving] = useState(false);
  const [msg, setMsg] = useState<{ ok: boolean; text: string } | null>(null);

  async function load() {
    const v = await getLLMSettings();
    setView(v);
    setForm((f) => ({
      ...f,
      provider: v.provider ?? "auto",
      ollama_url: v.ollama_url ?? "",
      ollama_model: v.ollama_model ?? "",
      openrouter_model: v.openrouter_model ?? "",
      openrouter_api_key: "", // never prefilled; blank = keep existing
    }));
  }

  useEffect(() => {
    load().catch(() => setMsg({ ok: false, text: "Could not reach the API." }));
  }, []);

  function set(k: string, v: string) {
    setForm((f) => ({ ...f, [k]: v }));
  }

  async function save(e: React.FormEvent) {
    e.preventDefault();
    setSaving(true);
    setMsg(null);
    try {
      // Only send the API key if the user typed a new one.
      const body: Record<string, string> = {
        provider: form.provider,
        ollama_url: form.ollama_url,
        ollama_model: form.ollama_model,
        openrouter_model: form.openrouter_model,
      };
      if (form.openrouter_api_key) body.openrouter_api_key = form.openrouter_api_key;
      await updateLLMSettings(body);
      await load();
      setMsg({ ok: true, text: "Saved." });
    } catch {
      setMsg({ ok: false, text: "Save failed." });
    } finally {
      setSaving(false);
    }
  }

  async function runTest() {
    setMsg({ ok: true, text: "Testing…" });
    try {
      const r = await testLLM();
      setMsg({ ok: r.ok, text: r.ok ? `✓ ${r.provider}: ${r.detail}` : `✗ ${r.detail}` });
    } catch {
      setMsg({ ok: false, text: "Test request failed." });
    }
  }

  return (
    <div className="flex min-h-screen">
      <aside className="hidden md:flex">
        <Navbar />
      </aside>
      <main className="flex-1 p-8">
        <h2 className="text-2xl font-bold mb-6">Settings</h2>
        <div className="space-y-6 max-w-2xl">
          <Card>
            <CardTitle>AI / LLM Provider</CardTitle>
            <CardContent>
              <p className="text-sm text-fg-2 mb-4">
                Configure the LLM the AI features use. Pick a provider, or leave it on{" "}
                <span className="font-mono">auto</span> (Ollama first, then OpenRouter).
                {view?.active_provider ? (
                  <>
                    {" "}
                    Currently active:{" "}
                    <span className="font-semibold text-brand-press">{view.active_provider}</span>.
                  </>
                ) : (
                  <> No provider is configured yet.</>
                )}
              </p>

              <form onSubmit={save} className="space-y-4">
                <div>
                  <label className="text-sm font-medium">Provider</label>
                  <select
                    value={form.provider}
                    onChange={(e) => set("provider", e.target.value)}
                    className="mt-1 w-full px-4 py-2 rounded-md border border-border-strong bg-bg"
                  >
                    <option value="auto">auto (Ollama → OpenRouter)</option>
                    <option value="ollama">Ollama (local)</option>
                    <option value="openrouter">OpenRouter (cloud)</option>
                  </select>
                </div>

                <div className="border-t border-border pt-4">
                  <p className="text-xs uppercase tracking-wide text-fg-2 font-semibold mb-2">
                    Ollama
                  </p>
                  <label className="text-sm font-medium">Endpoint</label>
                  <Input
                    placeholder="http://host.docker.internal:11434"
                    value={form.ollama_url}
                    onChange={(e) => set("ollama_url", e.target.value)}
                  />
                  <label className="text-sm font-medium mt-3 block">Model</label>
                  <Input
                    placeholder="llama3.2:3b"
                    value={form.ollama_model}
                    onChange={(e) => set("ollama_model", e.target.value)}
                  />
                </div>

                <div className="border-t border-border pt-4">
                  <p className="text-xs uppercase tracking-wide text-fg-2 font-semibold mb-2">
                    OpenRouter
                  </p>
                  <label className="text-sm font-medium">API token</label>
                  <Input
                    type="password"
                    placeholder={
                      view?.openrouter_api_key_set
                        ? `saved (${view.openrouter_api_key_hint}) — leave blank to keep`
                        : "sk-or-…"
                    }
                    value={form.openrouter_api_key}
                    onChange={(e) => set("openrouter_api_key", e.target.value)}
                  />
                  <label className="text-sm font-medium mt-3 block">Model</label>
                  <Input
                    placeholder="anthropic/claude-3.5-sonnet"
                    value={form.openrouter_model}
                    onChange={(e) => set("openrouter_model", e.target.value)}
                  />
                </div>

                <div className="flex items-center gap-3 pt-2">
                  <Button type="submit" disabled={saving}>
                    {saving ? "Saving…" : "Save"}
                  </Button>
                  <Button type="button" variant="secondary" onClick={runTest}>
                    Test connection
                  </Button>
                  {msg && (
                    <span className={`text-sm ${msg.ok ? "text-success" : "text-danger"}`}>
                      {msg.text}
                    </span>
                  )}
                </div>
              </form>
            </CardContent>
          </Card>

          <Card>
            <CardTitle>API Configuration</CardTitle>
            <CardContent>
              <p className="text-sm text-fg-1 mb-2">Backend API Base URL</p>
              <div className="p-3 bg-bg-muted rounded-md text-sm font-mono">
                {process.env.NEXT_PUBLIC_API_URL || "http://localhost:8095"}
              </div>
            </CardContent>
          </Card>
        </div>
      </main>
    </div>
  );
}
