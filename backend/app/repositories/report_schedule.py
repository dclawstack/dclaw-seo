from app.models.report_schedule import ReportSchedule
from app.repositories.base import BaseRepository


class ReportScheduleRepository(BaseRepository[ReportSchedule]):
    model = ReportSchedule
