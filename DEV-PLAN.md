# DClaw SEO — Phase-Wise Development Plan

> Generated 2026-05-29 from `AGENTS.md`, `REVISED-PRD.md` (v2.3 + YC gap analysis), `PLAN-v1.2.md`, `SCALING-PLAYBOOK.md`, `PRODUCT-SPEC.md.template`, and a read of the current `backend/`+`frontend/` source.
>
> **Source of truth for task status is the Neon Postgres DB** (project `dclaw-seo` / `restless-queen-89786738`, schema `plan`). This document is the human-readable narrative; the **GitHub Project "DClaw SEO Project"** mirrors the DB as issues. Update the DB first, then the issue/project field.

---

## Legend

- **Track:** `Backend` · `Frontend` · `AI` · `Infra` · `Docs`
- **Priority:** `P0` (must-have / demo) · `P1` (should-have) · `P2` (could-have)
- **Status:** `Todo` · `In Progress` · `Done` · `Blocked`
- Task keys (e.g. `F0.2`, `P0.1`) are stable identifiers shared across this doc, the DB, and the issue title.

---

## Current State (2026-05-29)

What the scaffold already has, and what's missing — this is why Phase 0 exists.

- ✅ **Present**
    - FastAPI app (`backend/app/main.py`), config, async engine + `get_db` (`core/`)
    - 4 models: `keyword`, `ranking`, `site_audit`, `content_optimization`
    - Pydantic v2 schemas (`schemas/seo.py`) + one router (`api/v1/seo.py`) with 4 POST endpoints + `/health`
    - Frontend pages: `dashboard`, `audit`, `keywords`, `content`, `rankings`, `settings`
    - `frontend/public/dclaw-manifest.json` (DPanel) — **already present**
    - Deps declared: `asyncpg`, `alembic`, `httpx`, `structlog`, `pytest-asyncio`
- ❌ **Missing / broken (Phase 0 targets)**
    - **No repository layer** (`app/repositories/`) — `AGENTS.md` mandates it; the service writes via `db.add` directly
    - **No Alembic** (`alembic/`, `alembic.ini`) — REVISED-PRD gap #1
    - **Mock data** — `services/seo_service.py` returns `random.*` values (violates the `NO MOCK DATA` rule)
    - **No AI Copilot** — the YC S25/W26 mandate (REVISED-PRD §9) is unmet
    - **Tests** — only `test_health.py`; no coverage of the SEO endpoints
    - **Config drift** — `.env.example` `DATABASE_URL` points at `dclaw_crm`; ports disagree across `README` (3006/8095), `AGENTS` (3008/8008), `REVISED-PRD` (3098/18168 TBD)
    - No LLM provider client (Ollama/OpenRouter), no `pgvector`, no auth (Logto), no billing (Stripe), no observability

---

## Phase 0 — Foundation & Scaffold Hardening
**Goal:** a green, real (no-mock), deployable baseline that obeys every `AGENTS.md` rule. **Target:** `v0.1.0`.

- **F0.1 — Resolve ports & fix config drift** · Infra · P0
    - Pick one canonical `(backend, frontend)` port pair and reconcile `README` / `AGENTS` / `REVISED-PRD` / the shared port registry
    - Fix `.env.example` `DATABASE_URL` (`dclaw_crm` → `dclaw_seo`) and `NEXT_PUBLIC_API_URL`
    - Verify `docker-compose.yml` port mappings match `EXPOSE`/`ENV PORT`
    - *Acceptance:* one port pair everywhere; `docker compose config` passes
- **F0.2 — Introduce repository layer** · Backend · P0
    - Add `app/repositories/base.py` (`BaseRepository`) + one repo per model
    - Refactor `seo_service.py` to go through repositories (no direct `db.add`)
    - *Acceptance:* no DB access outside `repositories/`; `Depends(get_db)` only
- **F0.3 — Initialize Alembic + initial migration** · Backend · P0
    - `alembic init`; async `env.py`; autogenerate initial migration for the 4 existing models
    - Wire `alembic upgrade head` into CI/startup docs
    - *Acceptance:* clean DB → `upgrade head` builds all tables; CI runs it
- **F0.4 — Replace mock SEO data with real persistence** · Backend · P0
    - Remove `random.*` from `run_site_audit` / `research_keywords` / `optimize_content` / `track_rankings`
    - Persist + read real rows; keep deterministic stubs **only** where a real external API is not yet wired (clearly flagged `TODO(P1)`)
    - *Acceptance:* no `random`/`MOCK_*`; responses come from the DB
- **F0.5 — Test baseline + CI green** · Backend · P0
    - `conftest.py` test-DB override on `localhost:5432`; `httpx.AsyncClient` + `ASGITransport`
    - Tests for all 4 SEO endpoints + health; keep `pytest-asyncio==0.24.0`
    - *Acceptance:* `pytest` green locally and in CI; ≥70% backend coverage
- **F0.6 — structlog logging + config hygiene** · Backend · P1
    - Replace any `print()` with `structlog`; central settings via `pydantic-settings`
    - *Acceptance:* no `print`; logs structured
- **F0.7 — Docs accuracy pass** · Docs · P1
    - Reconcile `docs/reference/*` + `AGENTS.md` port/identity with F0.1; note manifest already present
    - *Acceptance:* docs match code
- **F0.8 — Adopt DKube purple design system** · Frontend · P0
    - Port `frontend/src/styles/brand.css` (`--dk-*` purple tokens) **verbatim** from `dclaw-marketing`
    - Load **Poppins** via `next/font/google`; expose `--dk-font-sans`; wire in `app/layout.tsx`
    - Copy the DKube brand source kit into `design/` (`BRAND_GUIDELINES.md`, `colors_and_type.css`, fonts, logos/assets) — aligns with the `dkube-design` skill
    - Restyle the pre-built UI components to consume `--dk-*` tokens; add DClaw logo/favicons; no hardcoded hex; light mode only
    - *Decision:* the unified **DKube purple** brand is used identically to marketing — this **supersedes** the emerald `#10B981` named in REVISED-PRD
    - *Acceptance:* every surface uses `--dk-*` tokens; renders in the DKube purple system; Poppins loaded

---

## Phase 1 — P0 Foundation Features (demo-ready)
**Goal:** the four market-ready P0 features + the mandated AI Copilot, end-to-end (API + UI + real persistence). **Target:** `v1.0.0`.

- **P0.0 — LLM provider abstraction** · AI · P0  *(enabler for all AI features)*
    - `services/llm.py`: Ollama (local) primary, OpenRouter + Kimi K2.5 fallback; provider-swappable; structured prompts
    - *Acceptance:* one call site; falls back to Ollama when cloud is down
- **P0.1 — AI SEO Copilot** · AI · P0  *(YC mandate, REVISED-PRD §9)*
    - Backend `POST /api/v1/ai/copilot`: analyse a page/site vs SERP top-10; RAG over SEO best-practices corpus (pgvector)
    - Returns **prioritised next actions**, not just answers
    - Frontend: floating copilot accessible from every page (chat/sidebar)
    - *Acceptance:* audit 100 pages < 60s; returns top-10 prioritised actions
- **P0.2 — Keyword Research & Clustering** · AI+Backend · P0
    - LLM long-tail expansion; intent classification (informational / transactional / navigational); semantic clustering via embeddings
    - Frontend: keyword explorer with cluster visualisation
    - *Acceptance:* 50+ keyword suggestions; intent classified per keyword
- **P0.3 — Content Optimizer** · AI+Backend · P0
    - Score 0–100 on readability + keyword-density + semantic coverage; before/after; actionable checklist
    - Frontend: optimization report page
    - *Acceptance:* score + 5+ improvements per page
- **P0.4 — Rank Tracking & SERP Monitoring** · Backend · P0
    - Scheduled rank checks; SERP-feature extraction; anomaly detection on a >5-position drop; trend charts
    - *Acceptance:* daily checks; track 1000+ keywords; alert on >5 drop
- **P0.5 — Dashboard** · Frontend · P0
    - Visibility/traffic summary cards, recent activity, quick actions wired to real endpoints
    - *Acceptance:* all cards backed by real API data
- **P0.6 — v1.0 demo wiring + smoke** · Infra · P0
    - `docker compose up -d` green; OpenAPI export; scripted demo flow across all P0 features
    - *Acceptance:* fresh clone → demo runs end-to-end

---

## Phase 2 — P1 Platform Features
**Goal:** deepen the platform toward parity with Ahrefs/SEMrush-class tooling. **Target:** `v1.1 → v1.2`.

- **P1.1 — Backlink Analysis & Monitoring** · Backend+AI · P1
    - Backlink ingestion, anchor text, referring domains; AI toxic-link detection + outreach scoring; new/lost alerts
    - *Acceptance:* analyse 10K links; flag toxic ≥90% precision target
- **P1.2 — Technical Site Audit (deep crawl)** · Backend+AI · P1
    - `httpx` crawler; 50+ issue types (broken links, dup content, missing alt, slow pages, mobile); AI priority + fix instructions
    - *Acceptance:* crawl 10K pages; 50+ issue types detected
- **P1.3 — Competitor Gap Analysis** · Backend+AI · P1
    - Compare keyword profiles vs competitors; gap detection + opportunity scores; gap-matrix UI
    - *Acceptance:* track 5 competitors; 10+ content gaps
- **P1.4 — AI Content Brief Generator** · AI · P1
    - SERP analysis + LLM brief (outline, questions, length, internal links, H2/H3); export to Docs/Notion
    - *Acceptance:* brief in < 30s with H2/H3 recommendations
- **P1.5 — Core Web Vitals / Performance Monitor** · Backend+Infra · P1
    - Lighthouse CI integration; LCP/INP/CLS trends; recommendations
    - *Acceptance:* historical CWV per URL; trend dashboard

---

## Phase 3 — P2 Vertical / Scale Features
**Goal:** differentiation + breadth. **Target:** `v1.3+`.

- **P2.1 — AI Content Writer** · AI · P2 — long-form generation + fact-checking (1000-word article < 60s; plagiarism < 5%)
- **P2.2 — AI Meta Tags & Schema** · AI · P2 — auto title tags, meta descriptions, JSON-LD schema
- **P2.3 — Local SEO Manager** · Backend+AI · P2 — GBP sync, citation tracking, review monitoring/responses, NAP consistency
- **P2.4 — Video SEO** · AI · P2 — YouTube title/description/tag optimization; 3 title variants
- **P2.5 — White-Label Reports** · Backend · P2 — branded PDF/CSV; scheduled delivery; AI executive summary
- **P2.6 — Predictive Rank Forecasting** · AI · P2 — forecast ranking changes from content/competitor activity

---

## Phase 4 — Platform Hardening, Market-Ready & Launch
**Goal:** close the YC/market-ready gaps from REVISED-PRD §4/§8/§9 — auth, billing, multi-tenant, observability, prod deploy. **Target:** `v2.0`.

- **H.1 — Auth (Logto / JWT)** · Backend · P0 — JWT validation on all protected routes; login UI
- **H.2 — Billing (Stripe)** · Backend · P1 — metered or per-seat; usage → invoice
- **H.3 — Multi-tenant isolation + cost ledger/quota** · Backend · P1 — Org→Project hierarchy; per-org LLM cost ledger + quota/cost-cap (mirror dclaw-marketing patterns)
- **H.4 — Observability** · Infra · P1 — Prometheus/Grafana; `/admin/health`; structured logs/metrics
- **H.5 — Security & secrets hardening** · Infra · P0 — no hardcoded secrets (`.env`/K8s Secrets); non-root containers; TLS ingress; dependency audit
- **H.6 — Helm / K8s production deploy** · Infra · P1 — CloudNativePG; `ClusterIP`; deploy workflow; values per env
- **H.7 — Docs, demo & YC market-ready checklist** · Docs · P1 — user guide + PDF; demo video; close REVISED-PRD §8 scaffold checklist
- **H.8 — Marketing landing page (standalone Next.js, Vercel-deferred)** · Frontend · P1
    - Scaffold a **standalone `landing/` Next.js app** (own `package.json`/`tsconfig`/`next.config`), mirroring `dclaw-marketing/landing`
    - Apply the same **DKube purple** design system (shared `--dk-*` tokens + Poppins)
    - Sections: **hero** (headline + a *single CTA button → the frontend app*), features (P0 capabilities), how-it-works, footer
    - Brand assets (DClaw logos, favicons, `site.webmanifest`); `NEXT_PUBLIC_APP_URL` as the CTA target; responsive + SEO/OG meta
    - **Vercel hookup deferred** — structure Vercel-ready, no connection wired now
    - *Acceptance:* `landing/` builds green; hero CTA links through to the app; design matches the product

---

## How progress is tracked

1. **Neon DB (`plan` schema) is authoritative.** Set `tasks.status` there first.
2. **GitHub Project "DClaw SEO Project"** mirrors each task as an issue with `Phase` / `Track` / `Priority` / `Status` fields; the issue body holds the subtask checklist.
3. During dev: move the task `Todo → In Progress → Done` in the DB, then reflect it on the issue (status field + close on completion). Reference the task key (e.g. `P0.1`) in branch names and commits.
