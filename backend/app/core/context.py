"""Request-scoped LLM metering context.

The auth dependency sets the current request's :class:`Meter` (org + DB session
+ feature) into a ``ContextVar``. ``LLMService.complete`` reads it to enforce the
org's cost cap and record token usage — so every AI feature is metered without
each call site having to thread the org through. ContextVars are isolated per
asyncio task, so concurrent requests don't bleed into each other.
"""

from __future__ import annotations

from contextvars import ContextVar
from dataclasses import dataclass
from typing import TYPE_CHECKING, Optional

if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncSession


@dataclass
class Meter:
    org_id: int
    db: "AsyncSession"
    feature: str = "ai"


_current_meter: ContextVar[Optional[Meter]] = ContextVar("current_meter", default=None)


def set_meter(meter: Meter | None) -> None:
    _current_meter.set(meter)


def get_meter() -> Meter | None:
    return _current_meter.get()
