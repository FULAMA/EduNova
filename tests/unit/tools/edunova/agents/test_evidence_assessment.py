import pytest

from tools.edunova.agents.evidence_assessment import EvidenceAssessment
from tools.edunova.agents.evidence_level import EvidenceLevel


def test_observed_assessment_contains_source_and_line_provenance():
    assessment = EvidenceAssessment(
        statement="VALUE = 42 is defined in the file.",
        level=EvidenceLevel.OBSERVED,
        source_path="src/example.py",
        start_line=1,
        end_line=1,
        reason="Content was directly read from the project.",
    )

    assert assessment.statement == "VALUE = 42 is defined in the file."
    assert assessment.level is EvidenceLevel.OBSERVED
    assert assessment.source_path == "src/example.py"
    assert assessment.start_line == 1
    assert assessment.end_line == 1
    assert assessment.reason == "Content was directly read from the project."


def test_unknown_assessment_does_not_require_source():
    assessment = EvidenceAssessment(
        statement="The production database technology is unknown.",
        level=EvidenceLevel.UNKNOWN,
        reason="No explicit evidence establishes the current runtime database.",
    )

    assert assessment.level is EvidenceLevel.UNKNOWN
    assert assessment.source_path is None
    assert assessment.start_line is None
    assert assessment.end_line is None


def test_hypothesis_can_exist_without_observed_source():
    assessment = EvidenceAssessment(
        statement="The configuration may be loaded during startup.",
        level=EvidenceLevel.HYPOTHESIS,
        reason="Possible explanation not established by direct evidence.",
    )

    assert assessment.level is EvidenceLevel.HYPOTHESIS
    assert assessment.source_path is None


def test_recommendation_can_exist_without_observed_source():
    assessment = EvidenceAssessment(
        statement="Add an integration test for the runtime configuration.",
        level=EvidenceLevel.RECOMMENDATION,
        reason="Suggested engineering action.",
    )

    assert assessment.level is EvidenceLevel.RECOMMENDATION
    assert assessment.source_path is None


def test_observed_requires_source_path():
    with pytest.raises(ValueError, match="source_path"):
        EvidenceAssessment(
            statement="Observed fact.",
            level=EvidenceLevel.OBSERVED,
            start_line=1,
            end_line=1,
        )


def test_observed_requires_line_provenance():
    with pytest.raises(ValueError, match="line provenance"):
        EvidenceAssessment(
            statement="Observed fact.",
            level=EvidenceLevel.OBSERVED,
            source_path="src/example.py",
        )


def test_observed_requires_valid_start_line():
    with pytest.raises(ValueError, match="start_line"):
        EvidenceAssessment(
            statement="Observed fact.",
            level=EvidenceLevel.OBSERVED,
            source_path="src/example.py",
            start_line=0,
            end_line=1,
        )


def test_observed_requires_valid_line_range():
    with pytest.raises(ValueError, match="end_line"):
        EvidenceAssessment(
            statement="Observed fact.",
            level=EvidenceLevel.OBSERVED,
            source_path="src/example.py",
            start_line=5,
            end_line=3,
        )


def test_statement_cannot_be_empty():
    with pytest.raises(ValueError, match="statement"):
        EvidenceAssessment(
            statement="   ",
            level=EvidenceLevel.UNKNOWN,
        )
