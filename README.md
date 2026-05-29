# DClaw SEO

> **Rank higher with AI**

AI SEO Agent for the DClaw Stack. Audit sites, research keywords, optimize content, and track rankings.

## Tech Stack

- **Frontend:** Next.js 14+, Tailwind CSS, shadcn/ui
- **Backend:** FastAPI, Pydantic v2, SQLAlchemy 2.0, asyncpg
- **Database:** PostgreSQL 16
- **Dev Ports:** Frontend `3006`, Backend `8095`

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

## API Endpoints

| Method | Path | Description |
|--------|------|-------------|
| GET | `/health` | Health check |
| GET | `/api/v1/seo/stats` | Dashboard aggregates |
| POST | `/api/v1/seo/audit` | Site audit |
| POST | `/api/v1/seo/keywords` | Keyword research (Google Suggest + LLM) |
| POST | `/api/v1/seo/content/optimize` | Content optimization + scoring |
| POST | `/api/v1/seo/rankings/track` | Rank tracking + drop alerts |
| POST | `/api/v1/ai/copilot` | AI SEO copilot — prioritized actions |

## Contributors

- [Deepro Mallick (@deepro713)](https://github.com/deepro713)

## License

MIT — DClaw Stack
