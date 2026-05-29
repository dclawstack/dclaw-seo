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
| **Brand color** | `#10B981` |
| **Maturity** | 🟡 Tier 2 — Partial (P0 partially implemented) |
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

`/` · `/dashboard` · `/audit` · `/keywords` · `/content` · `/rankings` · `/settings`

## API endpoints (README)

| Method | Path | Description |
|--------|------|-------------|
| GET | `/health` | Health check |
| POST | `/api/v1/seo/audit` | Site audit |
| POST | `/api/v1/seo/keywords` | Keyword research |
| POST | `/api/v1/seo/content/optimize` | Content optimization |
| POST | `/api/v1/seo/rankings/track` | Rankings tracking |
