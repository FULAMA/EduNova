from datetime import datetime, timezone
from uuid import UUID

from src.academic.application.interfaces.deliberation_repository import DeliberationRepository
from src.academic.application.interfaces.report_card_repository import ReportCardRepository
from src.academic.application.interfaces.student_academic_record_repository import StudentAcademicRecordRepository
from src.academic.domain.entities.student_academic_record import AcademicRecordStatus


class PublishReportCard:
    def __init__(self, report_cards: ReportCardRepository, deliberations: DeliberationRepository, records: StudentAcademicRecordRepository) -> None:
        self._report_cards = report_cards
        self._deliberations = deliberations
        self._records = records

    def execute(self, tenant_id: UUID, report_card_id: UUID, actor_id: UUID):
        report_card = self._report_cards.find_by_id(report_card_id, tenant_id)
        if report_card is None:
            raise ValueError("Bulletin introuvable.")
        deliberation = self._deliberations.find_by_id(report_card.deliberation_id, tenant_id)
        if deliberation is None or deliberation.status != "VALIDATED" or deliberation.version != report_card.deliberation_version:
            raise ValueError("La deliberation source n est plus valide.")
        record = self._records.find_by_student_and_period(report_card.student_id, report_card.academic_period_id, tenant_id)
        if record is None or record.status is not AcademicRecordStatus.VALIDATED or record.version != report_card.record_version:
            raise ValueError("Le dossier source n est plus valide.")
        return self._report_cards.publish(report_card_id, tenant_id, actor_id, datetime.now(timezone.utc))
