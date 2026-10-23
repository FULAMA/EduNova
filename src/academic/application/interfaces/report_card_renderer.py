from abc import ABC, abstractmethod

from src.academic.domain.entities.report_card import ReportCard


class ReportCardRenderer(ABC):
    @abstractmethod
    def render(self, report_card: ReportCard) -> bytes:
        raise NotImplementedError
