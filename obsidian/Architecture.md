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
| Auth | **Self-contained JWT** (bcrypt + PyJWT; `core/security.py`) — chosen over Logto for a keyless, fully-testable flow |
| Multi-tenancy | org→project hierarchy; per-org LLM **cost ledger + cap** (metered via a `Meter` ContextVar in `services/llm.py`) |
| Billing | free/starter/pro, per-seat + metered invoicing; Stripe optional (httpx, no SDK) |
| LLM | Ollama (local, default) · OpenRouter (cloud fallback) |
| Observability | Prometheus `/metrics` + `MetricsMiddleware` · `/admin/health` · Grafana (`observability/`) |
| Container | Docker Compose (dev) · Helm chart (prod, `helm/dclaw-seo`) |
| CI | GitHub Actions (CI + build + deploy + Claude Code Action) |

## Directory layout

```
backend/
  app/
    api/      main.py · routes/health.py (+/metrics,/admin/health) · v1/ (seo, ai, auth, tenancy, billing, local_seo, reports, settings)
    core/     config.py · database.py · security.py (JWT/bcrypt) · auth_deps.py · context.py (Meter) · observability.py · security_headers.py
    models/   base.py + domain + tenancy + billing + local_seo + report_schedule
    repositories/  CRUD layer (all DB access goes here)
    schemas/  Pydantic v2
    services/ business logic / AI (llm.py = single metered call site · metering.py · billing.py · forecast.py · reports.py · …)
  alembic/    migrations (async env.py; 11 revisions through v2.0)
  scripts/    demo.py · export_openapi.py · build_user_guide_pdf.py
  tests/      conftest.py (seeds a tenant + auth override) + pytest-asyncio (92 tests)
frontend/
  src/app/         App Router pages (incl. login, account, billing, writer, meta, video, local, forecast, reports)
  src/components/ui/  pre-built UI components
  src/lib/         api.ts (typed fetch + JWT/token handling) · utils.ts (cn())
helm/dclaw-seo/  Helm chart (CNPG, ingress, per-env values)
observability/   Prometheus config + Grafana provisioning/dashboards
landing/         standalone marketing site (Vercel)
```

## Ports ✅ (canonical, reconciled in F0.1)

Canonical pair = **backend `8095` / frontend `3006`** (README values), now propagated to `AGENTS.md`, `REVISED-PRD.md`, and `docker-compose.yml`. DB name is `dclaw_seo` (fixed `.env.example` which pointed at `dclaw_crm`).

| Source | Frontend | Backend |
|--------|----------|---------|
| `README.md` / `AGENTS.md` / `REVISED-PRD.md` / compose | 3006 | 8095 |

> ⚠️ `8095 / 3006` still collides with `dclaw-crm` in the shared port registry — re-assignment is a platform-level decision, **deferred per owner** (documented in `AGENTS.md`).

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
