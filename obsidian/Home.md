# DClaw SEO — Vault Home

> Project wiki for **DClaw SEO**. Synthesised from the repo docs (`README.md`, `AGENTS.md`, `PLAN-v1.2.md`, `REVISED-PRD.md`) on 2026-05-29.
> Ground truth is always `git log` / the source tree; this vault is the human-readable map.

---

## Quick links

- [[Project Overview]] — what DClaw SEO is and who it's for
- [[Architecture]] — stack, ports, directory layout, anti-patterns
- [[Roadmap]] — P0 → P1 → P2 feature plan
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
| **Maturity** | 🟢 v1.2 — Phase 2 complete (P0 + P1 features shipped); Phase 3/4 pending |
| **Stack** | Next.js 14 · FastAPI · SQLAlchemy 2.0 · Postgres 16 |
| **GitHub** | [dclawstack/dclaw-seo](https://github.com/dclawstack/dclaw-seo) |

---

## Repository ground-truth

```
backend/    FastAPI · SQLAlchemy 2.0 async · Pydantic v2 · repository pattern
frontend/   Next.js 14 App Router · Tailwind · pre-built UI components
docs/       getting-started · guides · reference · releases · troubleshooting
helm/       Kubernetes Helm chart
obsidian/   This vault
.github/    CI workflows (incl. Claude Code Action)
```

## Frontend surfaces

`/` · `/dashboard` · `/audit` · `/keywords` · `/content` · `/rankings` · `/backlinks` · `/competitor` · `/brief` · `/performance` · `/settings` — plus a global **AI Copilot** widget on every page.

## API endpoints (v1.2)

| Method | Path | Description |
|--------|------|-------------|
| GET | `/health` | Health check |
| GET | `/api/v1/seo/stats` | Dashboard aggregates |
| POST | `/api/v1/seo/audit` | Technical site audit (real crawl) |
| POST | `/api/v1/seo/keywords` | Keyword research (Google Suggest + LLM) |
| POST | `/api/v1/seo/content/optimize` | Content optimizer (score + checklist) |
| POST | `/api/v1/seo/content/brief` | AI content brief |
| POST | `/api/v1/seo/rankings/track` | Rank tracking + drop alerts |
| POST/GET | `/api/v1/seo/backlinks[/analyze]` | Backlink toxicity + new/lost |
| POST | `/api/v1/seo/competitor/gap` | Competitor gap analysis |
| POST/GET | `/api/v1/seo/performance` | Core Web Vitals (PageSpeed Insights) |
| POST | `/api/v1/ai/copilot` | AI SEO copilot — prioritized actions |
| GET/PUT | `/api/v1/settings/llm` | In-app LLM provider config |
