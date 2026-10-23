from tools.edunova.agents.evidence_assessment import EvidenceAssessment
from tools.edunova.agents.evidence_gate import EvidenceGate
from tools.edunova.agents.evidence_level import EvidenceLevel


def observed(statement: str = "Observed statement") -> EvidenceAssessment:
    return EvidenceAssessment(
        statement=statement,
        level=EvidenceLevel.OBSERVED,
        source_path="src/example.py",
        start_line=1,
        end_line=3,
        reason="Directly observed.",
    )


def unknown(statement: str = "Unknown statement") -> EvidenceAssessment:
    return EvidenceAssessment(
        statement=statement,
        level=EvidenceLevel.UNKNOWN,
        reason="Insufficient evidence.",
    )


def test_all_observed_evidence_is_admissible():
    result = EvidenceGate().evaluate(
        (observed(),)
    )

    assert result.admissible is True
    assert result.requires_human_review is False


def test_empty_evidence_requires_human_review():
    result = EvidenceGate().evaluate(())

    assert result.admissible is False
    assert result.requires_human_review is True


def test_unknown_evidence_is_not_admissible():
    result = EvidenceGate().evaluate(
        (unknown(),)
    )

    assert result.admissible is False
    assert result.requires_human_review is True


def test_mixed_observed_and_unknown_evidence_is_not_admissible():
    result = EvidenceGate().evaluate(
        (
            observed(),
            unknown(),
        )
    )

    assert result.admissible is False
    assert result.requires_human_review is True


def test_gate_reason_is_deterministic():
    assessments = (
        observed(),
        unknown(),
    )

    first = EvidenceGate().evaluate(assessments)
    second = EvidenceGate().evaluate(assessments)

    assert first == second


def test_gate_does_not_modify_assessments():
    assessment = observed()

    EvidenceGate().evaluate((assessment,))

    assert assessment.level is EvidenceLevel.OBSERVED
    assert assessment.source_path == "src/example.py"
    assert assessment.start_line == 1
    assert assessment.end_line == 3
