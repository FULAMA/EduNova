from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status

from src.academic.application.use_cases.generate_parent_portal_ai_summary import (
    GenerateParentPortalAISummary,
)
from src.academic.application.use_cases.generate_report_card_ai_feedback import (
    GenerateReportCardAIFeedback,
)
from src.academic.application.use_cases.generate_student_risk_ai_diagnosis import (
    GenerateStudentRiskAIDiagnosis,
)
from src.identity.application.dto.authenticated_user import AuthenticatedUser
from src.presentation.api.dependencies import (
    get_generate_parent_portal_ai_summary_use_case,
    get_generate_report_card_ai_feedback_use_case,
    get_generate_student_risk_ai_diagnosis_use_case,
)
from src.presentation.api.dependencies.auth import (
    get_current_user,
    get_tenant_context,
    require_role,
)
from src.presentation.api.schemas.ai_pedagogical import (
    EarlyWarningAIDiagnosisResponse,
    ParentPortalAISummaryResponse,
    ReportCardAIFeedbackResponse,
)
from src.shared.application.context.tenant_context import TenantContext


router = APIRouter(tags=["AI Pedagogical Assistant"])
_staff = [Depends(require_role("ADMIN", "DIRECTION", "PROF", "TEACHER"))]
_parent = [Depends(require_role("PARENT"))]


@router.post(
    "/ai/report-cards/{report_card_id}/feedback",
    response_model=ReportCardAIFeedbackResponse,
    dependencies=_staff,
)
def generate_report_card_feedback(
    report_card_id: UUID,
    use_case: GenerateReportCardAIFeedback = Depends(
        get_generate_report_card_ai_feedback_use_case
    ),
    tenant: TenantContext = Depends(get_tenant_context),
) -> ReportCardAIFeedbackResponse:
    try:
        data = use_case.execute(tenant.tenant_id, report_card_id)
    except LookupError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    return ReportCardAIFeedbackResponse(**data)


@router.post(
    "/ai/students/{student_id}/risk-diagnosis",
    response_model=EarlyWarningAIDiagnosisResponse,
    dependencies=_staff,
)
def generate_student_risk_diagnosis(
    student_id: UUID,
    academic_period_id: UUID = Query(..., description="Période scolaire ciblée"),
    use_case: GenerateStudentRiskAIDiagnosis = Depends(
        get_generate_student_risk_ai_diagnosis_use_case
    ),
    tenant: TenantContext = Depends(get_tenant_context),
) -> EarlyWarningAIDiagnosisResponse:
    try:
        data = use_case.execute(tenant.tenant_id, student_id, academic_period_id)
    except LookupError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    return EarlyWarningAIDiagnosisResponse(**data)


@router.get(
    "/parent-portal/students/{student_id}/report-cards/{report_card_id}/ai-summary",
    response_model=ParentPortalAISummaryResponse,
    dependencies=_parent,
)
def generate_parent_portal_summary(
    student_id: UUID,
    report_card_id: UUID,
    use_case: GenerateParentPortalAISummary = Depends(
        get_generate_parent_portal_ai_summary_use_case
    ),
    tenant: TenantContext = Depends(get_tenant_context),
    current_user: AuthenticatedUser = Depends(get_current_user),
) -> ParentPortalAISummaryResponse:
    try:
        data = use_case.execute(tenant.tenant_id, current_user.id, student_id, report_card_id)
    except PermissionError as exc:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(exc)) from exc
    except LookupError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    return ParentPortalAISummaryResponse(**data)
