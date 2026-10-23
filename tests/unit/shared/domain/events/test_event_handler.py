from datetime import datetime, timezone
from uuid import uuid4

import pytest

from src.shared.application.events.event_handler import EventHandler
from src.shared.domain.events.domain_event import DomainEvent


class FakeEventHandler(EventHandler):
    def __init__(self) -> None:
        self.received_event: DomainEvent | None = None

    def handle(self, event: DomainEvent) -> None:
        self.received_event = event


def test_event_handler_accepts_domain_event() -> None:
    handler = FakeEventHandler()

    event = DomainEvent(
        event_id=uuid4(),
        occurred_at=datetime.now(timezone.utc),
    )

    handler.handle(event)

    assert handler.received_event is event


def test_event_handler_base_remains_abstract() -> None:
    with pytest.raises(TypeError):
        EventHandler()  # type: ignore[abstract]
