from app.models.keyword import Keyword
from app.repositories.base import BaseRepository


class KeywordRepository(BaseRepository[Keyword]):
    model = Keyword
