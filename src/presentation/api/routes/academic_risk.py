from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status

from src.academic.application.dto.analyze_academic_risk_request import (
    AnalyzeAcademicRiskRequest,
)
from src.academic.application.dto.analyze_academic_risk_response import (
    AnalyzeAcademicRiskResponse,
)
from src.academic.application.use_cases.analyze_academic_risk import (
    AnalyzeAcademicRisk,
)
from src.presentation.api.dependencies import (
    get_analyze_academic_risk_use_case,
    get_analyze_student_academic_risk_use_case,
)
from src.academic.application.use_cases.analyze_student_academic_risk import AnalyzeStudentAcademicRisk
from src.presentation.api.dependencies.auth import (
    get_tenant_context,
    require_role,
)
from src.shared.application.context.tenant_context import TenantContext
from src.presentation.api.schemas.analyze_academic_risk_request import (
    AnalyzeAcademicRiskRequestSchema,
)
from src.presentation.api.schemas.analyze_academic_risk_response import (
    AnalyzeAcademicRiskResponseSchema,
)


router = APIRouter(
    prefix="/academic-risk",
    tags=["Academic Risk"],
)
_admin = [Depends(require_role("ADMIN"))]


@router.get(
    "/students/{student_id}/periods/{academic_period_id}",
    response_model=AnalyzeAcademicRiskResponseSchema,
    dependencies=_admin,
)
def analyze_student_academic_risk(
    student_id: UUID,
    academic_period_id: UUID,
    use_case: AnalyzeStudentAcademicRisk = Depends(get_analyze_student_academic_risk_use_case),
    tenant: TenantContext = Depends(get_tenant_context),
) -> AnalyzeAcademicRiskResponseSchema:
    try:
        response = use_case.execute(tenant.tenant_id, student_id, academic_period_id)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return AnalyzeAcademicRiskResponseSchema(
        level=response.level, score=response.score, reasons=list(response.reasons)
    )


@router.post(
    "",
    response_model=AnalyzeAcademicRiskResponseSchema,
    status_code=status.HTTP_200_OK,
    deprecated=True,
    dependencies=_admin,
)
def analyze_academic_risk(
    data: AnalyzeAcademicRiskRequestSchema,
    use_case: AnalyzeAcademicRisk = Depends(
        get_analyze_academic_risk_use_case
    ),
) -> AnalyzeAcademicRiskResponseSchema:
    """Compatibility endpoint; the server-backed GET is authoritative."""

    request = AnalyzeAcademicRiskRequest(
        average=data.average,
        attendance_rate=data.attendance_rate,
        unjustified_absences=data.unjustified_absences,
    )

    response: AnalyzeAcademicRiskResponse = use_case.execute(
        request
    )

    return AnalyzeAcademicRiskResponseSchema(
        level=response.level,
        score=response.score,
        reasons=list(response.reasons),
    )
