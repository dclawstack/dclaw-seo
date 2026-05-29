from app.models.content_optimization import ContentOptimization
from app.repositories.base import BaseRepository


class ContentOptimizationRepository(BaseRepository[ContentOptimization]):
    model = ContentOptimization
