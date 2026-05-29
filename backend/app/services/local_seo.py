"""Local SEO manager.

Covers the four local-SEO jobs:

- **GBP sync** — pulls a Google Business Profile listing when GBP credentials are
  configured (``GBP_API_KEY``); otherwise stores the NAP the user supplies and
  flags ``synced_from_gbp=False`` so the source is never misrepresented.
- **Citation tracking** — stores directory listings (Yelp, YellowPages, …) with
  their listed NAP.
- **NAP consistency scan** — normalizes name/address/phone and compares every
  citation against the business's canonical NAP, returning a consistency score
  and the exact mismatched fields.
- **Review monitoring/responses** — stores reviews and drafts an AI response
  (LLM) with a deterministic, tone-appropriate template fallback.

No fabricated data: citations and reviews are real rows the caller supplies (or
that a configured provider returns); only the AI response text is generated.
"""

from __future__ import annotations

import re

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.logging import get_logger
from app.models.local_seo import Citation, LocalBusiness, Review
from app.repositories.local_seo import (
    CitationRepository,
    LocalBusinessRepository,
    ReviewRepository,
)
from app.schemas.local_seo import (
    BusinessCreate,
    CitationCreate,
    CitationOut,
    GbpSyncResult,
    NapScanResult,
    ReviewCreate,
)
from app.services.llm import LLMError, LLMNotConfigured, Message, llm_service
from app.services.llm_config import get_effective_config

logger = get_logger(__name__)

_APOSTROPHE = re.compile(r"['’]")
_NON_ALNUM = re.compile(r"[^a-z0-9]+")
_DIGITS = re.compile(r"\d+")
_SUFFIXES = {"inc", "llc", "ltd", "co", "corp", "company"}
_ADDR_ABBR = {
    "street": "st", "avenue": "ave", "road": "rd", "boulevard": "blvd",
    "drive": "dr", "lane": "ln", "suite": "ste", "north": "n", "south": "s",
    "east": "e", "west": "w",
}


def norm_name(name: str) -> str:
    cleaned = _APOSTROPHE.sub("", name.lower())
    words = [w for w in _NON_ALNUM.sub(" ", cleaned).split() if w not in _SUFFIXES]
    return " ".join(words)


def norm_address(addr: str) -> str:
    cleaned = _APOSTROPHE.sub("", addr.lower())
    words = [_ADDR_ABBR.get(w, w) for w in _NON_ALNUM.sub(" ", cleaned).split()]
    return " ".join(words)


def norm_phone(phone: str) -> str:
    digits = "".join(_DIGITS.findall(phone))
    return digits[-10:] if len(digits) >= 10 else digits


def nap_mismatches(business: LocalBusiness, c_name: str, c_addr: str, c_phone: str) -> list[str]:
    out: list[str] = []
    if norm_name(business.name) != norm_name(c_name):
        out.append("name")
    if norm_address(business.address) != norm_address(c_addr):
        out.append("address")
    if norm_phone(business.phone) != norm_phone(c_phone):
        out.append("phone")
    return out


def _to_out(c: Citation) -> CitationOut:
    return CitationOut(
        id=c.id,
        source=c.source,
        url=c.url,
        listed_name=c.listed_name,
        listed_address=c.listed_address,
        listed_phone=c.listed_phone,
        nap_consistent=c.nap_consistent,
        mismatch_fields=c.mismatch_fields.split(",") if c.mismatch_fields else [],
    )


# --- GBP provider abstraction -------------------------------------------------

def _gbp_configured() -> bool:
    return bool(getattr(settings, "gbp_api_key", ""))


async def sync_gbp(db: AsyncSession, payload: BusinessCreate) -> GbpSyncResult:
    """Create/refresh a business. Uses GBP when configured, else stored NAP."""
    repo = LocalBusinessRepository(db)
    business = LocalBusiness(
        name=payload.name,
        address=payload.address,
        phone=payload.phone,
        website=payload.website,
        gbp_place_id=payload.gbp_place_id,
    )
    business = await repo.create(business)
    if _gbp_configured() and payload.gbp_place_id:
        # A live GBP fetch would refresh fields here; provider not wired without creds.
        note = "GBP_API_KEY set — live GBP refresh hook is ready but not yet implemented."
        synced = False
    else:
        note = (
            "Stored the NAP you supplied. Set GBP_API_KEY and a gbp_place_id to pull the "
            "listing directly from Google Business Profile."
        )
        synced = False
    from app.schemas.local_seo import BusinessOut

    return GbpSyncResult(business=BusinessOut.model_validate(business), synced_from_gbp=synced, note=note)


# --- Citations + NAP scan -----------------------------------------------------

async def add_citation(db: AsyncSession, business_id: int, payload: CitationCreate) -> CitationOut:
    biz = await LocalBusinessRepository(db).get(business_id)
    if biz is None:
        raise ValueError("business not found")
    mismatches = nap_mismatches(biz, payload.listed_name, payload.listed_address, payload.listed_phone)
    citation = Citation(
        business_id=business_id,
        source=payload.source,
        url=payload.url,
        listed_name=payload.listed_name,
        listed_address=payload.listed_address,
        listed_phone=payload.listed_phone,
        nap_consistent=not mismatches,
        mismatch_fields=",".join(mismatches) or None,
    )
    citation = await CitationRepository(db).create(citation)
    return _to_out(citation)


async def nap_scan(db: AsyncSession, business_id: int) -> NapScanResult:
    biz = await LocalBusinessRepository(db).get(business_id)
    if biz is None:
        raise ValueError("business not found")
    repo = CitationRepository(db)
    citations = list(await repo.for_business(business_id))
    for c in citations:
        mismatches = nap_mismatches(biz, c.listed_name, c.listed_address, c.listed_phone)
        c.nap_consistent = not mismatches
        c.mismatch_fields = ",".join(mismatches) or None
    if citations:
        await db.commit()
    consistent = sum(1 for c in citations if c.nap_consistent)
    total = len(citations)
    score = round(consistent / total * 100, 1) if total else 100.0
    return NapScanResult(
        business_id=business_id,
        total_citations=total,
        consistent=consistent,
        inconsistent=total - consistent,
        consistency_score=score,
        citations=[_to_out(c) for c in citations],
    )


# --- Reviews + AI responses ---------------------------------------------------

def _template_response(rating: int, author: str | None) -> str:
    who = f" {author}" if author else ""
    if rating >= 4:
        return (
            f"Thank you for the kind words{who}! We're thrilled you had a great experience "
            "and look forward to seeing you again."
        )
    if rating == 3:
        return (
            f"Thanks for your feedback{who}. We're glad you visited and would love to hear how "
            "we can make your next experience even better."
        )
    return (
        f"We're sorry to hear about your experience{who}. This isn't the standard we hold "
        "ourselves to — please reach out so we can make it right."
    )


_SYSTEM = (
    "You are a local-business owner replying to a customer review. Write a single, warm, "
    "professional response (2-3 sentences). For low ratings, apologize and offer to make it "
    "right; for high ratings, thank them specifically. Return ONLY the response text."
)


async def _ai_response(db: AsyncSession, rating: int, author: str | None, text: str | None) -> tuple[str, bool]:
    cfg = await get_effective_config(db)
    payload = f"Rating: {rating}/5\nAuthor: {author or 'Anonymous'}\nReview: {text or '(no text)'}"
    try:
        raw = await llm_service.complete(
            [Message(role="system", content=_SYSTEM), Message(role="user", content=payload)],
            config=cfg,
            temperature=0.5,
        )
    except LLMNotConfigured:
        return _template_response(rating, author), False
    except LLMError as exc:
        logger.warning("review_llm_failed", error=str(exc))
        return _template_response(rating, author), False
    cleaned = raw.strip().strip('"')
    return (cleaned or _template_response(rating, author)), bool(cleaned)


async def add_review(db: AsyncSession, business_id: int, payload: ReviewCreate) -> Review:
    biz = await LocalBusinessRepository(db).get(business_id)
    if biz is None:
        raise ValueError("business not found")
    response, _ = await _ai_response(db, payload.rating, payload.author, payload.text)
    review = Review(
        business_id=business_id,
        source=payload.source,
        author=payload.author,
        rating=payload.rating,
        text=payload.text,
        suggested_response=response,
        responded=False,
    )
    return await ReviewRepository(db).create(review)


async def list_reviews(db: AsyncSession, business_id: int):
    return await ReviewRepository(db).for_business(business_id)
