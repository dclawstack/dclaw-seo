# Build Log

Human-readable mirror of development progress. One row per completed task (Neon `plan.tasks` is the source of truth; this is the vault view). Append newest at the bottom.

| Date | Task | Title | Phase | Issue | PR | Outcome |
|------|------|-------|-------|-------|----|---------|
| 2026-05-29 | — | Planning setup (plan + Neon + Project #6 + 34 issues) | — | — | — | Tracking stood up; dev not yet started |
| 2026-05-29 | F0.1 | Resolve ports & fix config drift | Phase 0 | #1 | — | Canonical 8095/3006 propagated to AGENTS/REVISED-PRD; `.env.example` DB `dclaw_crm`→`dclaw_seo`; `docker-compose config` passes; crm collision deferred |
| 2026-05-29 | F0.2 | Introduce repository layer | Phase 0 | #2 | — | `BaseRepository` + 4 per-model repos; service writes via repos (no `db.add`); consolidated duplicate `Base` to `app.models.base`; `get_db` moved to `core.database` |
| 2026-05-29 | F0.3 | Initialize Alembic + initial migration | Phase 0 | #3 | — | Async `env.py` wired to settings + `Base.metadata`; migration `db8a8e5e228a` (4 tables); clean DB→`upgrade head` verified + reversible; CI runs migrations |
| 2026-05-29 | F0.4 | Replace mock SEO data with real persistence | Phase 0 | #4 | — | Removed all `random.*`; deterministic sha256 estimates flagged `TODO(P1)`; responses read persisted JSON; rank history grows from real DB rows |
| 2026-05-29 | F0.5 | Test baseline + CI green | Phase 0 | #5 | — | Fixed conftest import + health path; added `test_seo.py` (4 endpoints + validation); 7 passed, 90% coverage (target ≥70%) |
| 2026-05-29 | F0.6 | structlog logging + config hygiene | Phase 0 | #6 | — | structlog setup (console/JSON); structured startup/shutdown logs; `SettingsConfigDict` (deprecation gone); structlog added to requirements |
| 2026-05-29 | F0.7 | Docs accuracy pass | Phase 0 | #7 | — | Reconciled docs/reference (ports 8095/3006, API URL, health version, SEO endpoints); marked Alembic + DPanel manifest resolved in vault |
| 2026-05-29 | F0.8 | Adopt DKube purple design system | Phase 0 | #33 | — | Ported `brand.css` `--dk-*` + Poppins (next/font) verbatim from dclaw-marketing; tailwind bound to tokens; restyled all components/pages off emerald→purple; favicons/manifest + `design/` kit; `npm run build` green (8 routes, no warnings); supersedes #10B981 |

## Related

- [[Home]]
- [[Dev Plan]] — phases, mirrors, and the per-task loop
- [[Roadmap]] — feature-level P0/P1/P2 view
