import pytest


from datetime import datetime, timezone
from uuid import uuid4


from src.shared.application.events.event_handler import EventHandler
from src.shared.application.events.in_memory_event_dispatcher import (
    InMemoryEventDispatcher,
)
from src.shared.domain.events.domain_event import DomainEvent


class FirstTestEvent(DomainEvent):
    pass


class SecondTestEvent(DomainEvent):
    pass


class FakeEventHandler(EventHandler):
    def __init__(self) -> None:
        self.received_events: list[DomainEvent] = []

    def handle(self, event: DomainEvent) -> None:
        self.received_events.append(event)


def create_event(event_type: type[DomainEvent]) -> DomainEvent:
    return event_type(
        event_id=uuid4(),
        occurred_at=datetime.now(timezone.utc),
    )


def test_dispatcher_sends_event_to_registered_handler() -> None:
    dispatcher = InMemoryEventDispatcher()
    handler = FakeEventHandler()
    event = create_event(FirstTestEvent)

    dispatcher.register(FirstTestEvent, handler)
    dispatcher.dispatch(event)

    assert handler.received_events == [event]


def test_dispatcher_sends_event_to_multiple_handlers() -> None:
    dispatcher = InMemoryEventDispatcher()
    first_handler = FakeEventHandler()
    second_handler = FakeEventHandler()
    event = create_event(FirstTestEvent)

    dispatcher.register(FirstTestEvent, first_handler)
    dispatcher.register(FirstTestEvent, second_handler)

    dispatcher.dispatch(event)

    assert first_handler.received_events == [event]
    assert second_handler.received_events == [event]


def test_dispatcher_ignores_event_without_registered_handler() -> None:
    dispatcher = InMemoryEventDispatcher()
    event = create_event(FirstTestEvent)

    dispatcher.dispatch(event)


def test_dispatcher_does_not_call_handler_registered_for_other_event_type() -> None:
    dispatcher = InMemoryEventDispatcher()
    handler = FakeEventHandler()
    event = create_event(FirstTestEvent)

    dispatcher.register(SecondTestEvent, handler)
    dispatcher.dispatch(event)

    assert handler.received_events == []

class RecordingEventHandler(EventHandler):
    def __init__(self, name: str, calls: list[str]) -> None:
        self.name = name
        self.calls = calls

    def handle(self, event: DomainEvent) -> None:
        self.calls.append(self.name)


class FailingEventHandler(EventHandler):
    def __init__(self, calls: list[str]) -> None:
        self.calls = calls

    def handle(self, event: DomainEvent) -> None:
        self.calls.append("failing")
        raise RuntimeError("forced handler failure")


def test_dispatcher_preserves_handler_registration_order() -> None:
    dispatcher = InMemoryEventDispatcher()
    calls: list[str] = []
    first_handler = RecordingEventHandler("first", calls)
    second_handler = RecordingEventHandler("second", calls)
    event = create_event(FirstTestEvent)

    dispatcher.register(FirstTestEvent, first_handler)
    dispatcher.register(FirstTestEvent, second_handler)

    dispatcher.dispatch(event)

    assert calls == ["first", "second"]


def test_dispatcher_propagates_handler_exception() -> None:
    dispatcher = InMemoryEventDispatcher()
    calls: list[str] = []
    handler = FailingEventHandler(calls)
    event = create_event(FirstTestEvent)

    dispatcher.register(FirstTestEvent, handler)

    with pytest.raises(RuntimeError, match="forced handler failure"):
        dispatcher.dispatch(event)

    assert calls == ["failing"]


def test_dispatcher_stops_after_handler_exception() -> None:
    dispatcher = InMemoryEventDispatcher()
    calls: list[str] = []
    failing_handler = FailingEventHandler(calls)
    later_handler = RecordingEventHandler("later", calls)
    event = create_event(FirstTestEvent)

    dispatcher.register(FirstTestEvent, failing_handler)
    dispatcher.register(FirstTestEvent, later_handler)

    with pytest.raises(RuntimeError, match="forced handler failure"):
        dispatcher.dispatch(event)

    assert calls == ["failing"]



def test_dispatcher_invokes_handler_once_per_registration() -> None:
    dispatcher = InMemoryEventDispatcher()
    handler = FakeEventHandler()
    event = create_event(FirstTestEvent)

    dispatcher.register(FirstTestEvent, handler)
    dispatcher.register(FirstTestEvent, handler)

    dispatcher.dispatch(event)

    assert handler.received_events == [event, event]

def test_dispatcher_instances_do_not_share_handlers() -> None:
    dispatcher_a = InMemoryEventDispatcher()
    dispatcher_b = InMemoryEventDispatcher()

    handler = FakeEventHandler()
    event = create_event(FirstTestEvent)

    dispatcher_a.register(FirstTestEvent, handler)

    dispatcher_b.dispatch(event)

    assert handler.received_events == []

def test_dispatcher_retains_registered_handlers_for_its_lifetime() -> None:
    dispatcher = InMemoryEventDispatcher()
    handler = FakeEventHandler()
    event = create_event(FirstTestEvent)

    dispatcher.register(FirstTestEvent, handler)

    dispatcher.dispatch(event)

    assert handler.received_events == [event]

def test_dispatcher_does_not_share_registered_handlers_with_new_instance() -> None:
    dispatcher_a = InMemoryEventDispatcher()
    dispatcher_b = InMemoryEventDispatcher()

    handler = FakeEventHandler()
    event = create_event(FirstTestEvent)

    dispatcher_a.register(FirstTestEvent, handler)

    dispatcher_a.dispatch(event)
    dispatcher_b.dispatch(event)

    assert handler.received_events == [event]
