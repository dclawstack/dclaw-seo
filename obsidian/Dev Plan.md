# Dev Plan

The detailed phase-wise build plan lives in [`DEV-PLAN.md`](../DEV-PLAN.md) at the repo root. This note is the vault-side pointer.

## Where the plan lives (3 mirrors)

| Surface | Role |
|---------|------|
| `DEV-PLAN.md` (repo root) | Human-readable narrative with nested sublists |
| **Neon Postgres** — project `dclaw-seo` (`restless-queen-89786738`), schema `plan` | **Source of truth** for task status (`plan.phases`, `plan.tasks`, `plan.subtasks`, view `plan.board`) |
| [GitHub Project "DClaw SEO Project" (#6)](https://github.com/orgs/dclawstack/projects/6) | Mirror — 1 issue per task (#1–#34) with `Phase` / `Track` / `Priority` / `Status` fields |

> Update order during dev: set `plan.tasks.status` in Neon **first**, then reflect on the GitHub issue/Project field, then close the issue on completion. Reference the task key (e.g. `P0.1`) in branches/commits.

## Phases

- **Phase 0 — Foundation & Scaffold Hardening** (`v0.1.0`) — repos/alembic/no-mock/tests/config + **DKube purple design system** (#33). Issues #1–#7, #33.
- **Phase 1 — P0 Foundation Features** (`v1.0.0`) — LLM abstraction, AI SEO Copilot, Keyword Research, Content Optimizer, Rank Tracking, Dashboard, demo. Issues #8–#14.
- **Phase 2 — P1 Platform Features** (`v1.1–1.2`) — backlinks, deep audit, competitor gap, content briefs, CWV. Issues #15–#19.
- **Phase 3 — P2 Vertical / Scale** (`v1.3+`) — content writer, meta/schema, local SEO, video SEO, white-label, forecasting. Issues #20–#25.
- **Phase 4 — Hardening, Market-Ready & Launch** (`v2.0`) — auth, billing, multi-tenant, observability, security, K8s, docs/demo + **standalone landing site** (#34, Vercel-deferred). Issues #26–#32, #34.

> **Design & landing.** The app frontend and the landing site both use the unified **DKube purple `--dk-*`** design kit + Poppins, identical to `dclaw-marketing` (this supersedes the emerald `#10B981` in REVISED-PRD). The landing page is a separate Next.js site whose hero CTA links through to the app frontend.

## Querying status

```bash
psql "$NEON_URI" -c "select * from plan.board;"        # phase-ordered task board
psql "$NEON_URI" -c "select status, count(*) from plan.tasks group by status;"
```

## Related

- [[Home]]
- [[Roadmap]] — the feature-level P0/P1/P2 view this plan operationalises
- [[Architecture]]
- [[Open Issues]]
