from dataclasses import dataclass
from uuid import UUID

from src.academic.application.dto.student_summary import StudentSummary
from src.academic.application.interfaces.student_repository import StudentRepository
from src.identity.application.interfaces.parent_student_link_repository import (
    ParentStudentLinkRepository,
)
from src.identity.domain.entities.parent_student_link import RelationshipType


@dataclass(frozen=True)
class ParentChildSummary:
    student: StudentSummary
    relationship_type: RelationshipType


class ListParentChildren:
    def __init__(
        self,
        link_repository: ParentStudentLinkRepository,
        student_repository: StudentRepository,
    ):
        self._link_repository = link_repository
        self._student_repository = student_repository

    def execute(self, tenant_id: UUID, parent_user_id: UUID) -> tuple[ParentChildSummary, ...]:
        links = self._link_repository.list_by_parent(tenant_id, parent_user_id)
        results: list[ParentChildSummary] = []
        for link in links:
            student = self._student_repository.get_by_id_and_tenant(link.student_id, tenant_id)
            if student is not None and student.active:
                results.append(
                    ParentChildSummary(
                        student=student,
                        relationship_type=link.relationship_type,
                    )
                )
        return tuple(results)
