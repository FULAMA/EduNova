from fastapi import APIRouter, Depends, status

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
)
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


@router.post(
    "",
    response_model=AnalyzeAcademicRiskResponseSchema,
    status_code=status.HTTP_200_OK,
)
def analyze_academic_risk(
    data: AnalyzeAcademicRiskRequestSchema,
    use_case: AnalyzeAcademicRisk = Depends(
        get_analyze_academic_risk_use_case
    ),
) -> AnalyzeAcademicRiskResponseSchema:

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
