from datetime import datetime, timezone

from src.academic.application.dto.add_subject_result_request import (
    AddSubjectResultRequest,
)
from src.academic.application.dto.add_subject_result_response import (
    AddSubjectResultResponse,
)
from src.academic.application.interfaces.student_academic_record_repository import (
    StudentAcademicRecordRepository,
)
from src.academic.application.interfaces.academic_period_repository import AcademicPeriodRepository
from src.academic.application.interfaces.class_subject_repository import ClassSubjectRepository
from src.academic.application.interfaces.student_assignment_repository import StudentAssignmentRepository
from src.academic.application.interfaces.subject_repository import SubjectRepository
from src.academic.domain.entities.student_assignment import StudentAssignmentStatus
from src.academic.domain.policies.academic_policy import AcademicPolicy
from src.academic.domain.events.subject_result_added import SubjectResultAdded
from src.academic.domain.value_objects.subject_result import SubjectResult
from src.shared.application.events.event_dispatcher import EventDispatcher


class AddSubjectResult:
    def __init__(
        self,
        repository: StudentAcademicRecordRepository,
        event_dispatcher: EventDispatcher | None = None,
        *,
        assignments: StudentAssignmentRepository,
        periods: AcademicPeriodRepository,
        class_subjects: ClassSubjectRepository,
        subjects: SubjectRepository,
        policy: AcademicPolicy | None = None,
    ):
        self._repository = repository
        self._event_dispatcher = event_dispatcher
        self._assignments = assignments
        self._periods = periods
        self._class_subjects = class_subjects
        self._subjects = subjects
        self._policy = policy or AcademicPolicy()

    def execute(
        self,
        request: AddSubjectResultRequest,
    ) -> AddSubjectResultResponse:

        record = self._repository.find_by_student_and_period(
            request.student_id,
            request.academic_period_id,
            request.tenant_id,
        )

        if record is None:
            raise ValueError(
                "Aucun dossier académique trouvé pour "
                "cet étudiant et cette période."
            )

        coefficient = self._resolve_coefficient(request)
        subject_result = SubjectResult(
            subject_id=request.subject_id,
            average=request.average,
            coefficient=coefficient,
        )

        updated_record = record.with_subject_result(
            subject_result,
            policy=self._policy,
        )

        self._repository.save(
            updated_record,
            expected_version=record.version,
            operation="SUBJECT_RESULT_ADDED",
        )

        if self._event_dispatcher is not None:
            event = SubjectResultAdded.create(
                occurred_at=datetime.now(timezone.utc),
                tenant_id=updated_record.tenant_id,
                student_id=updated_record.student_id,
                academic_period_id=updated_record.academic_period_id,
                subject_id=subject_result.subject_id,
                average=subject_result.average,
                coefficient=subject_result.coefficient,
                record_version=updated_record.version,
            )

            self._event_dispatcher.dispatch(event)

        return AddSubjectResultResponse(
            subject_id=subject_result.subject_id,
            average=subject_result.average,
            coefficient=subject_result.coefficient,
        )

    def _resolve_coefficient(self, request: AddSubjectResultRequest) -> float:
        period = self._periods.find_by_id(request.academic_period_id, request.tenant_id)
        if period is None or period.academic_year_id is None:
            raise ValueError("Cette periode historique n'est pas eligible a une nouvelle saisie.")

        assignment = next((
            item for item in self._assignments.list_by_student(request.student_id, request.tenant_id)
            if item.status is StudentAssignmentStatus.ACTIVE
            and item.academic_year_id == period.academic_year_id
        ), None)
        if assignment is None:
            raise ValueError("Aucune affectation active ne correspond a cette periode.")

        class_subject = next((
            item for item in self._class_subjects.find_by_class_and_option(
                assignment.academic_class_id, assignment.academic_option_id, request.tenant_id
            )
            if item.active and item.subject_id == request.subject_id
        ), None)
        subject = self._subjects.find_by_id(request.subject_id, request.tenant_id)
        if class_subject is None or subject is None or not subject.active:
            raise ValueError("Cette matiere n'est pas active et affectee a la classe de l'eleve.")
        return class_subject.coefficient
