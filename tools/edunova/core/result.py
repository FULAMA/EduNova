from dataclasses import dataclass
from enum import Enum


class Status(str, Enum):
    SAFE = "SAFE"
    WARN = "WARN"
    REVIEW = "REVIEW"
    FAIL = "FAIL"


@dataclass(frozen=True)
class CommandResult:
    command: str
    status: Status
    message: str
    exit_code: int = 0

    @property
    def succeeded(self) -> bool:
        return self.status != Status.FAIL
