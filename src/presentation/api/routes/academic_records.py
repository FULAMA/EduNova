from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, ConfigDict, Field

from src.academic.application.dto.add_subject_result_request import (
    AddSubjectResultRequest,
)
from src.academic.application.dto.analyze_student_academic_record_request import (
    AnalyzeStudentAcademicRecordRequest,
)
from src.academic.application.use_cases.add_subject_result import AddSubjectResult
from src.academic.application.use_cases.analyze_student_academic_record import (
    AnalyzeStudentAcademicRecord,
)
from src.presentation.api.dependencies import (
    get_add_subject_result_use_case,
    get_analyze_student_academic_record_use_case,
    get_list_student_academic_periods_use_case,
)
from src.academic.application.use_cases.list_student_academic_periods import (
    ListStudentAcademicPeriods,
)
from src.presentation.api.dependencies.auth import get_current_user, require_role
from src.identity.application.dto.authenticated_user import AuthenticatedUser
from src.presentation.api.schemas.academic_record import (
    AcademicRecordResponse,
    SubjectResultResponse,
    EligibleAcademicPeriodResponse,
    EligibleSubjectResponse,
    DeliberationResponse,
    AcademicRecordHistoryResponse,
)
from src.presentation.api.schemas.add_subject_result import (
    AddSubjectResultResponse,
)
from src.presentation.api.schemas.add_subject_result_request import (
    AddSubjectResultRequestSchema,
)
from src.shared.application.context.tenant_context import TenantContext
from src.presentation.api.dependencies.auth import get_tenant_context
from src.academic.application.dto.create_academic_record_request import (
    CreateAcademicRecordRequest,
)
from src.academic.application.use_cases.create_academic_record import (
    CreateAcademicRecord,
)
from src.academic.application.dto.validate_academic_record_request import (
    ValidateAcademicRecordRequest,
)
from src.academic.application.dto.correct_academic_record_request import (
    CorrectAcademicRecordRequest,
)
from src.academic.application.use_cases.validate_academic_record import (
    ValidateAcademicRecord,
)
from src.academic.application.use_cases.correct_academic_record import (
    CorrectAcademicRecord,
)
from src.academic.application.exceptions import (
    AcademicRecordConcurrencyError,
    AcademicRecordHistoryReadError,
)
from src.presentation.api.dependencies import (
    get_create_academic_record_use_case,
    get_validate_academic_record_use_case,
    get_correct_academic_record_use_case,
    get_list_eligible_student_periods_use_case,
    get_list_eligible_student_subjects_use_case,
    get_prepare_deliberation_use_case,
    get_validate_deliberation_use_case,
    get_student_academic_record_repository,
)
from src.presentation.api.schemas.create_academic_record_request import (
    CreateAcademicRecordRequestSchema,
)
from src.presentation.api.schemas.create_academic_record import (
    CreateAcademicRecordResponse,
)
from src.academic.application.use_cases.list_eligible_student_periods import ListEligibleStudentPeriods
from src.academic.application.use_cases.list_eligible_student_subjects import ListEligibleStudentSubjects
from src.academic.application.use_cases.prepare_deliberation import PrepareDeliberation
from src.academic.application.use_cases.validate_deliberation import ValidateDeliberation
from src.academic.application.exceptions import DeliberationConcurrencyError
from src.academic.application.interfaces.student_academic_record_repository import StudentAcademicRecordRepository


router = APIRouter(
    prefix="/academic-records",
    tags=["Academic Records"],
)


@router.get(
    "/students/{student_id}/periods",
    response_model=list[dict[str, UUID | str | None]],
    dependencies=[Depends(require_role("ADMIN"))],
)
def list_student_academic_periods(
    student_id: UUID,
    use_case: ListStudentAcademicPeriods = Depends(
        get_list_student_academic_periods_use_case
    ),
    tenant_context: TenantContext = Depends(get_tenant_context),
):
    return use_case.execute_detailed(student_id, tenant_context.tenant_id)


@router.get("/students/{student_id}/available-periods", response_model=list[EligibleAcademicPeriodResponse], dependencies=[Depends(require_role("ADMIN"))])
def list_eligible_student_periods(
    student_id: UUID,
    use_case: ListEligibleStudentPeriods = Depends(get_list_eligible_student_periods_use_case),
    tenant_context: TenantContext = Depends(get_tenant_context),
):
    return use_case.execute(student_id, tenant_context.tenant_id)


@router.get("/students/{student_id}/periods/{academic_period_id}/subjects", response_model=list[EligibleSubjectResponse], dependencies=[Depends(require_role("ADMIN"))])
def list_eligible_student_subjects(
    student_id: UUID,
    academic_period_id: UUID,
    use_case: ListEligibleStudentSubjects = Depends(get_list_eligible_student_subjects_use_case),
    tenant_context: TenantContext = Depends(get_tenant_context),
):
    try:
        return use_case.execute(student_id, academic_period_id, tenant_context.tenant_id)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@router.get(
    "/{student_id}/{academic_period_id}",
    response_model=AcademicRecordResponse,
    response_model_exclude_none=True,
    dependencies=[Depends(require_role("ADMIN"))],
)
def get_academic_record(
    student_id: UUID,
    academic_period_id: UUID,
    use_case: AnalyzeStudentAcademicRecord = Depends(
        get_analyze_student_academic_record_use_case
    ),
    tenant_context: TenantContext = Depends(get_tenant_context),
) -> AcademicRecordResponse:

    request = AnalyzeStudentAcademicRecordRequest(
        tenant_id=tenant_context.tenant_id,
        student_id=student_id,
        academic_period_id=academic_period_id,
    )

    try:
        response = use_case.execute(request)
    except ValueError as exc:
        raise HTTPException(
            status_code=404,
            detail=str(exc),
        ) from exc

    subject_results = [
        SubjectResultResponse(
            subject_id=result.subject_id,
            subject_name=(response.subject_names or {}).get(result.subject_id),
            average=result.average,
            coefficient=result.coefficient,
        )
        for result in response.subject_results
    ]

    return AcademicRecordResponse(
        student_id=response.student_id,
        academic_period_id=response.academic_period_id,
        general_average=response.general_average,
        failed_subjects=response.failed_subjects,
        credits_obtained=response.credits_obtained,
        total_credits=response.total_credits,
        subject_results=subject_results,
        status=response.status,
        version=response.version,
        academic_period_name=response.academic_period_name,
    )


@router.get(
    "/{student_id}/{academic_period_id}/deliberation",
    response_model=DeliberationResponse,
    dependencies=[Depends(require_role("ADMIN"))],
)
def prepare_deliberation(
    student_id: UUID,
    academic_period_id: UUID,
    use_case: PrepareDeliberation = Depends(get_prepare_deliberation_use_case),
    tenant_context: TenantContext = Depends(get_tenant_context),
    current_user: AuthenticatedUser = Depends(get_current_user),
) -> DeliberationResponse:
    try:
        result = use_case.execute(
            tenant_context.tenant_id, student_id, academic_period_id, current_user.id
        )
    except ValueError as exc:
        status_code = (
            status.HTTP_404_NOT_FOUND
            if str(exc).startswith("Aucun dossier academique trouve")
            else status.HTTP_400_BAD_REQUEST
        )
        raise HTTPException(status_code=status_code, detail=str(exc)) from exc
    return DeliberationResponse(
        student_id=result.student_id,
        academic_period_id=academic_period_id,
        record_version=result.record_version or 0,
        average=result.average,
        failed_subjects=result.failed_subjects,
        decision=result.decision.value,
        deliberation_id=result.id,
        deliberation_status=result.status,
        deliberation_version=result.version,
    )


class ValidateDeliberationRequest(BaseModel):
    expected_version: int = Field(ge=1)


@router.post(
    "/deliberations/{deliberation_id}/validate",
    response_model=DeliberationResponse,
    dependencies=[Depends(require_role("ADMIN"))],
)
def validate_deliberation(
    deliberation_id: UUID,
    data: ValidateDeliberationRequest,
    use_case: ValidateDeliberation = Depends(get_validate_deliberation_use_case),
    tenant_context: TenantContext = Depends(get_tenant_context),
    current_user: AuthenticatedUser = Depends(get_current_user),
) -> DeliberationResponse:
    try:
        result = use_case.execute(
            tenant_context.tenant_id,
            deliberation_id,
            data.expected_version,
            current_user.id,
        )
    except DeliberationConcurrencyError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc
    except ValueError as exc:
        status_code = (
            status.HTTP_404_NOT_FOUND
            if str(exc) == "Délibération introuvable."
            else status.HTTP_400_BAD_REQUEST
        )
        raise HTTPException(status_code=status_code, detail=str(exc)) from exc
    validated_period_id = result.academic_period_id
    if validated_period_id is None:
        raise HTTPException(status_code=500, detail="La période de délibération est manquante.")
    return DeliberationResponse(
        student_id=result.student_id,
        academic_period_id=validated_period_id,
        record_version=result.record_version or 0,
        average=result.average,
        failed_subjects=result.failed_subjects,
        decision=result.decision.value,
        deliberation_id=result.id,
        deliberation_status=result.status,
        deliberation_version=result.version,
    )


class AcademicRecordMutationRequestSchema(BaseModel):
    model_config = ConfigDict(allow_inf_nan=False)
    expected_version: int


class CorrectAcademicRecordRequestSchema(AcademicRecordMutationRequestSchema):
    reason: str = Field(min_length=1, max_length=500)
    general_average: float = Field(ge=0, le=20)
    failed_subjects: int = Field(ge=0)
    credits_obtained: float = Field(ge=0)


def _mutation_error(exc: Exception) -> HTTPException:
    if isinstance(exc, AcademicRecordConcurrencyError):
        return HTTPException(status_code=409, detail="Le dossier a changé. Rechargez la page.")
    if str(exc) == "Aucun dossier académique trouvé.":
        return HTTPException(status_code=404, detail=str(exc))
    return HTTPException(status_code=400, detail=str(exc))


@router.post(
    "/{student_id}/{academic_period_id}/validate",
    response_model=AcademicRecordResponse,
    dependencies=[Depends(require_role("ADMIN"))],
)
def validate_academic_record(
    student_id: UUID,
    academic_period_id: UUID,
    data: AcademicRecordMutationRequestSchema,
    use_case: ValidateAcademicRecord = Depends(get_validate_academic_record_use_case),
    analyze: AnalyzeStudentAcademicRecord = Depends(get_analyze_student_academic_record_use_case),
    tenant_context: TenantContext = Depends(get_tenant_context),
) -> AcademicRecordResponse:
    try:
        use_case.execute(ValidateAcademicRecordRequest(
            tenant_id=tenant_context.tenant_id,
            student_id=student_id,
            academic_period_id=academic_period_id,
            expected_version=data.expected_version,
        ))
    except (ValueError, AcademicRecordConcurrencyError) as exc:
        raise _mutation_error(exc) from exc
    return get_academic_record(student_id, academic_period_id, analyze, tenant_context)


@router.post(
    "/{student_id}/{academic_period_id}/correct",
    response_model=AcademicRecordResponse,
    dependencies=[Depends(require_role("ADMIN"))],
)
def correct_academic_record(
    student_id: UUID,
    academic_period_id: UUID,
    data: CorrectAcademicRecordRequestSchema,
    use_case: CorrectAcademicRecord = Depends(get_correct_academic_record_use_case),
    analyze: AnalyzeStudentAcademicRecord = Depends(get_analyze_student_academic_record_use_case),
    tenant_context: TenantContext = Depends(get_tenant_context),
    current_user: AuthenticatedUser = Depends(get_current_user),
) -> AcademicRecordResponse:
    try:
        use_case.execute(CorrectAcademicRecordRequest(
            tenant_id=tenant_context.tenant_id,
            student_id=student_id,
            academic_period_id=academic_period_id,
            expected_version=data.expected_version,
            actor_id=current_user.id,
            reason=data.reason,
            general_average=data.general_average,
            failed_subjects=data.failed_subjects,
            credits_obtained=data.credits_obtained,
        ))
    except (ValueError, AcademicRecordConcurrencyError) as exc:
        raise _mutation_error(exc) from exc
    return get_academic_record(student_id, academic_period_id, analyze, tenant_context)


@router.get(
    "/{student_id}/{academic_period_id}/history",
    response_model=list[AcademicRecordHistoryResponse],
    dependencies=[Depends(require_role("ADMIN"))],
)
def list_academic_record_history(
    student_id: UUID,
    academic_period_id: UUID,
    repository: StudentAcademicRecordRepository = Depends(
        get_student_academic_record_repository
    ),
    tenant_context: TenantContext = Depends(get_tenant_context),
):
    record = repository.find_by_student_and_period(
        student_id,
        academic_period_id,
        tenant_context.tenant_id,
    )
    if record is None:
        raise HTTPException(status_code=404, detail="Aucun dossier académique trouvé.")

    try:
        return list(repository.list_history(
            student_id, academic_period_id, tenant_context.tenant_id
        ))
    except AcademicRecordHistoryReadError as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="L'historique du dossier est temporairement indisponible.",
        ) from exc


@router.post(
    "/{student_id}/{academic_period_id}/subjects",
    response_model=AddSubjectResultResponse,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_role("ADMIN"))],
)
def add_subject_result(
    student_id: UUID,
    academic_period_id: UUID,
    data: AddSubjectResultRequestSchema,
    use_case: AddSubjectResult = Depends(
        get_add_subject_result_use_case
    ),
    tenant_context: TenantContext = Depends(get_tenant_context),
) -> AddSubjectResultResponse:

    request = AddSubjectResultRequest(
        tenant_id=tenant_context.tenant_id,
        student_id=student_id,
        academic_period_id=academic_period_id,
        subject_id=data.subject_id,
        average=data.average,
    )

    try:
        result = use_case.execute(request)
    except AcademicRecordConcurrencyError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Le dossier a changé. Rechargez la page.",
        ) from exc
    except ValueError as exc:
        raise HTTPException(
            status_code=404,
            detail=str(exc),
        ) from exc

    return AddSubjectResultResponse(
        subject_id=result.subject_id,
        average=result.average,
        coefficient=result.coefficient,
    )
@router.post(
    "",
    response_model=CreateAcademicRecordResponse,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_role("ADMIN"))],
)
def create_academic_record(
    data: CreateAcademicRecordRequestSchema,
    use_case: CreateAcademicRecord = Depends(
        get_create_academic_record_use_case
    ),
    tenant_context: TenantContext = Depends(get_tenant_context),
) -> CreateAcademicRecordResponse:

    request = CreateAcademicRecordRequest(
        tenant_id=tenant_context.tenant_id,
        student_id=data.student_id,
        academic_period_id=data.academic_period_id,
        total_credits=data.total_credits,
    )

    try:
        record = use_case.execute(request)
    except ValueError as exc:
        if str(exc) == "Academic record already exists":
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=str(exc),
            ) from exc

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc

    return CreateAcademicRecordResponse(
        student_id=record.student_id,
        academic_period_id=record.academic_period_id,
        general_average=record.general_average,
        failed_subjects=record.failed_subjects,
        credits_obtained=record.credits_obtained,
        total_credits=record.total_credits,
    )
