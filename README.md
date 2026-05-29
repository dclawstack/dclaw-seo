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

## API Endpoints

| Method | Path | Description |
|--------|------|-------------|
| GET | `/health` | Health check |
| POST | `/api/v1/seo/audit` | Site audit |
| POST | `/api/v1/seo/keywords` | Keyword research |
| POST | `/api/v1/seo/content/optimize` | Content optimization |
| POST | `/api/v1/seo/rankings/track` | Rankings tracking |

## Contributors

- [Deepro Mallick (@deepro713)](https://github.com/deepro713)

## License

MIT — DClaw Stack
