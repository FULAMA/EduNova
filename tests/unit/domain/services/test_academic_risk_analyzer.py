from src.domain.services.academic_risk_analyzer import (
    AcademicRiskAnalyzer,
)
from src.domain.value_objects.academic_risk import RiskLevel


def test_student_with_good_results_has_low_risk():

    analyzer = AcademicRiskAnalyzer()

    result = analyzer.analyze(
        average=15,
        attendance_rate=95,
        unjustified_absences=0,
    )

    assert result.level == RiskLevel.LOW
    assert result.score == 0


def test_low_average_creates_risk():

    analyzer = AcademicRiskAnalyzer()

    result = analyzer.analyze(
        average=9,
        attendance_rate=95,
        unjustified_absences=0,
    )

    assert result.level == RiskLevel.MEDIUM
    assert result.score == 40


def test_very_low_average_increases_risk():

    analyzer = AcademicRiskAnalyzer()

    result = analyzer.analyze(
        average=7,
        attendance_rate=95,
        unjustified_absences=0,
    )

    assert result.score == 60


def test_low_attendance_creates_risk():

    analyzer = AcademicRiskAnalyzer()

    result = analyzer.analyze(
        average=14,
        attendance_rate=75,
        unjustified_absences=0,
    )

    assert result.score == 20
    assert result.level == RiskLevel.LOW


def test_many_unjustified_absences_create_risk():

    analyzer = AcademicRiskAnalyzer()

    result = analyzer.analyze(
        average=14,
        attendance_rate=95,
        unjustified_absences=5,
    )

    assert result.score == 20


def test_multiple_risk_factors_create_high_risk():

    analyzer = AcademicRiskAnalyzer()

    result = analyzer.analyze(
        average=7,
        attendance_rate=50,
        unjustified_absences=8,
    )

    assert result.level == RiskLevel.HIGH
    assert result.score == 100
    assert len(result.reasons) >= 3