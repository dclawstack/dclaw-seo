"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { Card, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { loginUser, registerUser } from "@/lib/api";

export default function LoginPage() {
  const router = useRouter();
  const [mode, setMode] = useState<"login" | "register">("login");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [orgName, setOrgName] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setError("");
    setLoading(true);
    try {
      if (mode === "register") {
        await registerUser(email, password, orgName);
      } else {
        await loginUser(email, password);
      }
      router.push("/dashboard");
    } catch (err: any) {
      setError(err?.message || "Something went wrong");
    } finally {
      setLoading(false);
    }
  }

  return (
    <main className="flex min-h-screen items-center justify-center p-8 bg-bg-muted">
      <Card className="w-full max-w-sm">
        <CardContent>
          <div className="flex items-center gap-2 mb-6">
            <img src="/brand/logos/dclaw-icon-purple.svg" alt="" className="h-8 w-8" />
            <h1 className="text-xl font-bold text-brand">DClaw SEO</h1>
          </div>
          <div className="flex gap-2 mb-4 text-sm">
            <button
              className={mode === "login" ? "font-semibold text-brand-press" : "text-fg-2"}
              onClick={() => setMode("login")}
              type="button"
            >
              Sign in
            </button>
            <span className="text-fg-2">·</span>
            <button
              className={mode === "register" ? "font-semibold text-brand-press" : "text-fg-2"}
              onClick={() => setMode("register")}
              type="button"
            >
              Create account
            </button>
          </div>
          <form onSubmit={handleSubmit} className="space-y-3">
            {mode === "register" && (
              <Input placeholder="Organization name" value={orgName} onChange={(e) => setOrgName(e.target.value)} />
            )}
            <Input type="email" placeholder="Email" value={email} onChange={(e) => setEmail(e.target.value)} />
            <Input type="password" placeholder="Password (min 8 chars)" value={password} onChange={(e) => setPassword(e.target.value)} />
            {error && <p className="text-sm text-danger">{error}</p>}
            <Button type="submit" disabled={loading} className="w-full">
              {loading ? "..." : mode === "register" ? "Create account" : "Sign in"}
            </Button>
          </form>
        </CardContent>
      </Card>
    </main>
  );
}
