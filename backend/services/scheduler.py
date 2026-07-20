from abc import ABC, abstractmethod
from core.logging import logger


class ImportScheduler(ABC):
    @abstractmethod
    def schedule(self, workspace: str, cron_expr: str) -> str: ...

    @abstractmethod
    def cancel(self, schedule_id: str): ...

    @abstractmethod
    def list_schedules(self) -> list[dict]: ...


class ManualImportScheduler(ImportScheduler):
    def schedule(self, workspace: str, cron_expr: str) -> str:
        logger.info(f"Scheduling not implemented — would schedule {workspace} @ {cron_expr}")
        return ""

    def cancel(self, schedule_id: str):
        logger.info(f"Schedule cancellation not implemented: {schedule_id}")

    def list_schedules(self) -> list[dict]:
        return []
