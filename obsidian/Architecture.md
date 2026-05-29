# Architecture

## Stack (the "sacred" DClaw stack)

| Layer | Tech |
|-------|------|
| Frontend | Next.js 14+ App Router · Tailwind · pre-built UI components (no shadcn CLI) |
| Backend | FastAPI · SQLAlchemy 2.0 async (`Mapped`/`mapped_column`) · Pydantic v2 (`ConfigDict`) · asyncpg |
| DB | PostgreSQL 16 (CloudNativePG operator in K8s) |
| Vector | Qdrant / pgvector (only if RAG/semantic search) |
| Cache/Bus | Redis 7.x |
| Object storage | MinIO |
| Auth | Logto (JWT validation on protected routes) |
| LLM | Ollama (local) · OpenRouter + Kimi K2.5 (cloud fallback) |
| Container | Docker Compose (dev) · Helm chart (prod) |
| CI | GitHub Actions (incl. Claude Code Action) |

## Directory layout

```
backend/
  app/
    api/      main.py · routes/health.py · v1/  (app routers)
    core/     config.py · database.py (Base, engine, get_db)
    models/   base.py + domain models
    repositories/  CRUD layer (all DB access goes here)
    schemas/  Pydantic v2
    services/ business logic / AI
  alembic/    migrations  ⚠️ missing in seo (see Open Issues)
  tests/      conftest.py + pytest-asyncio
frontend/
  src/app/         App Router pages
  src/components/ui/  pre-built UI components
  src/lib/         api.ts (typed fetch) · utils.ts (cn())
```

## Ports ⚠️ (inconsistent across docs — see [[Open Issues]])

| Source | Frontend | Backend |
|--------|----------|---------|
| `README.md` quick-start | 3006 | 8095 |
| `AGENTS.md` app identity | 3008 | 8008 |
| `REVISED-PRD.md` (TBD) | 3098 | 18168 |

> The README's `3006 / 8095` is what the quick-start actually uses. Note that `8095 / 3006` collides with `dclaw-crm` in the shared port registry — a port needs to be formally assigned. DB name is `dclaw_seo`.

## Architecture lock — DO NOT CHANGE

- `DeclarativeBase` from `app.models.base` — **never** `declarative_base()`, **never** `MappedAsDataclass`.
- All DB access via the repository pattern + `Depends(get_db)`. No manual `AsyncSession`, no in-memory mock dicts.
- `pytest-asyncio==0.24.0` pinned (v1.3.0 breaks fixture scoping).
- Tests use `localhost:5432` (CI maps Postgres there).
- Frontend Dockerfile must declare `ARG NEXT_PUBLIC_API_URL` before build.
- Do **not** install the shadcn CLI or `@base-ui/react` (breaks Tailwind v3). Do **not** delete `.github/workflows/ci.yml`.

## Key anti-patterns

`default_factory=` in `mapped_column()` → use `default=` with a callable. Timezone-aware `datetime` in models → use naive UTC (`TIMESTAMP WITHOUT TIME ZONE`). `curl` in healthcheck on `python:*-slim` → use `python -c "import urllib.request; ..."`.

## Related

- [[Project Overview]]
- [[Glossary]]
- [[Open Issues]]
