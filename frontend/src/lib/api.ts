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

export async function trackRankings(keyword: string, url: string) {
  return apiFetch("/api/v1/seo/rankings/track", {
    method: "POST",
    body: JSON.stringify({ keyword, url }),
  });
}
