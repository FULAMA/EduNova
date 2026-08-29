import pytest
from datetime import date
from uuid import uuid4

from src.domain.entities.assessment import Assessment
from src.domain.entities.grade import Grade
from src.domain.services.subject_average_calculator import (
    SubjectAverageCalculator,
)
from src.domain.value_objects.coefficient import Coefficient
from src.domain.value_objects.score import Score


def create_grade(
    score: float,
    maximum: float,
    coefficient: float,
) -> Grade:

    assessment = Assessment(
        id=uuid4(),
        subject_id=uuid4(),
        title="Evaluation",
        maximum_score=maximum,
        coefficient=Coefficient(coefficient),
        assessment_date=date.today(),
    )

    return Grade(
        id=uuid4(),
        student_id=uuid4(),
        assessment=assessment,
        score=Score(score, maximum),
    )


def test_calculate_weighted_subject_average():

    grades = [
        create_grade(14, 20, 1),
        create_grade(12, 20, 2),
        create_grade(16, 20, 3),
    ]

    calculator = SubjectAverageCalculator()

    result = calculator.calculate(grades)

    assert result == pytest.approx(14.333333333333334)


def test_cannot_calculate_average_without_grades():

    calculator = SubjectAverageCalculator()

    with pytest.raises(ValueError):
        calculator.calculate([])


def test_single_grade_returns_its_normalized_score():

    grades = [
        create_grade(15, 20, 2),
    ]

    calculator = SubjectAverageCalculator()

    result = calculator.calculate(grades)

    assert result == pytest.approx(15)


def test_different_grading_scales_are_normalized():

    grades = [
        create_grade(15, 30, 1),
    ]

    calculator = SubjectAverageCalculator()

    result = calculator.calculate(grades)

    assert result == pytest.approx(10)