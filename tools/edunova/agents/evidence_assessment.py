from dataclasses import dataclass

from tools.edunova.agents.evidence_level import EvidenceLevel


@dataclass(frozen=True)
class EvidenceAssessment:
    statement: str
    level: EvidenceLevel
    source_path: str | None = None
    start_line: int | None = None
    end_line: int | None = None
    reason: str = ""

    def __post_init__(self) -> None:
        if not self.statement.strip():
            raise ValueError("statement must not be empty")

        if self.level is EvidenceLevel.OBSERVED:
            if not self.source_path:
                raise ValueError(
                    "observed evidence requires a source_path"
                )

            if self.start_line is None or self.end_line is None:
                raise ValueError(
                    "observed evidence requires line provenance"
                )

            if self.start_line < 1:
                raise ValueError(
                    "start_line must be greater than or equal to 1"
                )

            if self.end_line < self.start_line:
                raise ValueError(
                    "end_line must be greater than or equal to start_line"
                )
