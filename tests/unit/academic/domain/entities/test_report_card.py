from datetime import datetime, timezone
from uuid import uuid4

import pytest

from src.academic.domain.entities.report_card import ReportCard, ReportCardStatus


def make_card(status=ReportCardStatus.DRAFT):
    return ReportCard(
        tenant_id=uuid4(), student_id=uuid4(), academic_period_id=uuid4(),
        deliberation_id=uuid4(), deliberation_version=2, record_version=3,
        report_version=1, snapshot={"decision": "ADMITTED"}, snapshot_hash="hash",
        status=status, id=uuid4(), created_at=datetime.now(timezone.utc),
        issued_at=datetime.now(timezone.utc) if status is ReportCardStatus.ISSUED else None,
        issued_by=uuid4() if status is ReportCardStatus.ISSUED else None,
    )


def test_publish_transitions_only_a_draft():
    actor = uuid4()
    result = make_card().publish(actor, datetime.now(timezone.utc))
    assert result.status is ReportCardStatus.ISSUED
    assert result.issued_by == actor
    assert result.snapshot == {"decision": "ADMITTED"}


def test_published_snapshot_cannot_be_published_again():
    with pytest.raises(ValueError, match="prepare"):
        make_card(ReportCardStatus.ISSUED).publish(uuid4(), datetime.now(timezone.utc))


def test_issued_card_requires_publication_metadata():
    with pytest.raises(ValueError, match="auteur"):
        ReportCard(
            tenant_id=uuid4(), student_id=uuid4(), academic_period_id=uuid4(),
            deliberation_id=uuid4(), deliberation_version=1, record_version=1,
            report_version=1, snapshot={"x": 1}, snapshot_hash="hash",
            status=ReportCardStatus.ISSUED,
        )
