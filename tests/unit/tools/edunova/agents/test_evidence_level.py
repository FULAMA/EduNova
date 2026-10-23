from tools.edunova.agents.evidence_level import EvidenceLevel


def test_evidence_levels_are_explicit():
    assert EvidenceLevel.OBSERVED.value == "observed"
    assert EvidenceLevel.UNKNOWN.value == "unknown"
    assert EvidenceLevel.HYPOTHESIS.value == "hypothesis"
    assert EvidenceLevel.RECOMMENDATION.value == "recommendation"


def test_evidence_levels_are_distinct():
    values = {
        EvidenceLevel.OBSERVED.value,
        EvidenceLevel.UNKNOWN.value,
        EvidenceLevel.HYPOTHESIS.value,
        EvidenceLevel.RECOMMENDATION.value,
    }

    assert len(values) == 4


def test_evidence_level_is_string_compatible():
    assert EvidenceLevel.OBSERVED == "observed"
    assert EvidenceLevel.UNKNOWN == "unknown"
    assert EvidenceLevel.HYPOTHESIS == "hypothesis"
    assert EvidenceLevel.RECOMMENDATION == "recommendation"
