from uuid import UUID

from src.academic.application.interfaces.report_card_repository import ReportCardRepository


class ListStudentReportCards:
    def __init__(self, repository: ReportCardRepository) -> None:
        self._repository = repository

    def execute(self, tenant_id: UUID, student_id: UUID):
        return self._repository.list_published_for_student(tenant_id, student_id)
