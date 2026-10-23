from uuid import UUID

from src.academic.application.interfaces.attendance_repository import AttendanceRepository
from src.academic.application.interfaces.student_academic_record_repository import (
    StudentAcademicRecordRepository,
)
from src.academic.application.dto.analyze_academic_risk_response import AnalyzeAcademicRiskResponse
from src.academic.domain.services.academic_risk_analyzer import AcademicRiskAnalyzer
from src.academic.domain.services.attendance_analyzer import AttendanceAnalyzer


class AnalyzeStudentAcademicRisk:
    def __init__(
        self,
        records: StudentAcademicRecordRepository,
        attendance: AttendanceRepository,
        risk_analyzer: AcademicRiskAnalyzer | None = None,
        attendance_analyzer: AttendanceAnalyzer | None = None,
    ):
        self._records = records
        self._attendance = attendance
        self._risk = risk_analyzer or AcademicRiskAnalyzer()
        self._attendance_analyzer = attendance_analyzer or AttendanceAnalyzer()

    def execute(
        self, tenant_id: UUID, student_id: UUID, academic_period_id: UUID
    ) -> AnalyzeAcademicRiskResponse:
        record = self._records.find_by_student_and_period(
            student_id, academic_period_id, tenant_id
        )
        if record is None:
            raise ValueError("Dossier academique introuvable dans cet etablissement.")
        entries = self._attendance.list_by_student_period(
            tenant_id, student_id, academic_period_id
        )
        if not entries:
            raise ValueError("Impossible de calculer le risque sans releve de presence.")
        if not any(
            self._attendance.has_active_assignment(
                tenant_id, student_id, entry.academic_class_id, entry.academic_year_id
            )
            for entry in entries
        ):
            raise ValueError("Aucune affectation active ne permet de calculer ce risque.")
        result = self._risk.analyze(
            average=record.general_average,
            attendance_rate=self._attendance_analyzer.attendance_rate(entries),
            unjustified_absences=self._attendance_analyzer.count_unjustified_absences(entries),
        )
        return AnalyzeAcademicRiskResponse(
            level=result.level.value, score=result.score, reasons=result.reasons
        )
