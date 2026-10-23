from dataclasses import dataclass
from enum import Enum


class Status(str, Enum):
    SAFE = "SAFE"
    WARN = "WARN"
    REVIEW = "REVIEW"
    FAIL = "FAIL"

    @property
    def default_exit_code(self) -> int:
        """Return the stable shell code associated with this status."""
        return {
            Status.SAFE: 0,
            Status.WARN: 10,
            Status.REVIEW: 2,
            Status.FAIL: 1,
        }[self]


@dataclass(frozen=True)
class CommandResult:
    command: str
    status: Status
    message: str
    exit_code: int = 0

    def __post_init__(self) -> None:
        if self.status is Status.SAFE and self.exit_code != 0:
            # A non-zero process code cannot be represented as a safe result.
            object.__setattr__(self, "status", Status.FAIL)

        if self.status is Status.FAIL:
            if self.exit_code == 0:
                object.__setattr__(self, "exit_code", self.status.default_exit_code)
            return

        if self.exit_code == 0:
            object.__setattr__(self, "exit_code", self.status.default_exit_code)

    @property
    def succeeded(self) -> bool:
        return self.status is Status.SAFE
