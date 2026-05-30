# Build Log

Human-readable mirror of development progress. One row per completed task (Neon `plan.tasks` is the source of truth; this is the vault view). Append newest at the bottom.

| Date | Task | Title | Phase | Issue | PR | Outcome |
|------|------|-------|-------|-------|----|---------|
| 2026-05-29 | — | Planning setup (plan + Neon + Project #6 + 34 issues) | — | — | — | Tracking stood up; dev not yet started |
| 2026-05-29 | F0.1 | Resolve ports & fix config drift | Phase 0 | #1 | — | Canonical 8095/3006 propagated to AGENTS/REVISED-PRD; `.env.example` DB `dclaw_crm`→`dclaw_seo`; `docker-compose config` passes; crm collision deferred |
| 2026-05-29 | F0.2 | Introduce repository layer | Phase 0 | #2 | — | `BaseRepository` + 4 per-model repos; service writes via repos (no `db.add`); consolidated duplicate `Base` to `app.models.base`; `get_db` moved to `core.database` |
| 2026-05-29 | F0.3 | Initialize Alembic + initial migration | Phase 0 | #3 | — | Async `env.py` wired to settings + `Base.metadata`; migration `db8a8e5e228a` (4 tables); clean DB→`upgrade head` verified + reversible; CI runs migrations |
| 2026-05-29 | F0.4 | Replace mock SEO data with real persistence | Phase 0 | #4 | — | Removed all `random.*`; deterministic sha256 estimates flagged `TODO(P1)`; responses read persisted JSON; rank history grows from real DB rows |
| 2026-05-29 | F0.5 | Test baseline + CI green | Phase 0 | #5 | — | Fixed conftest import + health path; added `test_seo.py` (4 endpoints + validation); 7 passed, 90% coverage (target ≥70%) |
| 2026-05-29 | F0.6 | structlog logging + config hygiene | Phase 0 | #6 | — | structlog setup (console/JSON); structured startup/shutdown logs; `SettingsConfigDict` (deprecation gone); structlog added to requirements |
| 2026-05-29 | F0.7 | Docs accuracy pass | Phase 0 | #7 | — | Reconciled docs/reference (ports 8095/3006, API URL, health version, SEO endpoints); marked Alembic + DPanel manifest resolved in vault |
| 2026-05-29 | F0.8 | Adopt DKube purple design system | Phase 0 | #33 | #35 | Ported `brand.css` `--dk-*` + Poppins (next/font) verbatim from dclaw-marketing; tailwind bound to tokens; restyled all components/pages off emerald→purple; favicons/manifest + `design/` kit; `npm run build` green (8 routes, no warnings); supersedes #10B981 |
| 2026-05-29 | H.8 | Marketing landing page (live on Vercel) | Phase 4 | #34 | #36 | Standalone `landing/` Next 15 app (Tailwind v4 + lucide), DKube purple; deployed to **https://dclaw-seo.vercel.app** (200). Pulled forward on request |
| 2026-05-29 | P0.0 | LLM provider abstraction (Ollama + OpenRouter) | Phase 1 | #8 | — | `services/llm.py` single call site; `LLM_PROVIDER` auto/ollama/openrouter + fallback; env config slots; 12 tests |
| 2026-05-29 | P0.1 | AI SEO Copilot | Phase 1 | #9 | — | `POST /ai/copilot`: real page fetch + on-page signals + best-practice prioritized actions; LLM re-ranks when configured; floating widget in layout; 20 tests |
| 2026-05-29 | P0.2 | Keyword Research & Clustering | Phase 1 | #10 | — | Real Google Suggest expansion (50, free/keyless) + LLM intent/bands/clustering; `suggestions` widened to Text (mig `37e17d00997e`); no fabricated numbers |
| 2026-05-29 | P0.3 | Content Optimizer | Phase 1 | #11 | — | Real Flesch readability + keyword-density score 0–100 + data-driven checklist; LLM optional rewrite; works without LLM |
| 2026-05-29 | P0.4 | Rank Tracking & SERP Monitoring | Phase 1 | #12 | — | Pluggable SERP provider (NullSERPProvider default) + manual real positions; >5-drop alerts; never fabricated |
| 2026-05-29 | P0.5 | Dashboard | Phase 1 | #13 | — | `GET /seo/stats` real counts + latest score + recent activity (repo `count()`/`recent()`); dashboard cards wired to live data |
| 2026-05-29 | P0.6 | v1.0 demo wiring + smoke | Phase 1 | #14 | — | `scripts/demo.py` full P0 flow (all ✓) + `export_openapi.py`; frontend Dockerfile `ARG NEXT_PUBLIC_API_URL`; compose config valid; README runbook |
| 2026-05-29 | — | In-app LLM config + use local Ollama | Extra | — | #39 | Settings UI + DB-backed runtime config (`llm_settings`, mig `1c36cf764fa9`); compose defaults to host Ollama (`host.docker.internal`, `llama3.2:3b`); also fixed local fonts (#38) |
| 2026-05-29 | P1.2 | Technical Site Audit (deep crawl) | Phase 2 | #16 | — | Real httpx BFS crawler; ~12 issue types; weighted score; optional LLM summary; replaces stub + removes `seo_service.py`; `site_audits.pages_crawled` (mig `d7282a933801`) |
| 2026-05-29 | P1.1 | Backlink Analysis & Monitoring | Phase 2 | #15 | — | `backlinks` table (mig `1183625fe59a`); pluggable provider (default none) + user links; heuristic+LLM toxicity; new/lost detection |
| 2026-05-29 | P1.3 | Competitor Gap Analysis | Phase 2 | #17 | — | Your Suggest keywords vs competitor page terms; gap + opportunity scores; optional LLM; stateless |
| 2026-05-29 | P1.4 | AI Content Brief Generator | Phase 2 | #18 | — | Suggest related/question queries → outline/questions/length/secondary kw; LLM-enriched or deterministic |
| 2026-05-29 | P1.5 | Core Web Vitals / Performance Monitor | Phase 2 | #19 | — | Real Lighthouse CWV via PageSpeed Insights (free/keyless, optional `PAGESPEED_API_KEY`); `performance_metrics` (mig `e3ff7fe3c6e1`) trends; recommendations |
| 2026-05-30 | — | Hide copilot widget on welcome splash | Maint | — | #45 | `usePathname` guard returns `null` on `/` so the floating copilot is hidden on the bare splash; tsc clean (seo's landing fallback was already correct at 3006, so no port-fix PR) |
| 2026-05-30 | — | Local Docker refresh (standalone) | Maint | — | — | Rebuilt + recreated via `docker-compose.standalone.yml` (bundled per-app Postgres, internal 5432, not host-published); new code verified live on :3006 |
| 2026-05-30 | P2.1 | AI Content Writer | Phase 3 | #20 | #47 | Long-form draft via LLM; internal 5-gram originality score + LLM fact-check notes; Google-Suggest scaffold fallback. `/writer` page |
| 2026-05-30 | P2.2 | AI Meta Tags & Schema | Phase 3 | #21 | #47 | Length-bounded title/meta, OG + Twitter cards, JSON-LD Article schema; from URL or pasted content. `/meta` page |
| 2026-05-30 | P2.4 | Video SEO | Phase 3 | #23 | #47 | 3 CTR-tuned YouTube title variants, description, tags, hashtags. `/video` page |
| 2026-05-30 | P2.3 | Local SEO Manager | Phase 3 | #22 | #48 | GBP sync (env), citation tracking, NAP consistency scan (suffix/abbrev/apostrophe-aware), AI review replies; `local_businesses`/`citations`/`reviews` (mig `a0bf4ea01bf5`). `/local` page |
| 2026-05-30 | P2.5 | White-Label Reports | Phase 3 | #24 | #49 | Branded PDF (fpdf2) + CSV from real metrics; AI exec summary; scheduled delivery behind SMTP; `report_schedules` (mig `b1c2d3e4f5a6`). `/reports` page |
| 2026-05-30 | P2.6 | Predictive Rank Forecasting | Phase 3 | #25 | #49 | OLS trend on real rank history, competitor-adjusted, rank-floored; `insufficient_data` when <2 points (no invented numbers). `/forecast` page |
| 2026-05-30 | H.1 | Auth (self-contained JWT) | Phase 4 | #26 | #50 | `users` table, bcrypt, PyJWT; `/auth` register/login/me; HTTPBearer dep protects all feature routers; `/login` page + token-aware apiFetch |
| 2026-05-30 | H.3 | Multi-tenant + cost ledger/quota | Phase 4 | #28 | #50 | `organizations→projects` hierarchy; `llm_cost_ledger`; central metering via a request-scoped `Meter` ContextVar in `services/llm.py`; monthly cost cap (402); migration `c2d3e4f5a6b7`. `/account` page |
| 2026-05-30 | H.2 | Billing (Stripe-optional) | Phase 4 | #27 | #51 | free/starter/pro plans; per-seat + metered invoicing from the cost ledger; Stripe via httpx behind env; `billing_accounts` (mig `d3e4f5a6b7c8`). `/billing` page |
| 2026-05-30 | H.4 | Observability | Phase 4 | #29 | #52 | prometheus-client `/metrics` (request count + latency, route-template labels) + `MetricsMiddleware`; `/admin/health`; `observability/` Prometheus + auto-provisioned Grafana dashboard |
| 2026-05-30 | H.5 | Security hardening | Phase 4 | #30 | #52 | Security headers middleware (HSTS in prod); non-root frontend container; SECRET_KEY warning; `SECURITY.md`; pip-audit script + CI job. **Bumped Next.js 14.2.5→14.2.35 to clear a critical CVE** |
| 2026-05-30 | H.6 | Helm / K8s production deploy | Phase 4 | #31 | #53 | Consolidated `helm/dclaw-seo`: backend+frontend ClusterIP, non-root securityContext, probes, CloudNativePG, TLS ingress, per-env values, deploy CI (lint+template+guarded upgrade). Removed stale duplicate root chart |
| 2026-05-30 | H.7 | Docs, demo & YC checklist | Phase 4 | #32 | #54 | `docs/USER_GUIDE.md` (+ generated PDF), `DEMO.md` walkthrough, REVISED-PRD §8 checklist closed (15/15), README→v2.0, `docs/releases/v2.0.0.md` |

> **🏁 2026-05-30 — Plan complete.** All 34 tasks / 5 phases Done (v2.0). Neon 34/34, GitHub 34/34 closed, Project #6 34/34 Done. Live stack healthy at version 2.0.0.

## Related

- [[Home]]
- [[Dev Plan]] — phases, mirrors, and the per-task loop
- [[Roadmap]] — feature-level P0/P1/P2 view
