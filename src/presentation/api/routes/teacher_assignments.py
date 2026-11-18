import sqlite3
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status

from src.academic.application.use_cases.assign_teacher import AssignTeacher
from src.academic.application.use_cases.list_teacher_assignments import ListTeacherAssignments
from src.identity.application.dto.authenticated_user import AuthenticatedUser
from src.presentation.api.dependencies import (
    get_assign_teacher_use_case,
    get_list_teacher_assignments_use_case,
)
from src.presentation.api.dependencies.auth import (
    get_current_user,
    get_tenant_context,
    require_role,
)
from src.presentation.api.schemas.teacher_assignment import (
    AssignTeacherInput,
    TeacherAssignmentResponse,
)
from src.shared.application.context.tenant_context import TenantContext


router = APIRouter(tags=["Teacher Assignments"])
_admin_or_direction = [Depends(require_role("ADMIN", "DIRECTION"))]
_teacher_only = [Depends(require_role("PROF", "TEACHER"))]


@router.post(
    "/teacher-assignments",
    response_model=TeacherAssignmentResponse,
    status_code=status.HTTP_201_CREATED,
    dependencies=_admin_or_direction,
)
def assign_teacher(
    data: AssignTeacherInput,
    use_case: AssignTeacher = Depends(get_assign_teacher_use_case),
    tenant: TenantContext = Depends(get_tenant_context),
    current_user: AuthenticatedUser = Depends(get_current_user),
) -> TeacherAssignmentResponse:
    try:
        assignment = use_case.execute(
            tenant_id=tenant.tenant_id,
            teacher_user_id=data.teacher_user_id,
            academic_class_id=data.academic_class_id,
            subject_id=data.subject_id,
            academic_year_id=data.academic_year_id,
            assigned_by=current_user.id,
        )
    except sqlite3.IntegrityError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="L'affectation ne peut pas etre enregistree (contrainte d'integrite).",
        ) from exc
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    return TeacherAssignmentResponse(**assignment.__dict__)


@router.get(
    "/teacher-assignments",
    response_model=list[TeacherAssignmentResponse],
    dependencies=_admin_or_direction,
)
def list_teacher_assignments(
    teacher_user_id: UUID | None = Query(None, description="Filtrer par enseignant"),
    academic_class_id: UUID | None = Query(None, description="Filtrer par classe"),
    academic_year_id: UUID | None = Query(None, description="Filtrer par annee scolaire"),
    use_case: ListTeacherAssignments = Depends(get_list_teacher_assignments_use_case),
    tenant: TenantContext = Depends(get_tenant_context),
) -> list[TeacherAssignmentResponse]:
    if teacher_user_id is not None:
        assignments = use_case.execute_for_teacher(tenant.tenant_id, teacher_user_id, academic_year_id)
    elif academic_class_id is not None:
        assignments = use_case.execute_for_class(tenant.tenant_id, academic_class_id, academic_year_id)
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Au moins teacher_user_id ou academic_class_id doit etre specifie.",
        )
    return [TeacherAssignmentResponse(**a.__dict__) for a in assignments]


@router.get(
    "/teacher/assignments",
    response_model=list[TeacherAssignmentResponse],
    dependencies=_teacher_only,
)
def list_my_teacher_assignments(
    academic_year_id: UUID | None = Query(None, description="Filtrer par annee scolaire"),
    use_case: ListTeacherAssignments = Depends(get_list_teacher_assignments_use_case),
    tenant: TenantContext = Depends(get_tenant_context),
    current_user: AuthenticatedUser = Depends(get_current_user),
) -> list[TeacherAssignmentResponse]:
    assignments = use_case.execute_for_teacher(tenant.tenant_id, current_user.id, academic_year_id)
    return [TeacherAssignmentResponse(**a.__dict__) for a in assignments]
