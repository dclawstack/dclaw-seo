const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8095";

export async function apiFetch(path: string, options?: RequestInit) {
  const res = await fetch(`${API_BASE}${path}`, {
    ...options,
    headers: {
      "Content-Type": "application/json",
      ...options?.headers,
    },
  });
  if (!res.ok) throw new Error(`API error: ${res.status}`);
  return res.json();
}

export async function auditSite(url: string) {
  return apiFetch("/api/v1/seo/audit", {
    method: "POST",
    body: JSON.stringify({ url }),
  });
}

export async function researchKeywords(seed: string) {
  return apiFetch("/api/v1/seo/keywords", {
    method: "POST",
    body: JSON.stringify({ seed }),
  });
}

export async function optimizeContent(targetKeyword: string, content: string) {
  return apiFetch("/api/v1/seo/content/optimize", {
    method: "POST",
    body: JSON.stringify({ target_keyword: targetKeyword, content }),
  });
}

export async function trackRankings(keyword: string, url: string, position?: number) {
  return apiFetch("/api/v1/seo/rankings/track", {
    method: "POST",
    body: JSON.stringify({ keyword, url, position }),
  });
}

export async function getStats() {
  return apiFetch("/api/v1/seo/stats");
}

export async function analyzeBacklinks(
  targetUrl: string,
  links: { source_url: string; anchor_text?: string }[]
) {
  return apiFetch("/api/v1/seo/backlinks/analyze", {
    method: "POST",
    body: JSON.stringify({ target_url: targetUrl, links }),
  });
}

export async function competitorGap(seed: string, competitorUrl: string) {
  return apiFetch("/api/v1/seo/competitor/gap", {
    method: "POST",
    body: JSON.stringify({ seed, competitor_url: competitorUrl }),
  });
}

export async function getLLMSettings() {
  return apiFetch("/api/v1/settings/llm");
}

export async function updateLLMSettings(body: Record<string, string>) {
  return apiFetch("/api/v1/settings/llm", { method: "PUT", body: JSON.stringify(body) });
}

export async function testLLM() {
  return apiFetch("/api/v1/settings/llm/test", { method: "POST" });
}

export async function copilotAnalyze(url: string, question?: string) {
  return apiFetch("/api/v1/ai/copilot", {
    method: "POST",
    body: JSON.stringify({ url, question }),
  });
}
