"""Scripted v1.0 demo flow across all P0 features.

Runs the app in-process (httpx ASGITransport) and exercises every P0 endpoint,
printing a concise report. Requires the database to be migrated
(`alembic upgrade head`). Network-dependent steps (keyword research, copilot)
degrade gracefully and are reported, not fatal.

Usage:
    DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:5432/dclaw_seo \
        python scripts/demo.py
"""

import asyncio

from httpx import ASGITransport, AsyncClient

from app.main import app


def line(ok: bool, name: str, detail: str) -> None:
    print(f"  {'✓' if ok else '✗'} {name:<22} {detail}")


async def main() -> None:
    print("DClaw SEO — v1.0 demo flow\n")
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://demo") as c:
        r = await c.get("/health")
        line(r.status_code == 200, "health", r.json())

        r = await c.post("/api/v1/seo/audit", json={"url": "https://example.com"})
        b = r.json()
        line(r.status_code == 200, "site audit", f"score={b['score']} issues={len(b['issues'])}")

        r = await c.post("/api/v1/seo/keywords", json={"seed": "espresso machine"})
        b = r.json()
        line(
            r.status_code == 200,
            "keyword research",
            f"{len(b.get('suggestions', []))} suggestions, llm_enriched={b.get('llm_enriched')}",
        )

        r = await c.post(
            "/api/v1/seo/content/optimize",
            json={"target_keyword": "espresso", "content": "Espresso is strong coffee. " * 20},
        )
        b = r.json()
        line(r.status_code == 200, "content optimizer", f"score={b['score']} checks={len(b['suggestions'])}")

        r = await c.post(
            "/api/v1/seo/rankings/track",
            json={"keyword": "espresso machine", "url": "https://example.com", "position": 7},
        )
        b = r.json()
        line(r.status_code == 200, "rank tracking", f"history={len(b['history'])} source={b['serp_source']}")

        r = await c.post("/api/v1/ai/copilot", json={"url": "https://example.com"})
        b = r.json()
        line(
            r.status_code == 200,
            "ai copilot",
            f"{len(b.get('actions', []))} actions, llm_enriched={b.get('llm_enriched')}"
            if r.status_code == 200
            else f"status={r.status_code} (network?)",
        )

        r = await c.get("/api/v1/seo/stats")
        b = r.json()
        line(
            r.status_code == 200,
            "dashboard stats",
            f"audits={b['audits']} keywords={b['keywords']} ranks={b['rank_observations']}",
        )
    print("\nDemo flow complete.")


if __name__ == "__main__":
    asyncio.run(main())
