from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status

from src.academic.application.dto.student_summary import StudentSummary
from src.academic.application.use_cases.create_student import CreateStudent
from src.academic.application.use_cases.get_student import GetStudent
from src.academic.application.use_cases.list_students import ListStudents
from src.presentation.api.dependencies import (
    get_create_student_use_case,
    get_get_student_use_case,
    get_list_students_use_case,
)
from src.presentation.api.dependencies.auth import (
    get_tenant_context,
    require_finance_manager_role,
    require_finance_role,
)
from src.presentation.api.schemas.student import (
    StudentCreateRequest,
    StudentSummaryResponse,
)
from src.shared.application.context.tenant_context import TenantContext


router = APIRouter(prefix="/students", tags=["Students"])


def _student_response(student: StudentSummary) -> StudentSummaryResponse:
    return StudentSummaryResponse(
        id=student.id,
        first_name=student.first_name,
        last_name=student.last_name,
        email=student.email,
        active=student.active,
    )


@router.get(
    "",
    response_model=list[StudentSummaryResponse],
    dependencies=[Depends(require_finance_role())],
)
def list_students(
    use_case: ListStudents = Depends(get_list_students_use_case),
    tenant_context: TenantContext = Depends(get_tenant_context),
) -> list[StudentSummaryResponse]:
    return [
        _student_response(student)
        for student in use_case.execute(tenant_context.tenant_id)
    ]


@router.post(
    "",
    response_model=StudentSummaryResponse,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_finance_manager_role())],
)
def create_student(
    data: StudentCreateRequest,
    use_case: CreateStudent = Depends(get_create_student_use_case),
    tenant_context: TenantContext = Depends(get_tenant_context),
) -> StudentSummaryResponse:
    try:
        return _student_response(
            use_case.execute(
                tenant_context.tenant_id,
                data.first_name,
                data.last_name,
                data.email,
                data.phone,
            )
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc


@router.get(
    "/{student_id}",
    response_model=StudentSummaryResponse,
    dependencies=[Depends(require_finance_role())],
)
def get_student(
    student_id: UUID,
    use_case: GetStudent = Depends(get_get_student_use_case),
    tenant_context: TenantContext = Depends(get_tenant_context),
) -> StudentSummaryResponse:
    student = use_case.execute(student_id, tenant_context.tenant_id)
    if student is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Eleve introuvable.",
        )

    return _student_response(student)
