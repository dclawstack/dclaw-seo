# DClaw SEO — Demo

A scripted, end-to-end walkthrough of the platform. Use it to record the demo
video or to run a live demo.

## Automated smoke demo

The fastest way to see everything work against a running stack:

```bash
docker compose -f docker-compose.standalone.yml up -d --build
cd backend && DATABASE_URL=postgresql+asyncpg://dclaw:dclaw@localhost:5432/dclaw_seo \
    PYTHONPATH=. python scripts/demo.py
```

It registers an org, then exercises health → audit → keywords → content
optimizer → rank tracking → AI copilot → dashboard stats → the per-org LLM cost
ledger, printing a ✓/✗ line for each.

## Live walkthrough (≈5 min) — recommended video script

1. **Sign up** (`/login` → Create account) — org + owner created, land on the
   Dashboard.
2. **Audit** a site (`/audit`) — show the deep crawl + AI-prioritized issues.
3. **Keywords** (`/keywords`) — expand a seed, show intent + clusters.
4. **AI Writer** (`/writer`) — generate a draft; point out the originality score
   and fact-check notes.
5. **Meta & Schema** (`/meta`) — paste a URL, show generated tags + JSON-LD.
6. **Local SEO** (`/local`) — add a business + a mismatched citation, run the
   NAP scan, log a 2★ review and show the AI-drafted reply.
7. **Forecast** (`/forecast`) — after a few tracked checks, show the projection.
8. **Reports** (`/reports`) — download a branded PDF with the AI executive
   summary; create a schedule.
9. **Account** (`/account`) — show the LLM cost ledger filling up as you used AI,
   and set a monthly cost cap.
10. **Billing** (`/billing`) — switch to Starter, show the live invoice preview.
11. **Copilot** — open the floating Copilot on any page, give it a URL, show the
    prioritized next actions.
12. **Ops** — `curl /admin/health` and `/metrics`; open the Grafana dashboard
    (`observability/`).

## Recording the video

The video itself is a manual capture (e.g. Loom / QuickTime) following the
script above — it cannot be produced from CI. Save the recording link in
`docs/releases/` and the marketing site when available.
