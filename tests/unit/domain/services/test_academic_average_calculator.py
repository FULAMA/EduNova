import pytest
from uuid import uuid4

from src.academic.domain.services.academic_average_calculator import (
    AcademicAverageCalculator,
)
from src.academic.domain.value_objects.subject_result import SubjectResult


def test_calculate_academic_average():

    results = [
        SubjectResult(uuid4(), 14, 4),
        SubjectResult(uuid4(), 12, 3),
        SubjectResult(uuid4(), 16, 5),
    ]

    calculator = AcademicAverageCalculator()

    result = calculator.calculate(results)

    assert result == pytest.approx(14.333333333333334)


def test_cannot_calculate_academic_average_without_subjects():

    calculator = AcademicAverageCalculator()

    with pytest.raises(ValueError):
        calculator.calculate([])


def test_single_subject_returns_its_average():

    results = [
        SubjectResult(uuid4(), 15, 4),
    ]

    calculator = AcademicAverageCalculator()

    result = calculator.calculate(results)

    assert result == pytest.approx(15)


def test_subject_coefficient_affects_academic_average():

    results = [
        SubjectResult(uuid4(), 10, 1),
        SubjectResult(uuid4(), 20, 3),
    ]

    calculator = AcademicAverageCalculator()

    result = calculator.calculate(results)

    assert result == pytest.approx(17.5)
