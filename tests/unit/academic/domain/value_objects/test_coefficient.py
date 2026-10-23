import pytest

from src.academic.domain.value_objects.coefficient import Coefficient


def test_coefficient_requires_finite_positive_value():
    assert Coefficient(1.0).value == 1.0
    for invalid in (0.0, -1.0, float("nan"), float("inf"), float("-inf")):
        with pytest.raises(ValueError):
            Coefficient(invalid)
