from tools.edunova.agents.evidence import EvidenceItem
from tools.edunova.agents.evidence_assessor import EvidenceAssessor
from tools.edunova.agents.evidence_level import EvidenceLevel


def test_assessor_marks_directly_read_content_as_observed():
    evidence = EvidenceItem(
        path="src/example.py",
        exists=True,
        content="VALUE = 42\n",
        start_line=1,
        end_line=1,
    )

    assessment = EvidenceAssessor().assess(
        "src/example.py defines VALUE as 42.",
        evidence,
    )

    assert assessment.level is EvidenceLevel.OBSERVED
    assert assessment.source_path == "src/example.py"
    assert assessment.start_line == 1
    assert assessment.end_line == 1


def test_assessor_preserves_full_line_provenance():
    evidence = EvidenceItem(
        path="src/example.py",
        exists=True,
        content="a\nb\nc\n",
        start_line=1,
        end_line=3,
    )

    assessment = EvidenceAssessor().assess(
        "The file contains three lines.",
        evidence,
    )

    assert assessment.level is EvidenceLevel.OBSERVED
    assert assessment.start_line == 1
    assert assessment.end_line == 3


def test_assessor_marks_missing_file_as_unknown():
    evidence = EvidenceItem(
        path="src/missing.py",
        exists=False,
    )

    assessment = EvidenceAssessor().assess(
        "src/missing.py contains implementation code.",
        evidence,
    )

    assert assessment.level is EvidenceLevel.UNKNOWN
    assert assessment.source_path is None
    assert assessment.start_line is None
    assert assessment.end_line is None


def test_assessor_marks_omitted_content_as_unknown():
    evidence = EvidenceItem(
        path="src/large.py",
        exists=True,
        content="[CONTENT OMITTED: file exceeds 20 bytes]",
    )

    assessment = EvidenceAssessor().assess(
        "The file contains a specific implementation.",
        evidence,
    )

    assert assessment.level is EvidenceLevel.UNKNOWN
    assert assessment.source_path is None


def test_assessor_marks_unavailable_content_as_unknown():
    evidence = EvidenceItem(
        path="src/example.py",
        exists=True,
        content="[CONTENT UNAVAILABLE: UnicodeDecodeError]",
    )

    assessment = EvidenceAssessor().assess(
        "The file contains valid UTF-8 source code.",
        evidence,
    )

    assert assessment.level is EvidenceLevel.UNKNOWN


def test_assessor_does_not_invent_line_provenance():
    evidence = EvidenceItem(
        path="src/example.py",
        exists=True,
        content="VALUE = 42\n",
    )

    assessment = EvidenceAssessor().assess(
        "The file defines VALUE.",
        evidence,
    )

    assert assessment.level is EvidenceLevel.UNKNOWN
    assert assessment.start_line is None
    assert assessment.end_line is None


def test_assessor_preserves_statement():
    evidence = EvidenceItem(
        path="src/example.py",
        exists=True,
        content="VALUE = 42\n",
        start_line=1,
        end_line=1,
    )

    statement = "VALUE is defined in the file."

    assessment = EvidenceAssessor().assess(
        statement,
        evidence,
    )

    assert assessment.statement == statement


def test_assessor_is_deterministic():
    evidence = EvidenceItem(
        path="src/example.py",
        exists=True,
        content="VALUE = 42\n",
        start_line=1,
        end_line=1,
    )

    assessor = EvidenceAssessor()

    first = assessor.assess(
        "VALUE is defined in the file.",
        evidence,
    )
    second = assessor.assess(
        "VALUE is defined in the file.",
        evidence,
    )

    assert first == second
