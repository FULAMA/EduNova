from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status

from src.application.dto.add_subject_result_request import (
    AddSubjectResultRequest,
)
from src.application.dto.analyze_student_academic_record_request import (
    AnalyzeStudentAcademicRecordRequest,
)
from src.application.use_cases.add_subject_result import AddSubjectResult
from src.application.use_cases.analyze_student_academic_record import (
    AnalyzeStudentAcademicRecord,
)
from src.domain.value_objects import role as roles
from src.presentation.api.dependencies import (
    get_add_subject_result_use_case,
    get_analyze_student_academic_record_use_case,
)
from src.presentation.api.dependencies.auth import require_role
from src.presentation.api.schemas.academic_record import (
    AcademicRecordResponse,
    SubjectResultResponse,
)
from src.presentation.api.schemas.add_subject_result import (
    AddSubjectResultResponse,
)
from src.presentation.api.schemas.add_subject_result_request import (
    AddSubjectResultRequestSchema,
)


router = APIRouter(
    prefix="/academic-records",
    tags=["Academic Records"],
    dependencies=[
        Depends(require_role(roles.ADMIN, roles.TEACHER)),
    ],
)


@router.get(
    "/{student_id}/{academic_period_id}",
    response_model=AcademicRecordResponse,
)
def get_academic_record(
    student_id: UUID,
    academic_period_id: UUID,
    use_case: AnalyzeStudentAcademicRecord = Depends(get_analyze_student_academic_record_use_case),
) -> AcademicRecordResponse:

    request = AnalyzeStudentAcademicRecordRequest(
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
    )


@router.post(
    "/{student_id}/{academic_period_id}/subjects",
    response_model=AddSubjectResultResponse,
    status_code=status.HTTP_201_CREATED,
)
def add_subject_result(
    student_id: UUID,
    academic_period_id: UUID,
    data: AddSubjectResultRequestSchema,
    use_case: AddSubjectResult = Depends(
        get_add_subject_result_use_case
    ),
) -> AddSubjectResultResponse:

    request = AddSubjectResultRequest(
        student_id=student_id,
        academic_period_id=academic_period_id,
        subject_id=data.subject_id,
        average=data.average,
        coefficient=data.coefficient,
    )

    try:
        result = use_case.execute(request)
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
from src.application.dto.create_academic_record_request import (
    CreateAcademicRecordRequest,
)
from src.application.use_cases.create_academic_record import (
    CreateAcademicRecord,
)
from src.presentation.api.dependencies import (
    get_create_academic_record_use_case,
)
from src.presentation.api.schemas.create_academic_record_request import (
    CreateAcademicRecordRequestSchema,
)
from src.presentation.api.schemas.create_academic_record import (
    CreateAcademicRecordResponse,
)

@router.post(
    "",
    response_model=CreateAcademicRecordResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_academic_record(
    data: CreateAcademicRecordRequestSchema,
    use_case: CreateAcademicRecord = Depends(
        get_create_academic_record_use_case
    ),
) -> CreateAcademicRecordResponse:

    request = CreateAcademicRecordRequest(
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
