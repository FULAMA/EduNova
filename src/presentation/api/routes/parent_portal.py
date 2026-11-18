from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Response, status

from src.academic.application.interfaces.report_card_renderer import ReportCardRenderer
from src.academic.application.use_cases.get_student_report_card import GetStudentReportCard
from src.academic.application.use_cases.list_student_report_cards import ListStudentReportCards
from src.identity.application.dto.authenticated_user import AuthenticatedUser
from src.identity.application.interfaces.parent_student_link_repository import (
    ParentStudentLinkRepository,
)
from src.identity.application.use_cases.link_parent_student import LinkParentStudent
from src.identity.application.use_cases.list_parent_children import ListParentChildren
from src.presentation.api.dependencies import (
    get_link_parent_student_use_case,
    get_list_parent_children_use_case,
    get_list_student_report_cards_use_case,
    get_parent_student_link_repository,
    get_report_card_renderer,
    get_student_report_card_use_case,
)
from src.presentation.api.dependencies.auth import (
    get_current_user,
    get_tenant_context,
    require_role,
)
from src.presentation.api.schemas.parent_portal import (
    LinkParentStudentRequest,
    ParentChildResponse,
    ParentStudentLinkResponse,
)
from src.presentation.api.schemas.report_card import ReportCardResponse
from src.presentation.api.schemas.student import StudentSummaryResponse
from src.shared.application.context.tenant_context import TenantContext


router = APIRouter(tags=["Parent Portal"])
_admin_or_direction = [Depends(require_role("ADMIN", "DIRECTION"))]
_parent_only = [Depends(require_role("PARENT"))]


def _report_card_response(rc) -> ReportCardResponse:
    return ReportCardResponse(
        id=rc.id,
        student_id=rc.student_id,
        academic_period_id=rc.academic_period_id,
        deliberation_id=rc.deliberation_id,
        deliberation_version=rc.deliberation_version,
        record_version=rc.record_version,
        report_version=rc.report_version,
        status=rc.status.value,
        snapshot=rc.snapshot,
        snapshot_hash=rc.snapshot_hash,
        created_at=rc.created_at,
        issued_at=rc.issued_at,
    )


@router.post(
    "/parent-links",
    response_model=ParentStudentLinkResponse,
    status_code=status.HTTP_201_CREATED,
    dependencies=_admin_or_direction,
)
def link_parent_student(
    data: LinkParentStudentRequest,
    tenant: TenantContext = Depends(get_tenant_context),
    current_user: AuthenticatedUser = Depends(get_current_user),
    use_case: LinkParentStudent = Depends(get_link_parent_student_use_case),
):
    try:
        link = use_case.execute(
            tenant_id=tenant.tenant_id,
            parent_user_id=data.parent_user_id,
            student_id=data.student_id,
            relationship_type=data.relationship_type,
            actor_id=current_user.id,
        )
        return ParentStudentLinkResponse(
            tenant_id=link.tenant_id,
            parent_user_id=link.parent_user_id,
            student_id=link.student_id,
            relationship_type=link.relationship_type.value,
            created_by=link.created_by,
            created_at=link.created_at,
        )
    except LookupError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.get(
    "/parent-portal/students",
    response_model=list[ParentChildResponse],
    dependencies=_parent_only,
)
def list_parent_children(
    tenant: TenantContext = Depends(get_tenant_context),
    current_user: AuthenticatedUser = Depends(get_current_user),
    use_case: ListParentChildren = Depends(get_list_parent_children_use_case),
):
    children = use_case.execute(tenant.tenant_id, current_user.id)
    return [
        ParentChildResponse(
            student=StudentSummaryResponse(
                id=c.student.id,
                first_name=c.student.first_name,
                last_name=c.student.last_name,
                email=c.student.email,
                registration_number=c.student.registration_number,
                active=c.student.active,
            ),
            relationship_type=c.relationship_type.value,
        )
        for c in children
    ]


@router.get(
    "/parent-portal/students/{student_id}/report-cards",
    response_model=list[ReportCardResponse],
    dependencies=_parent_only,
)
def list_child_report_cards(
    student_id: UUID,
    tenant: TenantContext = Depends(get_tenant_context),
    current_user: AuthenticatedUser = Depends(get_current_user),
    link_repo: ParentStudentLinkRepository = Depends(get_parent_student_link_repository),
    cards_use_case: ListStudentReportCards = Depends(get_list_student_report_cards_use_case),
):
    # PAR-REL-06 : Vérification stricte du rattachement
    if not link_repo.is_parent_of(tenant.tenant_id, current_user.id, student_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Acces refuse : cet eleve n est pas associe a votre compte parent.",
        )

    # Bulletins officiellement publiés (ISSUED) uniquement
    cards = cards_use_case.execute(tenant.tenant_id, student_id)
    return [_report_card_response(c) for c in cards]


@router.get(
    "/parent-portal/students/{student_id}/report-cards/{report_card_id}/pdf",
    dependencies=_parent_only,
)
def download_child_report_card_pdf(
    student_id: UUID,
    report_card_id: UUID,
    tenant: TenantContext = Depends(get_tenant_context),
    current_user: AuthenticatedUser = Depends(get_current_user),
    link_repo: ParentStudentLinkRepository = Depends(get_parent_student_link_repository),
    get_card_use_case: GetStudentReportCard = Depends(get_student_report_card_use_case),
    renderer: ReportCardRenderer = Depends(get_report_card_renderer),
):
    if not link_repo.is_parent_of(tenant.tenant_id, current_user.id, student_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Acces refuse : cet eleve n est pas associe a votre compte parent.",
        )

    try:
        report_card = get_card_use_case.execute(report_card_id, tenant.tenant_id, student_id)
        content = renderer.render(report_card)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail="Bulletin introuvable.") from exc

    return Response(
        content=content,
        media_type="application/pdf",
        headers={"Content-Disposition": f'attachment; filename="bulletin-{report_card.id}.pdf"'},
    )
