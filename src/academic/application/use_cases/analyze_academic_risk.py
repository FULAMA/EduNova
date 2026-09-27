from src.academic.application.dto.analyze_academic_risk_request import (
    AnalyzeAcademicRiskRequest,
)
from src.academic.application.dto.analyze_academic_risk_response import (
    AnalyzeAcademicRiskResponse,
)
from src.academic.domain.services.academic_risk_analyzer import (
    AcademicRiskAnalyzer,
)


class AnalyzeAcademicRisk:

    def __init__(
        self,
        analyzer: AcademicRiskAnalyzer,
    ):
        self._analyzer = analyzer

    def execute(
        self,
        request: AnalyzeAcademicRiskRequest,
    ) -> AnalyzeAcademicRiskResponse:

        result = self._analyzer.analyze(
            average=request.average,
            attendance_rate=request.attendance_rate,
            unjustified_absences=request.unjustified_absences,
        )

        return AnalyzeAcademicRiskResponse(
            level=result.level.value,
            score=result.score,
            reasons=result.reasons,
        )
