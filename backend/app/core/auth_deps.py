"""Auth dependencies.

``get_current_user`` validates the Bearer JWT, loads the user, and installs a
request-scoped :class:`Meter` so any LLM call made while serving the request is
metered against the user's organization. Feature label is derived from the path.
"""

from __future__ import annotations

from fastapi import Depends, HTTPException, Request, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.context import Meter, set_meter
from app.core.database import get_db
from app.core.security import decode_access_token
from app.models.tenancy import User

_bearer = HTTPBearer(auto_error=False)


def _feature_from_path(path: str) -> str:
    marker = "/api/v1/"
    return path.split(marker, 1)[1] if marker in path else "ai"


async def get_current_user(
    request: Request,
    creds: HTTPAuthorizationCredentials | None = Depends(_bearer),
    db: AsyncSession = Depends(get_db),
) -> User:
    if creds is None or not creds.credentials:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")
    payload = decode_access_token(creds.credentials)
    if payload is None or "sub" not in payload:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, detail="Invalid or expired token")
    user = await db.get(User, int(payload["sub"]))
    if user is None:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, detail="User no longer exists")
    set_meter(Meter(org_id=user.org_id, db=db, feature=_feature_from_path(request.url.path)))
    return user
