from app.models.site_audit import SiteAudit
from app.repositories.base import BaseRepository


class SiteAuditRepository(BaseRepository[SiteAudit]):
    model = SiteAudit
