from uuid import UUID

from src.academic.application.interfaces.report_card_repository import ReportCardRepository


class GetStudentReportCard:
    def __init__(self, repository: ReportCardRepository) -> None:
        self._repository = repository

    def execute(self, report_card_id: UUID, tenant_id: UUID, student_id: UUID):
        result = self._repository.find_published_for_student(report_card_id, tenant_id, student_id)
        if result is None:
            raise ValueError("Bulletin introuvable.")
        return result
