from collections.abc import Sequence
from typing import Generic, TypeVar

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.base import Base

ModelT = TypeVar("ModelT", bound=Base)


class BaseRepository(Generic[ModelT]):
    """Generic async CRUD. All DB access for a model flows through its repository."""

    model: type[ModelT]

    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def create(self, obj: ModelT) -> ModelT:
        self.db.add(obj)
        await self.db.commit()
        await self.db.refresh(obj)
        return obj

    async def get(self, id_: int) -> ModelT | None:
        return await self.db.get(self.model, id_)

    async def list(self, limit: int = 100) -> Sequence[ModelT]:
        result = await self.db.execute(select(self.model).limit(limit))
        return result.scalars().all()
