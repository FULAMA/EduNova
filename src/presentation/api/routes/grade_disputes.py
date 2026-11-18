from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status

from src.academic.application.use_cases.list_grade_disputes import ListGradeDisputes
from src.academic.application.use_cases.resolve_grade_dispute import ResolveGradeDispute
from src.academic.application.use_cases.review_grade_dispute import ReviewGradeDispute
from src.academic.application.use_cases.submit_grade_dispute import SubmitGradeDispute
from src.academic.domain.entities.grade_dispute import GradeDispute, GradeDisputeStatus
from src.identity.application.dto.authenticated_user import AuthenticatedUser
from src.presentation.api.dependencies import (
    get_list_grade_disputes_use_case,
    get_resolve_grade_dispute_use_case,
    get_review_grade_dispute_use_case,
    get_submit_grade_dispute_use_case,
)
from src.presentation.api.dependencies.auth import (
    get_current_user,
    get_tenant_context,
    require_role,
)
from src.presentation.api.schemas.grade_dispute import (
    CreateGradeDisputeRequest,
    GradeDisputeResponse,
    ResolveGradeDisputeRequest,
)
from src.shared.application.context.tenant_context import TenantContext


router = APIRouter(prefix="/academic/disputes", tags=["Grade Disputes"])
_admin_or_direction = [Depends(require_role("ADMIN", "DIRECTION"))]


def _to_response(d: GradeDispute) -> GradeDisputeResponse:
    return GradeDisputeResponse(
        id=d.id,
        tenant_id=d.tenant_id,
        student_id=d.student_id,
        academic_period_id=d.academic_period_id,
        subject_id=d.subject_id,
        reason=d.reason,
        status=d.status,
        submitted_by=d.submitted_by,
        submitted_at=d.submitted_at,
        reviewed_by=d.reviewed_by,
        reviewed_at=d.reviewed_at,
        resolution_notes=d.resolution_notes,
        resolved_at=d.resolved_at,
    )


@router.post(
    "",
    response_model=GradeDisputeResponse,
    status_code=status.HTTP_201_CREATED,
)
def submit_dispute(
    data: CreateGradeDisputeRequest,
    use_case: SubmitGradeDispute = Depends(get_submit_grade_dispute_use_case),
    tenant: TenantContext = Depends(get_tenant_context),
    current_user: AuthenticatedUser = Depends(get_current_user),
):
    try:
        dispute = use_case.execute(
            tenant_id=tenant.tenant_id,
            student_id=data.student_id,
            academic_period_id=data.academic_period_id,
            subject_id=data.subject_id,
            reason=data.reason,
            submitted_by=current_user.id,
        )
        return _to_response(dispute)
    except LookupError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.post(
    "/{dispute_id}/review",
    response_model=GradeDisputeResponse,
    dependencies=_admin_or_direction,
)
def review_dispute(
    dispute_id: UUID,
    use_case: ReviewGradeDispute = Depends(get_review_grade_dispute_use_case),
    tenant: TenantContext = Depends(get_tenant_context),
    current_user: AuthenticatedUser = Depends(get_current_user),
):
    try:
        dispute = use_case.execute(
            tenant_id=tenant.tenant_id,
            dispute_id=dispute_id,
            reviewer_id=current_user.id,
        )
        return _to_response(dispute)
    except LookupError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.post(
    "/{dispute_id}/resolve",
    response_model=GradeDisputeResponse,
    dependencies=_admin_or_direction,
)
def resolve_dispute(
    dispute_id: UUID,
    data: ResolveGradeDisputeRequest,
    use_case: ResolveGradeDispute = Depends(get_resolve_grade_dispute_use_case),
    tenant: TenantContext = Depends(get_tenant_context),
    current_user: AuthenticatedUser = Depends(get_current_user),
):
    try:
        dispute = use_case.execute(
            tenant_id=tenant.tenant_id,
            dispute_id=dispute_id,
            decision=data.decision,
            resolution_notes=data.resolution_notes,
            reviewer_id=current_user.id,
        )
        return _to_response(dispute)
    except LookupError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.get(
    "",
    response_model=list[GradeDisputeResponse],
)
def list_disputes(
    student_id: UUID | None = Query(None),
    academic_period_id: UUID | None = Query(None),
    subject_id: UUID | None = Query(None),
    status: GradeDisputeStatus | None = Query(None),
    use_case: ListGradeDisputes = Depends(get_list_grade_disputes_use_case),
    tenant: TenantContext = Depends(get_tenant_context),
    current_user: AuthenticatedUser = Depends(get_current_user),
):
    disputes = use_case.execute(
        tenant_id=tenant.tenant_id,
        student_id=student_id,
        academic_period_id=academic_period_id,
        subject_id=subject_id,
        status=status,
    )
    return [_to_response(d) for d in disputes]
