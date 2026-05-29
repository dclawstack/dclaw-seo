# DClaw SEO

> **Rank higher with AI** · v2.0 (market-ready)

AI-native SEO platform for the DClaw Stack. Audit sites, research keywords,
generate and optimize content, track and forecast rankings, manage local SEO,
and ship white-label reports — with an AI Copilot on every page, multi-tenant
auth, per-org LLM cost metering, billing, observability, and a production Helm
chart.

📘 **[User Guide](docs/USER_GUIDE.md)** · 🎬 **[Demo walkthrough](DEMO.md)** ·
🔒 **[Security](SECURITY.md)** · ☸️ **[Deploy](helm/README.md)** ·
📈 **[Observability](observability/README.md)**

## Tech Stack

- **Frontend:** Next.js 14+, Tailwind CSS, shadcn/ui
- **Backend:** FastAPI, Pydantic v2, SQLAlchemy 2.0, asyncpg
- **Database:** PostgreSQL 16 (CloudNativePG in K8s)
- **AI:** provider-agnostic LLM layer (local Ollama default, OpenRouter fallback)
- **Auth/Tenancy:** JWT, org→project hierarchy, per-org LLM cost ledger + cap
- **Ops:** Prometheus `/metrics`, Grafana dashboard, Helm chart, CI/CD
- **Dev Ports:** Frontend `3006`, Backend `8095`

## Features

P0/P1: site audit · keyword research & clustering · content optimizer · content
brief · rank tracking · backlink analysis · competitor gap · Core Web Vitals ·
AI Copilot. **P2:** AI content writer · meta tags & schema · video SEO · local
SEO (GBP/citations/NAP/reviews) · white-label reports · predictive forecasting.
**Hardening:** auth · billing · multi-tenant · observability · security · Helm.

## Quick Start

```bash
# Backend
cd backend
pip install -e ".[dev]"
alembic upgrade head          # apply DB migrations (DATABASE_URL -> dclaw_seo)
uvicorn app.main:app --reload --port 8095

# Frontend
cd frontend
npm install
npm run dev
```

## Docker

```bash
docker-compose up --build
```

## Demo (v1.0)

From a fresh clone, with Postgres running and `DATABASE_URL` pointing at `dclaw_seo`:

```bash
cd backend
pip install -e ".[dev]"
alembic upgrade head
PYTHONPATH=. python scripts/demo.py          # runs the full P0 flow in-process
PYTHONPATH=. python scripts/export_openapi.py # writes backend/openapi.json
```

The demo exercises every P0 feature (health, audit, keyword research, content
optimizer, rank tracking, AI copilot, dashboard stats). AI enrichment and live
SERP positions activate once you configure a provider in `backend/.env`
(`OLLAMA_*` / `OPENROUTER_*`); without one, real data + clear notes are returned.

## AI Copilot — bring your own model

Configure either provider in `backend/.env` (see `.env.example`):

- **Ollama (local):** `OLLAMA_URL`, `OLLAMA_MODEL`
- **OpenRouter (cloud):** `OPENROUTER_API_KEY`, `OPENROUTER_MODEL`
- `LLM_PROVIDER` = `auto` (local→cloud fallback) | `ollama` | `openrouter`

Keyword data uses **Google Suggest** (free, no key). A paid SEO-data provider
can be slotted in later for search volume / SERP positions.

## API Endpoints (selected)

All `/api/v1/*` feature routes require a JWT (`Authorization: Bearer …`); only
`/health`, `/metrics`, `/admin/health`, and `/api/v1/auth/*` are public.

| Method | Path | Description |
|--------|------|-------------|
| GET | `/health` · `/admin/health` · `/metrics` | Liveness · readiness · Prometheus |
| POST | `/api/v1/auth/register` · `/login` · GET `/me` | Self-contained JWT auth |
| GET | `/api/v1/seo/stats` | Dashboard aggregates |
| POST | `/api/v1/seo/audit` · `/keywords` · `/content/optimize` · `/rankings/track` | Core SEO |
| POST | `/api/v1/seo/content/write` · `/meta` · `/video` | AI content suite |
| POST | `/api/v1/local/businesses/...` | Local SEO (GBP, citations, NAP, reviews) |
| POST | `/api/v1/reports/preview` · `/pdf` · `/csv` · `/forecast` | Reports & forecasting |
| GET/PUT | `/api/v1/org/...` · `/billing/...` | Org, cost ledger/cap, billing |
| POST | `/api/v1/ai/copilot` | AI SEO copilot — prioritized actions |

## Contributors

- [Deepro Mallick (@deepro713)](https://github.com/deepro713)

## License

MIT — DClaw Stack
