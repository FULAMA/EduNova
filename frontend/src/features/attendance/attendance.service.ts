import { apiRequest } from '../../shared/api/client'

export type AttendanceStatistics = {
  total_sessions: number
  absences: number
  justified_absences: number
  unjustified_absences: number
  lates: number
  attendance_rate: number | null
}

export type AcademicRisk = {
  level: string
  score: number
  reasons: string[]
}

export type AttendanceStatus = 'PRESENT' | 'ABSENT' | 'LATE'

export type AttendanceInput = {
  student_id: string
  academic_class_id: string
  academic_year_id: string
  academic_period_id: string
  attendance_date: string
  status: AttendanceStatus
  justified?: boolean
}

export type AttendanceRecord = AttendanceInput & {
  id: string
  version: number
  recorded_by: string | null
}

export function getAttendanceStatistics(
  studentId: string,
  academicPeriodId: string,
): Promise<AttendanceStatistics> {
  return apiRequest(
    `/attendance/students/${encodeURIComponent(studentId)}/statistics?academic_period_id=${encodeURIComponent(academicPeriodId)}`,
    { authenticated: true },
  )
}

export function getStudentAcademicRisk(
  studentId: string,
  academicPeriodId: string,
): Promise<AcademicRisk> {
  return apiRequest(
    `/academic-risk/students/${encodeURIComponent(studentId)}/periods/${encodeURIComponent(academicPeriodId)}`,
    { authenticated: true },
  )
}

export function recordAttendance(payload: AttendanceInput) {
  return apiRequest('/attendance', {
    method: 'POST',
    authenticated: true,
    body: JSON.stringify(payload),
  })
}

export function listStudentAttendance(studentId: string, academicPeriodId: string): Promise<AttendanceRecord[]> {
  return apiRequest(
    `/attendance/students/${encodeURIComponent(studentId)}/records?academic_period_id=${encodeURIComponent(academicPeriodId)}`,
    { authenticated: true },
  )
}

export function correctAttendance(
  attendanceId: string,
  status: AttendanceStatus,
  justified: boolean,
  expectedVersion: number,
) {
  return apiRequest(`/attendance/${encodeURIComponent(attendanceId)}`, {
    method: 'PUT',
    authenticated: true,
    body: JSON.stringify({ status, justified, expected_version: expectedVersion }),
  })
}
