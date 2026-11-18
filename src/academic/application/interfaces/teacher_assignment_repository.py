from abc import ABC, abstractmethod
from uuid import UUID

from src.academic.domain.entities.teacher_assignment import TeacherAssignment


class TeacherAssignmentRepository(ABC):
    @abstractmethod
    def save(self, assignment: TeacherAssignment) -> TeacherAssignment:
        """Enregistre une affectation d'enseignant. Lève ValueError si doublon."""
        ...

    @abstractmethod
    def list_by_teacher(
        self, tenant_id: UUID, teacher_user_id: UUID, academic_year_id: UUID | None = None,
    ) -> tuple[TeacherAssignment, ...]:
        """Retourne les affectations d'un enseignant au sein d'un établissement."""
        ...

    @abstractmethod
    def list_by_class(
        self, tenant_id: UUID, academic_class_id: UUID, academic_year_id: UUID | None = None,
    ) -> tuple[TeacherAssignment, ...]:
        """Retourne les affectations d'une classe au sein d'un établissement."""
        ...

    @abstractmethod
    def is_teacher_assigned(
        self,
        tenant_id: UUID,
        teacher_user_id: UUID,
        academic_class_id: UUID,
        subject_id: UUID,
        academic_year_id: UUID | None = None,
    ) -> bool:
        """Vérifie si l'enseignant est affecté à la classe et matière spécifiées."""
        ...
