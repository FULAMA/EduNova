from uuid import uuid4

import pytest

from src.academic.domain.value_objects.subject_result import SubjectResult


@pytest.mark.parametrize("value", [float("nan"), float("inf"), float("-inf")])
def test_subject_result_rejects_non_finite_average_and_coefficient(value):
    with pytest.raises(ValueError):
        SubjectResult(uuid4(), value, 1.0)
    with pytest.raises(ValueError):
        SubjectResult(uuid4(), 10.0, value)
