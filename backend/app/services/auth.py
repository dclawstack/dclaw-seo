"""Self-contained auth: register an org+owner, authenticate, issue JWTs."""

from __future__ import annotations

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import hash_password, verify_password
from app.models.tenancy import Organization, User
from app.repositories.tenancy import OrganizationRepository, UserRepository
from app.schemas.auth import LoginRequest, RegisterRequest


class AuthError(Exception):
    """Raised on duplicate email or bad credentials."""


async def register(db: AsyncSession, payload: RegisterRequest) -> User:
    users = UserRepository(db)
    if await users.get_by_email(payload.email.lower()):
        raise AuthError("An account with that email already exists.")
    org = await OrganizationRepository(db).create(Organization(name=payload.org_name))
    user = User(
        org_id=org.id,
        email=payload.email.lower(),
        hashed_password=hash_password(payload.password),
        role="owner",
    )
    return await users.create(user)


async def authenticate(db: AsyncSession, payload: LoginRequest) -> User:
    user = await UserRepository(db).get_by_email(payload.email.lower())
    if user is None or not verify_password(payload.password, user.hashed_password):
        raise AuthError("Invalid email or password.")
    return user
