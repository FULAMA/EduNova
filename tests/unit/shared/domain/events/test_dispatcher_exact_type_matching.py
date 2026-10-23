from datetime import datetime, timezone
from uuid import uuid4

from src.shared.application.events.event_handler import EventHandler
from src.shared.application.events.in_memory_event_dispatcher import (
    InMemoryEventDispatcher,
)
from src.shared.domain.events.domain_event import DomainEvent


class ConcreteTestEvent(DomainEvent):
    pass


class RecordingHandler(EventHandler):
    def __init__(self) -> None:
        self.received_events: list[DomainEvent] = []

    def handle(self, event: DomainEvent) -> None:
        self.received_events.append(event)


def test_dispatcher_uses_exact_event_type_matching() -> None:
    dispatcher = InMemoryEventDispatcher()
    handler = RecordingHandler()

    event = ConcreteTestEvent(
        event_id=uuid4(),
        occurred_at=datetime.now(timezone.utc),
    )

    dispatcher.register(DomainEvent, handler)
    dispatcher.dispatch(event)

    assert handler.received_events == []
