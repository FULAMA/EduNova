from src.shared.application.events.event_dispatcher import EventDispatcher
from src.shared.application.events.event_handler import EventHandler
from src.shared.domain.events.domain_event import DomainEvent


class InMemoryEventDispatcher(EventDispatcher):
    """Synchronous, process-local dispatch; events are not durably delivered."""

    def __init__(self) -> None:
        self._handlers: dict[type[DomainEvent], list[EventHandler]] = {}

    def register(
        self,
        event_type: type[DomainEvent],
        handler: EventHandler,
    ) -> None:
        self._handlers.setdefault(event_type, []).append(handler)

    def dispatch(self, event: DomainEvent) -> None:
        for handler in self._handlers.get(type(event), []):
            handler.handle(event)
