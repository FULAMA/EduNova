from datetime import datetime, timezone
from uuid import uuid4

import pytest

from src.shared.application.events.event_dispatcher import EventDispatcher
from src.shared.application.events.event_handler import EventHandler
from src.shared.domain.events.domain_event import DomainEvent


class FakeEventHandler(EventHandler):
    def __init__(self) -> None:
        self.received_events: list[DomainEvent] = []

    def handle(self, event: DomainEvent) -> None:
        self.received_events.append(event)


class FakeEventDispatcher(EventDispatcher):
    def __init__(self) -> None:
        self.handlers: dict[type[DomainEvent], list[EventHandler]] = {}

    def register(
        self,
        event_type: type[DomainEvent],
        handler: EventHandler,
    ) -> None:
        self.handlers.setdefault(event_type, []).append(handler)

    def dispatch(self, event: DomainEvent) -> None:
        for handler in self.handlers.get(type(event), []):
            handler.handle(event)


def create_event() -> DomainEvent:
    return DomainEvent(
        event_id=uuid4(),
        occurred_at=datetime.now(timezone.utc),
    )


def test_event_dispatcher_registers_and_dispatches_event() -> None:
    dispatcher = FakeEventDispatcher()
    handler = FakeEventHandler()
    event = create_event()

    dispatcher.register(DomainEvent, handler)
    dispatcher.dispatch(event)

    assert handler.received_events == [event]


def test_event_dispatcher_supports_multiple_handlers() -> None:
    dispatcher = FakeEventDispatcher()
    first_handler = FakeEventHandler()
    second_handler = FakeEventHandler()
    event = create_event()

    dispatcher.register(DomainEvent, first_handler)
    dispatcher.register(DomainEvent, second_handler)

    dispatcher.dispatch(event)

    assert first_handler.received_events == [event]
    assert second_handler.received_events == [event]


def test_event_dispatcher_base_remains_abstract() -> None:
    with pytest.raises(TypeError):
        EventDispatcher()  # type: ignore[abstract]
