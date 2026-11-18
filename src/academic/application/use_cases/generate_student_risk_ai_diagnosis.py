from typing import Any
from uuid import UUID

from src.academic.application.interfaces.ai_pedagogical_service import AIPedagogicalService
from src.academic.application.interfaces.attendance_repository import AttendanceRepository
from src.academic.application.interfaces.student_academic_record_repository import (
    StudentAcademicRecordRepository,
)
from src.academic.application.interfaces.student_repository import StudentRepository
from src.academic.application.use_cases.analyze_student_academic_risk import (
    AnalyzeStudentAcademicRisk,
)
from src.academic.domain.services.attendance_analyzer import AttendanceAnalyzer


class GenerateStudentRiskAIDiagnosis:
    def __init__(
        self,
        ai_service: AIPedagogicalService,
        risk_use_case: AnalyzeStudentAcademicRisk,
        students: StudentRepository,
        records: StudentAcademicRecordRepository,
        attendance: AttendanceRepository,
        attendance_analyzer: AttendanceAnalyzer | None = None,
    ):
        self._ai = ai_service
        self._risk = risk_use_case
        self._students = students
        self._records = records
        self._attendance = attendance
        self._attendance_analyzer = attendance_analyzer or AttendanceAnalyzer()

    def execute(
        self, tenant_id: UUID, student_id: UUID, academic_period_id: UUID
    ) -> dict[str, Any]:
        student = self._students.get_by_id_and_tenant(student_id, tenant_id)
        if student is None:
            raise LookupError("Eleve introuvable dans cet etablissement.")

        student_name = f"{student.first_name} {student.last_name}"

        # Calculer le risque objectif via le moteur métier existant
        risk_res = self._risk.execute(tenant_id, student_id, academic_period_id)

        record = self._records.find_by_student_and_period(student_id, academic_period_id, tenant_id)
        avg = record.general_average if record else 10.0

        entries = self._attendance.list_by_student_period(tenant_id, student_id, academic_period_id)
        att_rate = self._attendance_analyzer.attendance_rate(entries) if entries else 100.0
        absences = self._attendance_analyzer.count_unjustified_absences(entries) if entries else 0

        diagnosis = self._ai.generate_early_warning_diagnosis(
            student_name=student_name,
            risk_level=risk_res.level,
            risk_score=risk_res.score,
            reasons=list(risk_res.reasons),
            general_average=float(avg),
            attendance_rate=float(att_rate),
            unjustified_absences=int(absences),
        )

        return {
            "student_id": str(student_id),
            "student_name": student_name,
            "academic_period_id": str(academic_period_id),
            "risk_level": diagnosis["risk_level"],
            "risk_score": diagnosis["risk_score"],
            "diagnostic_summary": diagnosis["diagnostic_summary"],
            "root_causes": diagnosis["root_causes"],
            "action_plan": diagnosis["action_plan"],
        }
