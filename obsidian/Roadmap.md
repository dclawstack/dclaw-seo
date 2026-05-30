# Roadmap

From `REVISED-PRD.md` v2.3 and `PLAN-v1.2.md`. Every P0 must ship with an AI Copilot (YC S25/W26 mandate).

## Foundation (Phase 0) — ✅ complete (v0.1.0)

Scaffold hardening shipped: ports/config reconciled, repository layer, Alembic migrations, real (no-mock) persistence, test baseline (7 passed / 90% cov), structlog, docs accuracy, and the DKube purple design system. Product features below begin in **Phase 1**.

## P0 — Must have (demo-ready) — ✅ shipped in v1.0 (Phase 1)

| # | Feature | Status | Notes |
|---|---------|--------|-------|
| P0.0 | **LLM provider abstraction** | ✅ | Ollama + OpenRouter, config-driven, fallback |
| P0.1 | **AI SEO Copilot** | ✅ | Page fetch + on-page signals → prioritized actions; floating widget |
| P0.2 | **Keyword Research** | ✅ | Real Google Suggest (free) + LLM intent/bands/clustering |
| P0.3 | **Content Optimizer** | ✅ | Real readability + density score 0–100 + checklist; LLM rewrite |
| P0.4 | **Rank Tracking** | ✅ | Pluggable SERP provider + manual positions; >5-drop alerts |
| P0.5 | **Dashboard** | ✅ | Real `/seo/stats` (counts + recent activity) |
| P0.6 | **Demo wiring + smoke** | ✅ | Full P0 flow script + OpenAPI export |

> **AI enrichment + live SERP** activate when an LLM / SERP-data provider is configured; without one, real free data + honest notes are returned (no fabricated metrics).

## P1 — Should have (v1.1–1.2) — ✅ shipped in Phase 2

- ✅ **P1.1 Backlink Analysis** — heuristic+LLM toxic-link scoring; new/lost detection; pluggable provider.
- ✅ **P1.2 Site Audit** — real bounded httpx crawl; ~12 issue types; weighted score; optional LLM summary.
- ✅ **P1.3 Competitor Analysis** — Suggest keywords vs competitor page terms; gaps + opportunity scores.
- ✅ **P1.4 Content Brief Generator** — Suggest-driven outline/questions/length; LLM-enriched.
- ✅ **P1.5 Core Web Vitals** — real Lighthouse via PageSpeed Insights; trend history + recommendations.

> Same design rule as P0: real free data always; AI/provider-dependent depth activates when configured.

## P2 — Vertical / scale (Phase 3) — ✅ shipped in v1.3+

- ✅ **P2.1 AI Content Writer** — long-form draft + originality + LLM fact-check notes.
- ✅ **P2.2 AI Meta Tags & Schema** — title/meta, OG/Twitter, JSON-LD.
- ✅ **P2.3 Local SEO Manager** — GBP sync, citations, NAP consistency scan, AI review replies.
- ✅ **P2.4 Video SEO** — 3 CTR YouTube title variants, description, tags, hashtags.
- ✅ **P2.5 White-Label Reports** — branded PDF/CSV, AI exec summary, scheduled delivery.
- ✅ **P2.6 Predictive Rank Forecasting** — OLS trend on real history, competitor-adjusted.

## Hardening & launch (Phase 4) — ✅ shipped in v2.0

- ✅ **H.1 Auth** — self-contained JWT (bcrypt, login UI); all feature routes protected.
- ✅ **H.2 Billing** — free/starter/pro, per-seat + metered invoicing, Stripe-optional.
- ✅ **H.3 Multi-tenant + cost ledger** — org→project hierarchy; per-org LLM cost ledger + cap.
- ✅ **H.4 Observability** — Prometheus `/metrics`, `/admin/health`, Grafana dashboard.
- ✅ **H.5 Security** — non-root containers, security headers, no hardcoded secrets, dep audit.
- ✅ **H.6 Helm / K8s** — CloudNativePG, ClusterIP, TLS ingress, per-env values, deploy CI.
- ✅ **H.7 Docs & demo** — user guide (+PDF), demo walkthrough, REVISED-PRD §8 closed.
- ✅ **H.8 Marketing landing** — standalone Next.js site live on Vercel (shipped early).

> **🏁 All phases complete (v2.0).** 34/34 tasks; 92 backend tests; live at version 2.0.0.

## Implementation sequence (as built)

1. **Phase 0–1:** foundation + P0 (Copilot, Keywords, Optimizer, Rank, Dashboard) → v1.0
2. **Phase 2:** Audit, Backlinks, Competitor, Briefs, CWV → v1.2
3. **Phase 3:** Writer, Meta/Schema, Video, Local SEO, Reports, Forecasting → v1.3+
4. **Phase 4:** Auth, Billing, Multi-tenant, Observability, Security, Helm, Docs → v2.0

## Related

- [[Project Overview]]
- [[Open Issues]]
