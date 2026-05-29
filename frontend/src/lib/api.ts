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

export async function generateBrief(keyword: string) {
  return apiFetch("/api/v1/seo/content/brief", {
    method: "POST",
    body: JSON.stringify({ keyword }),
  });
}

export async function checkPerformance(url: string, strategy = "mobile") {
  return apiFetch("/api/v1/seo/performance", {
    method: "POST",
    body: JSON.stringify({ url, strategy }),
  });
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

export async function writeArticle(
  keyword: string,
  opts?: { tone?: string; target_words?: number }
) {
  return apiFetch("/api/v1/seo/content/write", {
    method: "POST",
    body: JSON.stringify({ keyword, ...opts }),
  });
}

export async function generateMetaTags(input: {
  url?: string;
  content?: string;
  keyword?: string;
}) {
  return apiFetch("/api/v1/seo/meta", {
    method: "POST",
    body: JSON.stringify(input),
  });
}

export async function optimizeVideo(topic: string, keywords?: string[]) {
  return apiFetch("/api/v1/seo/video", {
    method: "POST",
    body: JSON.stringify({ topic, keywords }),
  });
}

// --- Local SEO ---
export async function createBusiness(body: {
  name: string;
  address: string;
  phone: string;
  website?: string;
}) {
  return apiFetch("/api/v1/local/businesses", { method: "POST", body: JSON.stringify(body) });
}

export async function listBusinesses() {
  return apiFetch("/api/v1/local/businesses");
}

export async function addCitation(
  businessId: number,
  body: { source: string; listed_name: string; listed_address: string; listed_phone: string; url?: string }
) {
  return apiFetch(`/api/v1/local/businesses/${businessId}/citations`, {
    method: "POST",
    body: JSON.stringify(body),
  });
}

export async function napScan(businessId: number) {
  return apiFetch(`/api/v1/local/businesses/${businessId}/nap-scan`);
}

export async function addReview(
  businessId: number,
  body: { source: string; author?: string; rating: number; text?: string }
) {
  return apiFetch(`/api/v1/local/businesses/${businessId}/reviews`, {
    method: "POST",
    body: JSON.stringify(body),
  });
}

export async function listReviews(businessId: number) {
  return apiFetch(`/api/v1/local/businesses/${businessId}/reviews`);
}
