import pytest

from src.domain.value_objects.score import Score


def test_score_is_valid():
    score = Score(15, 20)

    assert score.value == 15
    assert score.maximum == 20


def test_score_is_normalized_to_20():
    score = Score(15, 30)

    assert score.normalized_to_20() == 10


def test_score_cannot_be_negative():
    with pytest.raises(ValueError):
        Score(-1, 20)


def test_score_cannot_exceed_maximum():
    with pytest.raises(ValueError):
        Score(21, 20)


def test_maximum_must_be_positive():
    with pytest.raises(ValueError):
        Score(10, 0)