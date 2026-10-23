from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Response, status

from src.academic.application.use_cases.get_student_report_card import GetStudentReportCard
from src.academic.application.use_cases.list_student_report_cards import ListStudentReportCards
from src.academic.application.use_cases.prepare_report_card import PrepareReportCard
from src.academic.application.use_cases.publish_report_card import PublishReportCard
from src.identity.application.dto.authenticated_user import AuthenticatedUser
from src.presentation.api.dependencies import (
    get_student_report_card_use_case,
    get_correct_report_card_use_case,
    get_report_card_renderer,
    get_list_student_report_cards_use_case,
    get_prepare_report_card_use_case,
    get_publish_report_card_use_case,
    get_student_portal_profile_use_case,
)
from src.presentation.api.dependencies.auth import get_current_user, get_tenant_context, require_role
from src.presentation.api.schemas.report_card import PrepareReportCardRequest, ReportCardResponse
from src.academic.application.interfaces.report_card_renderer import ReportCardRenderer
from src.shared.application.context.tenant_context import TenantContext


router = APIRouter(prefix="/report-cards", tags=["Report Cards"])


def _response(report_card) -> ReportCardResponse:
    return ReportCardResponse(
        id=report_card.id,
        student_id=report_card.student_id,
        academic_period_id=report_card.academic_period_id,
        deliberation_id=report_card.deliberation_id,
        deliberation_version=report_card.deliberation_version,
        record_version=report_card.record_version,
        report_version=report_card.report_version,
        status=report_card.status.value,
        snapshot=report_card.snapshot,
        snapshot_hash=report_card.snapshot_hash,
        created_at=report_card.created_at,
        issued_at=report_card.issued_at,
    )


@router.post(
    "/{student_id}/{academic_period_id}/prepare",
    response_model=ReportCardResponse,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_role("ADMIN"))],
)
def prepare_report_card(
    student_id: UUID,
    academic_period_id: UUID,
    data: PrepareReportCardRequest,
    use_case: PrepareReportCard = Depends(get_prepare_report_card_use_case),
    tenant: TenantContext = Depends(get_tenant_context),
    current_user: AuthenticatedUser = Depends(get_current_user),
) -> ReportCardResponse:
    try:
        return _response(use_case.execute(tenant.tenant_id, student_id, academic_period_id, data.deliberation_id, current_user.id))
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.post(
    "/{report_card_id}/publish",
    response_model=ReportCardResponse,
    dependencies=[Depends(require_role("ADMIN"))],
)
def publish_report_card(
    report_card_id: UUID,
    use_case: PublishReportCard = Depends(get_publish_report_card_use_case),
    tenant: TenantContext = Depends(get_tenant_context),
    current_user: AuthenticatedUser = Depends(get_current_user),
) -> ReportCardResponse:
    try:
        return _response(use_case.execute(tenant.tenant_id, report_card_id, current_user.id))
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.post(
    "/{report_card_id}/correct",
    response_model=ReportCardResponse,
    dependencies=[Depends(require_role("ADMIN"))],
)
def correct_report_card(
    report_card_id: UUID,
    data: PrepareReportCardRequest,
    use_case=Depends(get_correct_report_card_use_case),
    tenant: TenantContext = Depends(get_tenant_context),
    current_user: AuthenticatedUser = Depends(get_current_user),
) -> ReportCardResponse:
    try:
        return _response(use_case.execute(
            tenant.tenant_id, report_card_id, data.deliberation_id, current_user.id,
        ))
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.get("/{report_card_id}", response_model=ReportCardResponse, dependencies=[Depends(require_role("STUDENT"))])
def get_student_report_card(
    report_card_id: UUID,
    use_case: GetStudentReportCard = Depends(get_student_report_card_use_case),
    profile_use_case=Depends(get_student_portal_profile_use_case),
    tenant: TenantContext = Depends(get_tenant_context),
    current_user: AuthenticatedUser = Depends(get_current_user),
) -> ReportCardResponse:
    try:
        profile = profile_use_case.execute(current_user.id, tenant.tenant_id)
        return _response(use_case.execute(report_card_id, tenant.tenant_id, profile.student.id))
    except ValueError as exc:
        raise HTTPException(status_code=404, detail="Bulletin introuvable.") from exc


@router.get("/{report_card_id}/pdf", dependencies=[Depends(require_role("STUDENT"))])
def download_student_report_card_pdf(
    report_card_id: UUID,
    use_case: GetStudentReportCard = Depends(get_student_report_card_use_case),
    renderer: ReportCardRenderer = Depends(get_report_card_renderer),
    profile_use_case=Depends(get_student_portal_profile_use_case),
    tenant: TenantContext = Depends(get_tenant_context),
    current_user: AuthenticatedUser = Depends(get_current_user),
) -> Response:
    try:
        profile = profile_use_case.execute(current_user.id, tenant.tenant_id)
        report_card = use_case.execute(report_card_id, tenant.tenant_id, profile.student.id)
        content = renderer.render(report_card)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail="Bulletin introuvable.") from exc
    return Response(
        content=content,
        media_type="application/pdf",
        headers={"Content-Disposition": f'attachment; filename="bulletin-{report_card.id}.pdf"'},
    )


@router.get("", response_model=list[ReportCardResponse], dependencies=[Depends(require_role("STUDENT"))])
def list_student_report_cards(
    use_case: ListStudentReportCards = Depends(get_list_student_report_cards_use_case),
    profile_use_case=Depends(get_student_portal_profile_use_case),
    tenant: TenantContext = Depends(get_tenant_context),
    current_user: AuthenticatedUser = Depends(get_current_user),
) -> list[ReportCardResponse]:
    try:
        profile = profile_use_case.execute(current_user.id, tenant.tenant_id)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail="Bulletin introuvable.") from exc
    return [_response(item) for item in use_case.execute(tenant.tenant_id, profile.student.id)]
