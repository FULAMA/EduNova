import pytest

from src.academic.domain.policies.academic_policy import AcademicPolicy


def test_student_passes_with_passing_average():
    policy = AcademicPolicy()

    assert policy.has_passing_average(10) is True
    assert policy.has_passing_average(14) is True


def test_student_fails_below_passing_average():
    policy = AcademicPolicy()

    assert policy.has_passing_average(9.99) is False


def test_subject_is_passed_at_minimum_threshold():
    policy = AcademicPolicy()

    assert policy.is_subject_passed(8) is True


def test_subject_is_failed_below_minimum_threshold():
    policy = AcademicPolicy()

    assert policy.is_subject_passed(7.99) is False


def test_failed_subject_limit():
    policy = AcademicPolicy(
        max_failed_subjects=2
    )

    assert policy.can_pass_with_failed_subjects(2) is True
    assert policy.can_pass_with_failed_subjects(3) is False


def test_average_is_rounded():
    policy = AcademicPolicy(
        rounding_precision=2
    )

    assert policy.round_average(14.5678) == 14.57


def test_grading_scale_must_be_positive():
    with pytest.raises(ValueError):
        AcademicPolicy(grading_scale=0)


def test_passing_average_cannot_exceed_scale():
    with pytest.raises(ValueError):
        AcademicPolicy(
            grading_scale=20,
            passing_average=21,
        )