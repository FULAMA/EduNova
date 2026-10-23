from abc import ABC, abstractmethod

from src.shared.domain.events.domain_event import DomainEvent


class EventHandler(ABC):
    @abstractmethod
    def handle(self, event: DomainEvent) -> None:
        raise NotImplementedError
