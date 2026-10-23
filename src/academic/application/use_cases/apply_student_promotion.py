from uuid import UUID, uuid4
from datetime import datetime, timezone

from src.academic.application.interfaces.academic_class_repository import AcademicClassRepository
from src.academic.application.interfaces.academic_year_repository import AcademicYearRepository
from src.academic.application.interfaces.deliberation_repository import DeliberationRepository
from src.academic.application.interfaces.student_assignment_repository import StudentAssignmentRepository
from src.academic.application.interfaces.student_academic_record_repository import StudentAcademicRecordRepository
from src.academic.domain.entities.academic_year import AcademicYearStatus
from src.academic.domain.entities.deliberation import DeliberationDecision
from src.academic.domain.entities.student_assignment import StudentAssignment, StudentAssignmentStatus


class ApplyStudentPromotion:
    def __init__(
        self,
        assignments: StudentAssignmentRepository,
        deliberations: DeliberationRepository,
        years: AcademicYearRepository,
        classes: AcademicClassRepository,
        records: StudentAcademicRecordRepository | None = None,
    ):
        self._assignments = assignments
        self._deliberations = deliberations
        self._years = years
        self._classes = classes
        self._records = records

    def execute(self, tenant_id: UUID, source_assignment_id: UUID, deliberation_id: UUID, target_year_id: UUID, target_class_id: UUID, actor_id: UUID) -> StudentAssignment:
        source = self._assignments.find_by_id(source_assignment_id, tenant_id)
        if source is None:
            raise ValueError("Affectation source introuvable.")
        if source.status is not StudentAssignmentStatus.ACTIVE:
            raise ValueError("Seule une affectation active peut etre promue.")
        if getattr(source, "academic_year_id", None) == target_year_id:
            raise ValueError("L annee cible doit etre differente de l annee source.")
        deliberation = self._deliberations.find_by_id(deliberation_id, tenant_id)
        if deliberation is None or deliberation.student_id != source.student_id:
            raise ValueError("Deliberation introuvable ou incompatible.")
        if deliberation.status != "VALIDATED" or deliberation.decision is not DeliberationDecision.ADMITTED:
            raise ValueError("La deliberation ne permet pas ce passage.")
        if self._records is not None:
            record = self._records.find_by_student_and_period(
                source.student_id,
                deliberation.academic_period_id,
                tenant_id,
            )
            if record is None or record.version != deliberation.record_version:
                raise ValueError(
                    "Le dossier academique a change depuis la deliberation."
                )
        year = self._years.find_by_id(target_year_id, tenant_id)
        if year is None or year.status is not AcademicYearStatus.ACTIVE:
            raise ValueError("L annee cible doit etre active.")
        if self._classes.find_by_id(target_class_id, tenant_id) is None:
            raise ValueError("Classe cible introuvable dans cet etablissement.")
        existing = [item for item in self._assignments.list_by_student(source.student_id, tenant_id) if item.academic_year_id == target_year_id and item.status is StudentAssignmentStatus.ACTIVE]
        if existing:
            return existing[0]
        now = datetime.now(timezone.utc)
        assignment = StudentAssignment(uuid4(), tenant_id, source.student_id, target_year_id, target_class_id, None, StudentAssignmentStatus.DRAFT, actor_id, now, now)
        save_active = getattr(self._assignments, "save_active", None)
        if save_active is not None:
            return save_active(assignment.activate())
        self._assignments.save(assignment)
        return self._assignments.update(assignment.activate(), StudentAssignmentStatus.DRAFT.value)
