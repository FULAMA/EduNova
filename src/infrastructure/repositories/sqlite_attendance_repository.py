from datetime import date, datetime, timezone
from uuid import UUID

from src.academic.application.interfaces.attendance_repository import AttendanceRepository
from src.academic.domain.entities.attendance import Attendance, AttendanceStatus
from src.infrastructure.persistence.database import SQLiteDatabase


class SQLiteAttendanceRepository(AttendanceRepository):
    def __init__(self, database: SQLiteDatabase):
        self._database = database

    def record(self, attendance: Attendance) -> Attendance:
        with self._database.connect() as connection:
            connection.execute("BEGIN IMMEDIATE")
            connection.execute("""INSERT INTO attendance_records
                (id, tenant_id, student_id, academic_class_id, academic_year_id,
                 academic_period_id, attendance_date, status, justified, recorded_by, version)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 1)""", (
                str(attendance.id), str(attendance.tenant_id), str(attendance.student_id),
                str(attendance.academic_class_id), str(attendance.academic_year_id),
                str(attendance.academic_period_id), attendance.attendance_date.isoformat(),
                attendance.status.value, int(attendance.justified),
                str(attendance.recorded_by) if attendance.recorded_by else None,
            ))
            connection.execute("""INSERT INTO attendance_history
                (tenant_id, attendance_id, version, previous_status, previous_justified,
                 new_status, new_justified, changed_by, changed_at)
                VALUES (?, ?, 1, NULL, NULL, ?, ?, ?, ?)""", (
                str(attendance.tenant_id), str(attendance.id), attendance.status.value,
                int(attendance.justified), str(attendance.recorded_by),
                datetime.now(timezone.utc).isoformat(),
            ))
        return attendance

    def find_by_id(self, tenant_id: UUID, attendance_id: UUID) -> Attendance | None:
        with self._database.connect() as connection:
            row = connection.execute(
                "SELECT * FROM attendance_records WHERE tenant_id=? AND id=?",
                (str(tenant_id), str(attendance_id)),
            ).fetchone()
        return self._to_entity(row) if row else None

    def correct(self, attendance: Attendance, expected_version: int, changed_by: UUID) -> Attendance:
        with self._database.connect() as connection:
            connection.execute("BEGIN IMMEDIATE")
            previous = connection.execute("""SELECT id, status, justified FROM attendance_records
                WHERE tenant_id=? AND id=? AND version=?""", (str(attendance.tenant_id),
                str(attendance.id), expected_version)).fetchone()
            if previous is None:
                raise ValueError("Relevé introuvable ou déjà modifié. Rechargez les données avant de corriger.")
            cursor = connection.execute("""UPDATE attendance_records
                SET status=?, justified=?, version=version+1
                WHERE tenant_id=? AND id=? AND version=?""", (attendance.status.value,
                int(attendance.justified), str(attendance.tenant_id), str(attendance.id),
                expected_version))
            if cursor.rowcount != 1:
                raise ValueError("Relevé introuvable ou déjà modifié. Rechargez les données avant de corriger.")
            connection.execute("""INSERT INTO attendance_history
                (tenant_id, attendance_id, version, previous_status, previous_justified,
                 new_status, new_justified, changed_by, changed_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (str(attendance.tenant_id), previous["id"], expected_version + 1,
                 previous["status"], previous["justified"], attendance.status.value,
                 int(attendance.justified), str(changed_by),
                 datetime.now(timezone.utc).isoformat()))
            return attendance

    def list_by_class_date(self, tenant_id: UUID, academic_class_id: UUID,
                           academic_period_id: UUID, attendance_date: date) -> tuple[Attendance, ...]:
        with self._database.connect() as connection:
            rows = connection.execute("""SELECT * FROM attendance_records
                WHERE tenant_id=? AND academic_class_id=? AND academic_period_id=? AND attendance_date=?
                ORDER BY student_id""", (str(tenant_id), str(academic_class_id),
                str(academic_period_id), attendance_date.isoformat())).fetchall()
        return tuple(self._to_entity(row) for row in rows)

    def list_by_student_period(self, tenant_id: UUID, student_id: UUID,
                               academic_period_id: UUID) -> tuple[Attendance, ...]:
        with self._database.connect() as connection:
            rows = connection.execute("""SELECT * FROM attendance_records
                WHERE tenant_id=? AND student_id=? AND academic_period_id=?
                ORDER BY attendance_date, id""", (str(tenant_id), str(student_id),
                str(academic_period_id))).fetchall()
        return tuple(self._to_entity(row) for row in rows)

    def has_active_assignment(self, tenant_id: UUID, student_id: UUID,
                               academic_class_id: UUID, academic_year_id: UUID) -> bool:
        with self._database.connect() as connection:
            row = connection.execute("""SELECT 1 FROM student_assignments
                WHERE tenant_id=? AND student_id=? AND academic_class_id=?
                  AND academic_year_id=? AND status='ACTIVE' LIMIT 1""",
                (str(tenant_id), str(student_id), str(academic_class_id),
                 str(academic_year_id))).fetchone()
        return row is not None

    def list_active_roster(self, tenant_id: UUID, academic_class_id: UUID,
                           academic_year_id: UUID) -> tuple[tuple[UUID, str, str], ...]:
        with self._database.connect() as connection:
            rows = connection.execute("""SELECT s.id, s.first_name, s.last_name
                FROM student_assignments a JOIN students s
                  ON s.tenant_id=a.tenant_id AND s.id=a.student_id
                WHERE a.tenant_id=? AND a.academic_class_id=? AND a.academic_year_id=?
                  AND a.status='ACTIVE' AND s.active=1
                ORDER BY s.last_name, s.first_name, s.id""",
                (str(tenant_id), str(academic_class_id), str(academic_year_id))).fetchall()
        return tuple((UUID(row["id"]), row["first_name"], row["last_name"]) for row in rows)

    @staticmethod
    def _to_entity(row) -> Attendance:
        return Attendance(
            id=UUID(row["id"]), tenant_id=UUID(row["tenant_id"]),
            student_id=UUID(row["student_id"]), academic_class_id=UUID(row["academic_class_id"]),
            academic_year_id=UUID(row["academic_year_id"]),
            academic_period_id=UUID(row["academic_period_id"]),
            attendance_date=date.fromisoformat(row["attendance_date"]),
            status=AttendanceStatus(row["status"]), justified=bool(row["justified"]),
            recorded_by=UUID(row["recorded_by"]) if row["recorded_by"] else None,
            version=int(row["version"]),
        )
