from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.auth_deps import get_current_user
from app.core.database import get_db
from app.core.security import create_access_token
from app.models.tenancy import Organization, User
from app.schemas.auth import (
    LoginRequest,
    MeResponse,
    OrgOut,
    RegisterRequest,
    TokenResponse,
    UserOut,
)
from app.services import auth as svc

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
async def register(payload: RegisterRequest, db: AsyncSession = Depends(get_db)) -> TokenResponse:
    """Create an organization + owner account and return an access token."""
    try:
        user = await svc.register(db, payload)
    except svc.AuthError as exc:
        raise HTTPException(status.HTTP_409_CONFLICT, detail=str(exc)) from exc
    return TokenResponse(access_token=create_access_token(user_id=user.id, org_id=user.org_id))


@router.post("/login", response_model=TokenResponse)
async def login(payload: LoginRequest, db: AsyncSession = Depends(get_db)) -> TokenResponse:
    try:
        user = await svc.authenticate(db, payload)
    except svc.AuthError as exc:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, detail=str(exc)) from exc
    return TokenResponse(access_token=create_access_token(user_id=user.id, org_id=user.org_id))


@router.get("/me", response_model=MeResponse)
async def me(
    user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)
) -> MeResponse:
    org = await db.get(Organization, user.org_id)
    return MeResponse(user=UserOut.model_validate(user), org=OrgOut.model_validate(org))
