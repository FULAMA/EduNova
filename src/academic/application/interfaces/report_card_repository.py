from abc import ABC, abstractmethod
from uuid import UUID

from src.academic.domain.entities.report_card import ReportCard


class ReportCardRepository(ABC):
    @abstractmethod
    def save(self, report_card: ReportCard) -> ReportCard:
        raise NotImplementedError

    @abstractmethod
    def find_by_id(self, report_card_id: UUID, tenant_id: UUID) -> ReportCard | None:
        raise NotImplementedError

    @abstractmethod
    def list_published_for_student(self, tenant_id: UUID, student_id: UUID) -> tuple[ReportCard, ...]:
        raise NotImplementedError

    @abstractmethod
    def find_published_for_student(
        self, report_card_id: UUID, tenant_id: UUID, student_id: UUID
    ) -> ReportCard | None:
        raise NotImplementedError

    @abstractmethod
    def publish(self, report_card_id: UUID, tenant_id: UUID, actor_id: UUID, published_at) -> ReportCard:
        raise NotImplementedError

    @abstractmethod
    def replace_with_correction(self, previous: ReportCard, replacement: ReportCard) -> ReportCard:
        raise NotImplementedError
