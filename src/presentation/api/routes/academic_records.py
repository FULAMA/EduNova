from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException

from src.application.dto.analyze_student_academic_record_request import (
    AnalyzeStudentAcademicRecordRequest,
)
from src.application.use_cases.analyze_student_academic_record import (
    AnalyzeStudentAcademicRecord,
)
from src.infrastructure.persistence.database import SQLiteDatabase
from src.infrastructure.repositories.sqlite_student_academic_record_repository import (
    SQLiteStudentAcademicRecordRepository,
)
from src.presentation.api.dependencies import get_use_case
from src.presentation.api.schemas.academic_record import (
    AcademicRecordResponse,
    SubjectResultResponse,
)


router = APIRouter(
    prefix="/academic-records",
    tags=["Academic Records"],
)


@router.get(
    "/{student_id}/{academic_period_id}",
    response_model=AcademicRecordResponse,
)
def get_academic_record(
    student_id: UUID,
    academic_period_id: UUID,
    use_case: AnalyzeStudentAcademicRecord = Depends(get_use_case),
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

    return AcademicRecordResponse(
        student_id=response.student_id,
        academic_period_id=response.academic_period_id,
        general_average=response.general_average,
        failed_subjects=response.failed_subjects,
        credits_obtained=response.credits_obtained,
        total_credits=response.total_credits,
        subject_results=[
            SubjectResultResponse(
                subject_id=result.subject_id,
                average=result.average,
                coefficient=result.coefficient,
            )
            for result in response.subject_results
        ],
    )
