import sqlite3
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status

from src.academic.application.exceptions import ActiveConflictError
from src.academic.application.use_cases.change_student_assignment_status import ChangeStudentAssignmentStatus
from src.academic.application.use_cases.create_student_assignment import CreateStudentAssignment
from src.presentation.api.dependencies import (
    get_change_student_assignment_status_use_case,
    get_create_student_assignment_use_case,
    get_apply_student_promotion_use_case,
    get_list_student_assignments_use_case,
)
from src.presentation.api.dependencies.auth import get_current_user, get_tenant_context, require_role
from src.presentation.api.schemas.student_assignment import StudentAssignmentInput, StudentAssignmentResponse, StudentPromotionInput
from src.shared.application.context.tenant_context import TenantContext
from src.identity.application.dto.authenticated_user import AuthenticatedUser


router = APIRouter(prefix="/student-assignments", tags=["Student Assignments"])


@router.get("", response_model=list[StudentAssignmentResponse], dependencies=[Depends(require_role("ADMIN"))])
def list_student_assignments(
    student_id: UUID = Query(...),
    use_case=Depends(get_list_student_assignments_use_case),
    tenant: TenantContext = Depends(get_tenant_context),
) -> list[StudentAssignmentResponse]:
    return [StudentAssignmentResponse(**assignment.__dict__) for assignment in use_case.execute(student_id, tenant.tenant_id)]


@router.post("", response_model=StudentAssignmentResponse, status_code=status.HTTP_201_CREATED, dependencies=[Depends(require_role("ADMIN"))])
def create_student_assignment(
    data: StudentAssignmentInput,
    use_case: CreateStudentAssignment = Depends(get_create_student_assignment_use_case),
    tenant: TenantContext = Depends(get_tenant_context),
    current_user: AuthenticatedUser = Depends(get_current_user),
) -> StudentAssignmentResponse:
    try:
        assignment = use_case.execute(
            tenant.tenant_id, data.student_id, data.academic_year_id,
            data.academic_class_id, current_user.id, data.academic_option_id,
        )
    except sqlite3.IntegrityError as exc:
        raise HTTPException(status_code=409, detail="L'affectation ne peut pas etre enregistree.") from exc
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return StudentAssignmentResponse(**assignment.__dict__)


@router.post("/{assignment_id}/activate", response_model=StudentAssignmentResponse, dependencies=[Depends(require_role("ADMIN"))])
def activate_student_assignment(
    assignment_id: UUID,
    use_case: ChangeStudentAssignmentStatus = Depends(get_change_student_assignment_status_use_case),
    tenant: TenantContext = Depends(get_tenant_context),
) -> StudentAssignmentResponse:
    try:
        assignment = use_case.activate(assignment_id, tenant.tenant_id)
    except ActiveConflictError as exc:
        raise HTTPException(status_code=409, detail="Une affectation active existe deja pour cet eleve et cette annee.") from exc
    except sqlite3.IntegrityError as exc:
        err_str = str(exc)
        if "student_assignments.academic_year_id" in err_str or "uq_student_assignment_active" in err_str:
            raise HTTPException(status_code=409, detail="Une affectation active existe deja pour cet eleve et cette annee.") from exc
        raise HTTPException(status_code=400, detail="Erreur d'integrite des donnees.") from exc
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return StudentAssignmentResponse(**assignment.__dict__)


@router.post("/{assignment_id}/cancel", response_model=StudentAssignmentResponse, dependencies=[Depends(require_role("ADMIN"))])
def cancel_student_assignment(
    assignment_id: UUID,
    use_case: ChangeStudentAssignmentStatus = Depends(get_change_student_assignment_status_use_case),
    tenant: TenantContext = Depends(get_tenant_context),
) -> StudentAssignmentResponse:
    try:
        assignment = use_case.cancel(assignment_id, tenant.tenant_id)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return StudentAssignmentResponse(**assignment.__dict__)


@router.post("/{assignment_id}/close", response_model=StudentAssignmentResponse, dependencies=[Depends(require_role("ADMIN"))])
def close_student_assignment(
    assignment_id: UUID,
    use_case: ChangeStudentAssignmentStatus = Depends(get_change_student_assignment_status_use_case),
    tenant: TenantContext = Depends(get_tenant_context),
) -> StudentAssignmentResponse:
    try:
        assignment = use_case.close(assignment_id, tenant.tenant_id)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return StudentAssignmentResponse(**assignment.__dict__)


@router.post("/promote", response_model=StudentAssignmentResponse, status_code=status.HTTP_201_CREATED, dependencies=[Depends(require_role("ADMIN"))])
def promote_student(
    data: StudentPromotionInput,
    use_case=Depends(get_apply_student_promotion_use_case),
    tenant: TenantContext = Depends(get_tenant_context),
    current_user: AuthenticatedUser = Depends(get_current_user),
) -> StudentAssignmentResponse:
    try:
        assignment = use_case.execute(tenant.tenant_id, data.source_assignment_id, data.deliberation_id, data.target_year_id, data.target_class_id, current_user.id)
    except sqlite3.IntegrityError as exc:
        raise HTTPException(status_code=409, detail="Le passage entre en conflit avec une affectation existante.") from exc
    except ValueError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc
    return StudentAssignmentResponse(**assignment.__dict__)
