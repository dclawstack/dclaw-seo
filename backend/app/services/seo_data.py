"""Free, keyless SEO data sources.

The default keyword-data source is **Google Suggest** (autocomplete) — real
data, no API key, no subscription. Providers implement ``KeywordDataProvider``
so a paid source (DataForSEO / SerpApi / Ahrefs) can be slotted in later via
config without touching callers.
"""

from __future__ import annotations

import json
from typing import Protocol

import httpx

from app.core.logging import get_logger

logger = get_logger(__name__)

GOOGLE_SUGGEST_URL = "https://suggestqueries.google.com/complete/search"


class KeywordDataProvider(Protocol):
    async def expand(self, seed: str, target: int = 50) -> list[str]: ...


class ProviderUnavailable(RuntimeError):
    """Raised when the external data source cannot be reached."""


class GoogleSuggestProvider:
    """Real keyword expansion via Google autocomplete (free, keyless)."""

    name = "google_suggest"

    async def _suggest(self, client: httpx.AsyncClient, query: str) -> list[str]:
        resp = await client.get(GOOGLE_SUGGEST_URL, params={"client": "firefox", "q": query})
        resp.raise_for_status()
        # Response is a JSON array: [query, [suggestions...], ...]
        data = json.loads(resp.text)
        return data[1] if len(data) > 1 and isinstance(data[1], list) else []

    async def expand(self, seed: str, target: int = 50) -> list[str]:
        seed = seed.strip()
        results: list[str] = []
        seen: set[str] = {seed.lower()}
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                level1 = await self._suggest(client, seed)
                for s in level1:
                    s = s.strip()
                    if s and s.lower() not in seen:
                        seen.add(s.lower())
                        results.append(s)
                # Second level: expand each first-level term until we hit target.
                for kw in level1:
                    if len(results) >= target:
                        break
                    for s in await self._suggest(client, kw):
                        s = s.strip()
                        if s and s.lower() not in seen:
                            seen.add(s.lower())
                            results.append(s)
                        if len(results) >= target:
                            break
        except httpx.HTTPError as exc:
            raise ProviderUnavailable(f"Google Suggest unavailable: {exc}") from exc
        return results[:target]


# Default provider. Swap here (or via future config) for a paid source.
keyword_provider: KeywordDataProvider = GoogleSuggestProvider()
