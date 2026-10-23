from datetime import datetime, timezone
from uuid import UUID

from src.academic.application.interfaces.report_card_repository import ReportCardRepository
from src.academic.application.use_cases.prepare_report_card import PrepareReportCard


class CorrectReportCard:
    def __init__(self, report_cards: ReportCardRepository, preparer: PrepareReportCard) -> None:
        self._report_cards = report_cards
        self._preparer = preparer

    def execute(self, tenant_id: UUID, report_card_id: UUID, deliberation_id: UUID, actor_id: UUID):
        previous = self._report_cards.find_by_id(report_card_id, tenant_id)
        if previous is None:
            raise ValueError("Bulletin introuvable.")
        if previous.status.value != "ISSUED":
            raise ValueError("Seul un bulletin emis peut etre corrige.")
        replacement = self._preparer.build(
            tenant_id, previous.student_id, previous.academic_period_id,
            deliberation_id, actor_id, report_version=previous.report_version + 1,
            previous_report_card_id=previous.id,
        ).publish(actor_id, datetime.now(timezone.utc))
        return self._report_cards.replace_with_correction(previous, replacement)
