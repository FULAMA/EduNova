from abc import ABC, abstractmethod

from src.shared.application.events.event_handler import EventHandler
from src.shared.domain.events.domain_event import DomainEvent


class EventDispatcher(ABC):
    @abstractmethod
    def register(
        self,
        event_type: type[DomainEvent],
        handler: EventHandler,
    ) -> None:
        raise NotImplementedError

    @abstractmethod
    def dispatch(self, event: DomainEvent) -> None:
        raise NotImplementedError
