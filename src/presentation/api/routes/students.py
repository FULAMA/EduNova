from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status

from src.academic.application.use_cases.get_student import GetStudent
from src.academic.application.use_cases.list_students import ListStudents
from src.presentation.api.dependencies import (
    get_get_student_use_case,
    get_list_students_use_case,
)
from src.presentation.api.dependencies.auth import get_tenant_context, require_role
from src.presentation.api.schemas.student import StudentSummaryResponse
from src.shared.application.context.tenant_context import TenantContext


router = APIRouter(prefix="/students", tags=["Students"])


@router.get(
    "",
    response_model=list[StudentSummaryResponse],
    dependencies=[Depends(require_role("ADMIN"))],
)
def list_students(
    use_case: ListStudents = Depends(get_list_students_use_case),
    tenant_context: TenantContext = Depends(get_tenant_context),
) -> list[StudentSummaryResponse]:
    students = use_case.execute(tenant_context.tenant_id)
    return [
        StudentSummaryResponse(
            id=student.id,
            first_name=student.first_name,
            last_name=student.last_name,
            email=student.email,
            active=student.active,
        )
        for student in students
    ]


@router.get(
    "/{student_id}",
    response_model=StudentSummaryResponse,
    dependencies=[Depends(require_role("ADMIN"))],
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

    return StudentSummaryResponse(
        id=student.id,
        first_name=student.first_name,
        last_name=student.last_name,
        email=student.email,
        active=student.active,
    )
