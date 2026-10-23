from abc import ABC, abstractmethod

from tools.edunova.execution.decision import ExecutionDecision
from tools.edunova.execution.request import ExecutionRequest


class ExecutionPolicy(ABC):
    @abstractmethod
    def evaluate(
        self,
        request: ExecutionRequest,
    ) -> ExecutionDecision:
        raise NotImplementedError
