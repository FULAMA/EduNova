from uuid import UUID

from src.academic.application.dto.teacher_assignment_view import TeacherAssignmentView
from src.academic.application.interfaces.academic_class_repository import AcademicClassRepository
from src.academic.application.interfaces.academic_year_repository import AcademicYearRepository
from src.academic.application.interfaces.subject_repository import SubjectRepository
from src.academic.application.interfaces.teacher_assignment_repository import TeacherAssignmentRepository
from src.academic.domain.entities.teacher_assignment import TeacherAssignment


class ListTeacherAssignments:
    def __init__(
        self,
        teacher_assignment_repository: TeacherAssignmentRepository,
        academic_classes: AcademicClassRepository,
        subjects: SubjectRepository,
        academic_years: AcademicYearRepository,
    ):
        self._repository = teacher_assignment_repository
        self._academic_classes = academic_classes
        self._subjects = subjects
        self._academic_years = academic_years

    def execute_for_teacher(
        self, tenant_id: UUID, teacher_user_id: UUID, academic_year_id: UUID | None = None,
    ) -> tuple[TeacherAssignmentView, ...]:
        return self._with_labels(
            self._repository.list_by_teacher(tenant_id, teacher_user_id, academic_year_id)
        )

    def execute_for_class(
        self, tenant_id: UUID, academic_class_id: UUID, academic_year_id: UUID | None = None,
    ) -> tuple[TeacherAssignmentView, ...]:
        return self._with_labels(
            self._repository.list_by_class(tenant_id, academic_class_id, academic_year_id)
        )

    def _with_labels(
        self, assignments: tuple[TeacherAssignment, ...]
    ) -> tuple[TeacherAssignmentView, ...]:
        views: list[TeacherAssignmentView] = []
        for assignment in assignments:
            academic_class = self._academic_classes.find_by_id(
                assignment.academic_class_id, assignment.tenant_id
            )
            subject = self._subjects.find_by_id(
                assignment.subject_id, assignment.tenant_id
            )
            academic_year = self._academic_years.find_by_id(
                assignment.academic_year_id, assignment.tenant_id
            )
            views.append(TeacherAssignmentView(
                tenant_id=assignment.tenant_id,
                teacher_user_id=assignment.teacher_user_id,
                academic_class_id=assignment.academic_class_id,
                academic_class_label=academic_class.name if academic_class else None,
                subject_id=assignment.subject_id,
                subject_label=subject.name if subject else None,
                academic_year_id=assignment.academic_year_id,
                academic_year_label=academic_year.label if academic_year else None,
                assigned_by=assignment.assigned_by,
                assigned_at=assignment.assigned_at,
            ))
        return tuple(views)
