from uuid import UUID, uuid4

from src.academic.application.dto.student_summary import StudentSummary
from src.academic.application.interfaces.student_repository import StudentRepository
from src.academic.domain.entities.student import Student


def _optional_text(value: str | None) -> str | None:
    if value is None:
        return None
    stripped = value.strip()
    return stripped or None


class CreateStudent:
    def __init__(self, repository: StudentRepository):
        self._repository = repository

    def execute(
        self,
        tenant_id: UUID,
        first_name: str,
        last_name: str,
        email: str | None = None,
        phone: str | None = None,
    ) -> StudentSummary:
        student = Student(
            id=uuid4(),
            tenant_id=tenant_id,
            first_name=first_name.strip(),
            last_name=last_name.strip(),
            email=_optional_text(email),
            phone=_optional_text(phone),
        )
        self._repository.save(student)
        return StudentSummary(
            id=student.id,
            first_name=student.first_name,
            last_name=student.last_name,
            email=student.email,
            active=student.active,
        )
