# Open Issues

> Updated 2026-05-30. **No open GitHub issues — all 34 closed (v2.0).** This note now tracks only residual deferred/known items. Re-run `gh issue list` for the authoritative live state.

## Gaps (from REVISED-PRD v2.3)

| # | Gap | Severity | Fix |
|---|-----|----------|-----|
| 1 | ~~Missing Alembic migrations~~ ✅ **Resolved (F0.3)** | — | `alembic init -t async` + initial migration `db8a8e5e228a` (11 migrations now) |
| 2 | ~~Partial implementation~~ ✅ **Resolved** | — | All P0/P1/P2 + hardening shipped end-to-end (v2.0) |
| 3 | ~~No auth / billing / multi-tenant / observability~~ ✅ **Resolved** | — | Phase 4: JWT auth, billing, org cost ledger, Prometheus/Grafana, Helm |

## Residual / deferred (not blockers)

- **Next.js advisories on the 14.x line.** Bumped `14.2.5 → 14.2.35` to clear the **critical** CVE; remaining `npm audit` items need a **Next 15 major upgrade** (App Router migration) — tracked, not done. See `SECURITY.md`.
- **`pytest` CVE-2025-71176.** Test-only dependency (not in the prod image); no runtime exposure.
- **Demo video.** `DEMO.md` has the full recording script; the video itself is a manual screen capture.
- **Neon `plan.subtasks` flags.** 61 granular sub-checkboxes show `done=false` — never maintained at any point in the project (task-level tracking was used instead); parent tasks all Done. Flip to match reality on request.

## Doc inconsistencies (worth resolving)

- ~~**Port mismatch.** `README.md` (3006/8095), `AGENTS.md` (3008/8008), and `REVISED-PRD.md` (3098/18168 TBD) disagree.~~ ✅ **Resolved in F0.1** — canonical `8095/3006` propagated everywhere. See [[Architecture]].
- **Port collision (deferred).** Canonical `8095 / 3006` is the same pair the registry assigns to `dclaw-crm`; re-assignment deferred per owner.
- ~~**Missing DPanel manifest.**~~ ✅ **Present** — `frontend/public/dclaw-manifest.json` exists (verified in F0.7; the REVISED-PRD gap note was stale).

## Related

- [[Architecture]]
- [[Roadmap]]
