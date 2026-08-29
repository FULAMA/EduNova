from dataclasses import dataclass


@dataclass(frozen=True)
class AnalyzeAcademicRiskRequest:
    average: float
    attendance_rate: float
    unjustified_absences: int