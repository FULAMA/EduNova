from src.application.dto.analyze_academic_risk_request import (
    AnalyzeAcademicRiskRequest,
)
from src.application.dto.analyze_academic_risk_response import (
    AnalyzeAcademicRiskResponse,
)
from src.application.use_cases.analyze_academic_risk import (
    AnalyzeAcademicRisk,
)
from src.domain.services.academic_risk_analyzer import (
    AcademicRiskAnalyzer,
)
from src.domain.value_objects.academic_risk import RiskLevel


def create_use_case() -> AnalyzeAcademicRisk:

    analyzer = AcademicRiskAnalyzer()

    return AnalyzeAcademicRisk(analyzer)


def test_use_case_returns_academic_risk():

    use_case = create_use_case()

    request = AnalyzeAcademicRiskRequest(
        average=15,
        attendance_rate=95,
        unjustified_absences=0,
    )

    result = use_case.execute(request)

    assert isinstance(result, AnalyzeAcademicRiskResponse)


def test_use_case_returns_low_risk_for_good_student():

    use_case = create_use_case()

    request = AnalyzeAcademicRiskRequest(
        average=15,
        attendance_rate=95,
        unjustified_absences=0,
    )

    result = use_case.execute(request)

    assert result.level == RiskLevel.LOW
    assert result.score == 0


def test_use_case_returns_medium_risk_for_low_average():

    use_case = create_use_case()

    request = AnalyzeAcademicRiskRequest(
        average=9,
        attendance_rate=95,
        unjustified_absences=0,
    )

    result = use_case.execute(request)

    assert result.level == RiskLevel.MEDIUM
    assert result.score == 40


def test_use_case_preserves_risk_reasons():

    use_case = create_use_case()

    request = AnalyzeAcademicRiskRequest(
        average=7,
        attendance_rate=50,
        unjustified_absences=8,
    )

    result = use_case.execute(request)

    assert result.level == RiskLevel.HIGH
    assert result.score == 100
    assert len(result.reasons) >= 3


def test_use_case_passes_all_request_data_to_domain_service():

    use_case = create_use_case()

    request = AnalyzeAcademicRiskRequest(
        average=14,
        attendance_rate=95,
        unjustified_absences=5,
    )

    result = use_case.execute(request)

    assert result.score == 20