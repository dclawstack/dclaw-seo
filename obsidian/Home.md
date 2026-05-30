# DClaw SEO — Vault Home

> Project wiki for **DClaw SEO**. Synthesised from the repo docs on 2026-05-29; **updated 2026-05-30 to v2.0 (all 5 phases / 34 tasks complete).**
> Ground truth is always `git log` / the source tree; this vault is the human-readable map.

---

## Quick links

- [[Project Overview]] — what DClaw SEO is and who it's for
- [[Architecture]] — stack, ports, directory layout, anti-patterns
- [[Roadmap]] — P0 → P1 → P2 + hardening feature plan
- [[Dev Plan]] — phase-wise build plan (mirrored to Neon + GitHub Project #6)
- [[Build Log]] — per-task progress as development lands
- [[Open Issues]] — known gaps and scaffold inconsistencies
- [[Glossary]] — terms and acronyms

---

## At a glance

| | |
|---|---|
| **App ID** | `seo` |
| **Tagline** | Rank higher with AI |
| **Category** | Marketing |
| **Brand color** | DKube purple `#7660A8` (supersedes the old emerald `#10B981`) |
| **Maturity** | 🟢 **v2.0 — ALL phases complete** (Phases 0–4 / 34 tasks shipped, market-ready) |
| **Stack** | Next.js 14 · FastAPI · SQLAlchemy 2.0 · Postgres 16 · JWT auth · Prometheus · Helm |
| **Tests** | 92 backend tests green · 11 alembic migrations |
| **GitHub** | [dclawstack/dclaw-seo](https://github.com/dclawstack/dclaw-seo) |

---

## Repository ground-truth

```
backend/        FastAPI · SQLAlchemy 2.0 async · Pydantic v2 · repository pattern
frontend/       Next.js 14 App Router · Tailwind · pre-built UI components
landing/        Standalone Next.js marketing site (Vercel)
docs/           getting-started · guides · reference · releases · troubleshooting · USER_GUIDE
helm/dclaw-seo/ Production Helm chart (CloudNativePG, TLS ingress, per-env values)
observability/  Prometheus + Grafana stack (dashboard auto-provisioned)
obsidian/       This vault
.github/        CI workflows (incl. Claude Code Action) + deploy
```

## Frontend surfaces

**Core:** `/dashboard` · `/audit` · `/keywords` · `/content` · `/rankings` · `/backlinks` · `/competitor` · `/brief` · `/performance`
**AI content (P2):** `/writer` · `/meta` · `/video`
**Scale (P2):** `/local` · `/forecast` · `/reports`
**Platform:** `/login` · `/account` (org, projects, LLM cost ledger + cap) · `/billing` · `/settings`
— plus a global **AI Copilot** widget on every page.

## API endpoints (v2.0)

All `/api/v1/*` feature routes require a JWT; only `/health`, `/metrics`, `/admin/health`, `/api/v1/auth/*` are public.

| Method | Path | Description |
|--------|------|-------------|
| GET | `/health` · `/admin/health` · `/metrics` | Liveness · readiness · Prometheus |
| POST/GET | `/api/v1/auth/register` · `/login` · `/me` | Self-contained JWT auth |
| GET | `/api/v1/seo/stats` | Dashboard aggregates |
| POST | `/api/v1/seo/audit` · `/keywords` · `/content/optimize` · `/content/brief` · `/rankings/track` | Core SEO |
| POST | `/api/v1/seo/content/write` · `/meta` · `/video` | AI content suite (P2.1/P2.2/P2.4) |
| POST/GET | `/api/v1/seo/backlinks[/analyze]` · `/competitor/gap` · `/performance` | Backlinks · gap · CWV |
| POST/GET | `/api/v1/local/businesses/...` | Local SEO — GBP, citations, NAP scan, reviews (P2.3) |
| POST | `/api/v1/reports/preview` · `/pdf` · `/csv` · `/forecast` · `/schedules` | White-label reports + forecasting (P2.5/P2.6) |
| GET/PUT | `/api/v1/org` · `/org/cost-cap` · `/org/projects` · `/org/usage` | Multi-tenant + cost ledger (H.3) |
| GET/PUT | `/api/v1/billing/plans` · `/account` · `/subscribe` · `/invoice/preview` | Billing (H.2) |
| POST | `/api/v1/ai/copilot` | AI SEO copilot — prioritized actions |
| GET/PUT | `/api/v1/settings/llm` | In-app LLM provider config |
