# Open Issues

> Snapshot at 2026-05-29 from `REVISED-PRD.md` gap analysis + cross-doc review. Re-run `gh issue list` for the authoritative live state.

## Gaps (from REVISED-PRD v2.3)

| # | Gap | Severity | Fix |
|---|-----|----------|-----|
| 1 | Missing Alembic migrations | 🟡 | `alembic init` + initial autogenerate migration |
| 2 | Partial implementation | 🟡 | Expand backend services + frontend pages per P0 roadmap |

## Doc inconsistencies (worth resolving)

- **Port mismatch.** `README.md` (3006/8095), `AGENTS.md` (3008/8008), and `REVISED-PRD.md` (3098/18168 TBD) disagree. A canonical port must be assigned and propagated. See [[Architecture]].
- **Port collision.** README's `8095 / 3006` is the same pair the registry assigns to `dclaw-crm`.
- **Missing DPanel manifest.** `frontend/public/dclaw-manifest.json` not yet present (scaffold checklist item).

## Related

- [[Architecture]]
- [[Roadmap]]
