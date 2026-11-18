from uuid import UUID, uuid4

from src.academic.application.dto.student_summary import (
    StudentDuplicateCandidate,
    StudentSummary,
)
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
        registration_number: str | None = None,
    ) -> StudentSummary:
        clean_first_name = first_name.strip()
        clean_last_name = last_name.strip()
        if not clean_first_name:
            raise ValueError("Le prenom de l'eleve est obligatoire.")
        if not clean_last_name:
            raise ValueError("Le nom de l'eleve est obligatoire.")

        clean_reg = _optional_text(registration_number)
        if clean_reg:
            existing = self._repository.find_by_registration_number(tenant_id, clean_reg)
            if existing is not None:
                raise ValueError("Le matricule scolaire est deja attribue dans cet etablissement.")

        candidates = self._repository.find_potential_duplicates(
            tenant_id, clean_first_name, clean_last_name
        )
        student = Student(
            id=uuid4(),
            tenant_id=tenant_id,
            first_name=clean_first_name,
            last_name=clean_last_name,
            email=_optional_text(email),
            phone=_optional_text(phone),
            registration_number=clean_reg,
        )
        self._repository.save(student)
        return StudentSummary(
            id=student.id,
            first_name=student.first_name,
            last_name=student.last_name,
            email=student.email,
            active=student.active,
            registration_number=student.registration_number,
            potential_duplicates=tuple(
                StudentDuplicateCandidate(
                    id=candidate.id,
                    first_name=candidate.first_name,
                    last_name=candidate.last_name,
                    registration_number=candidate.registration_number,
                )
                for candidate in candidates
            ),
        )
