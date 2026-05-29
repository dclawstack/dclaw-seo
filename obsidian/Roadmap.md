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

## P1 — Should have (v1.1–1.2)

- **P1.1 Backlink Analysis** — toxic-link detection + outreach scoring.
- **P1.2 Site Audit** — crawl 10K pages; 50+ issue types; AI priority scoring.
- **P1.3 Competitor Analysis** — track 5 competitors; 10+ content gaps.
- **P1.4 Content Brief Generator** — brief in <30s with H2/H3 recommendations.

## P2 — Could have (v1.3+)

- **P2.1 AI Content Writer** — long-form generation + fact-checking.
- **P2.2 Local SEO** — GBP sync, citations, review responses.
- **P2.3 Video SEO** — YouTube title/description/tag optimization.
- **P2.4 White-Label Reports** — branded, scheduled client reports.

## Implementation sequence (PLAN-v1.2)

1. **Wk 1–2:** AI SEO Copilot + Keyword Research
2. **Wk 3–4:** Rank Tracking + Site Audit
3. **Wk 5–6:** Competitor Gap + Content Briefs
4. **Wk 7–8:** Backlink Analysis + Performance Monitor

## Related

- [[Project Overview]]
- [[Open Issues]]
