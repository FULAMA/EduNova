from datetime import datetime, timezone
from uuid import UUID, uuid4

from src.academic.application.interfaces.deliberation_repository import DeliberationRepository
from src.academic.application.interfaces.report_card_repository import ReportCardRepository
from src.academic.application.interfaces.student_academic_record_repository import StudentAcademicRecordRepository
from src.academic.domain.entities.deliberation import Deliberation
from src.academic.domain.entities.student_academic_record import AcademicRecordStatus
from src.academic.domain.entities.report_card import ReportCard


class PrepareReportCard:
    def __init__(
        self,
        records: StudentAcademicRecordRepository,
        deliberations: DeliberationRepository,
        report_cards: ReportCardRepository,
    ) -> None:
        self._records = records
        self._deliberations = deliberations
        self._report_cards = report_cards

    def execute(
        self, tenant_id: UUID, student_id: UUID, academic_period_id: UUID,
        deliberation_id: UUID, actor_id: UUID,
    ) -> ReportCard:
        report_card = self.build(tenant_id, student_id, academic_period_id, deliberation_id, actor_id)
        return self._report_cards.save(report_card)

    def build(
        self, tenant_id: UUID, student_id: UUID, academic_period_id: UUID,
        deliberation_id: UUID, actor_id: UUID, report_version: int = 1,
        previous_report_card_id: UUID | None = None,
    ) -> ReportCard:
        record = self._records.find_by_student_and_period(student_id, academic_period_id, tenant_id)
        if record is None:
            raise ValueError("Aucun dossier academique trouve pour cette periode.")
        if record.status is not AcademicRecordStatus.VALIDATED:
            raise ValueError("Le bulletin exige un dossier academique valide.")
        deliberation = self._deliberations.find_by_id(deliberation_id, tenant_id)
        self._check_deliberation(deliberation, record, student_id, academic_period_id)
        snapshot = self._snapshot(record, deliberation)
        return ReportCard(
            tenant_id=tenant_id,
            student_id=student_id,
            academic_period_id=academic_period_id,
            deliberation_id=deliberation_id,
            deliberation_version=deliberation.version,
            record_version=record.version,
            report_version=report_version,
            snapshot=snapshot,
            snapshot_hash=ReportCard.calculate_snapshot_hash(snapshot),
            id=uuid4(),
            created_at=datetime.now(timezone.utc),
            previous_report_card_id=previous_report_card_id,
        )

    @staticmethod
    def _check_deliberation(deliberation, record, student_id, period_id) -> None:
        if deliberation is None:
            raise ValueError("Deliberation introuvable.")
        if deliberation.status != "VALIDATED":
            raise ValueError("La deliberation source doit etre validee.")
        if deliberation.student_id != student_id or deliberation.academic_period_id != period_id:
            raise ValueError("La deliberation ne correspond pas au dossier.")
        if deliberation.record_version != record.version:
            raise ValueError("La deliberation ne correspond plus a la version du dossier.")

    @staticmethod
    def _snapshot(record, deliberation: Deliberation) -> dict:
        return {
            "student_id": str(record.student_id),
            "academic_period_id": str(record.academic_period_id),
            "record_version": record.version,
            "general_average": record.general_average,
            "failed_subjects": record.failed_subjects,
            "credits_obtained": record.credits_obtained,
            "total_credits": record.total_credits,
            "subject_results": [
                {
                    "subject_id": str(result.subject_id),
                    "average": result.average,
                    "coefficient": result.coefficient,
                }
                for result in record.subject_results
            ],
            "deliberation": {
                "id": str(deliberation.id),
                "version": deliberation.version,
                "decision": deliberation.decision.value,
                "average": deliberation.average,
                "failed_subjects": deliberation.failed_subjects,
            },
        }
