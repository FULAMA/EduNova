from uuid import UUID

from src.academic.application.dto.student_summary import StudentSummary
from src.academic.application.interfaces.student_repository import StudentRepository
from src.academic.domain.entities.student import Student


def _optional_text(value: str | None) -> str | None:
    if value is None:
        return None
    stripped = value.strip()
    return stripped or None


class UpdateStudent:
    def __init__(self, repository: StudentRepository):
        self._repository = repository

    def execute(
        self,
        tenant_id: UUID,
        student_id: UUID,
        first_name: str,
        last_name: str,
        email: str | None = None,
        phone: str | None = None,
        active: bool = True,
        registration_number: str | None = None,
    ) -> StudentSummary:
        existing = self._repository.get_by_id_and_tenant(student_id, tenant_id)
        if existing is None:
            raise LookupError("Eleve introuvable.")

        clean_reg = _optional_text(registration_number)
        if clean_reg:
            by_reg = self._repository.find_by_registration_number(tenant_id, clean_reg)
            if by_reg is not None and by_reg.id != student_id:
                raise ValueError("Le matricule scolaire est deja attribue dans cet etablissement.")

        student = Student(
            id=student_id,
            tenant_id=tenant_id,
            first_name=first_name.strip(),
            last_name=last_name.strip(),
            email=_optional_text(email),
            phone=_optional_text(phone),
            registration_number=clean_reg,
            active=active,
        )
        self._repository.update(student)
        return StudentSummary(
            id=student.id,
            first_name=student.first_name,
            last_name=student.last_name,
            email=student.email,
            active=student.active,
            registration_number=student.registration_number,
        )
