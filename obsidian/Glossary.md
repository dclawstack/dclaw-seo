# Glossary

| Term | Meaning |
|------|---------|
| **AI SEO Copilot** | The mandated P0.1 feature: analyses pages/sites against the SERP top-10 and returns prioritised optimization actions. |
| **SERP** | Search Engine Results Page. SERP features = featured snippets, "people also ask", etc. |
| **Keyword clustering** | Grouping keywords into topic clusters via embeddings/semantic similarity. |
| **Search intent** | Classification of a query as informational / transactional / navigational. |
| **Content brief** | A generated outline (target keyword, questions, headings, length, internal links) used to write SEO content. |
| **Core Web Vitals** | Google's UX performance metrics: LCP, FID/INP, CLS. |
| **Toxic link** | A backlink likely to harm rankings; flagged by the backlink-analysis AI. |
| **DPanel** | The DClaw admin panel; apps register via `frontend/public/dclaw-manifest.json`. |
| **Repository pattern** | DClaw rule: all DB access goes through `app/repositories/`, never inline in routers. |
| **Sacred stack** | The non-negotiable DClaw tech stack (Next.js 14 / FastAPI / SQLAlchemy 2.0 / Postgres 16). |
| **Maturity Tier** | DClaw readiness rating: 🟢 Tier 1 mature · 🟡 Tier 2 partial · (etc). SEO is now Tier 1 (v2.0). |
| **NAP** | Name / Address / Phone — the core local-SEO identity; the Local SEO Manager scans citations for NAP consistency. |
| **NAP consistency scan** | Normalized comparison (legal-suffix, street-abbrev, apostrophe-aware) of each citation against a business's canonical NAP, scoring consistency. |
| **GBP** | Google Business Profile — the local listing the Local SEO Manager syncs from (behind `GBP_API_KEY`). |
| **Cost ledger** | Per-org record of every metered LLM call (tokens + cost), wired centrally via a request-scoped `Meter` ContextVar; backs the cost cap and metered billing. |
| **Cost cap** | An org's monthly LLM spend ceiling; once reached, AI calls return HTTP 402 (`QuotaExceeded`). |
| **Multi-tenant (org→project)** | Users belong to an organization, which owns projects + a billing account; data and LLM spend are isolated per org. |
| **JWT auth** | Self-contained auth (bcrypt + PyJWT HS256); all `/api/v1/*` feature routes require a Bearer token. |
| **CloudNativePG (CNPG)** | The Kubernetes operator that runs Postgres in prod; the Helm chart provisions a CNPG `Cluster`. |
| **Prometheus `/metrics`** | Exposition endpoint scraped for request-rate/latency; visualized in the provisioned Grafana dashboard. |
| **Originality score** | Internal 5-gram redundancy check on AI-written content (not a web plagiarism scan — that needs an external provider). |

## Related

- [[Architecture]]
- [[Project Overview]]
