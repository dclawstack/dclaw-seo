"""Pluggable SERP position provider.

No reliable free, keyless SERP API exists, so the default provider is
``NullSERPProvider`` (returns no position). Real positions come from either a
manually observed value supplied on the request, or a paid provider
(SerpApi / DataForSEO) slotted in here later — without changing callers.
"""

from __future__ import annotations

from typing import Protocol


class SERPProvider(Protocol):
    name: str

    async def position(self, keyword: str, url: str) -> int | None: ...


class NullSERPProvider:
    """No SERP source configured — positions must be supplied manually."""

    name = "none"

    async def position(self, keyword: str, url: str) -> int | None:  # noqa: ARG002
        return None


# Default. TODO(P1): swap for a real provider (SerpApi/DataForSEO) via config.
serp_provider: SERPProvider = NullSERPProvider()
