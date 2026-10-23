import { apiRequest, apiRequestBlob } from '../../../shared/api/client'

export type StudentAcademicPeriod = {
  id: string
  name: string | null
}

export type StudentAcademicRecord = {
  student_id: string
  academic_period_id: string
  general_average: number
  failed_subjects: number
  credits_obtained: number
  total_credits: number
  subject_results: Array<{
    subject_id: string
    subject_name: string | null
    average: number
    coefficient: number
  }>
  status: string
  version: number
  academic_period_name: string | null
}

export type StudentPortalProfile = {
  student: {
    id: string
    first_name: string
    last_name: string
    email: string | null
    active: boolean
  }
  assignment: {
    id: string
    academic_year_id: string
    academic_class_id: string
    status: 'ACTIVE'
    created_at: string
  } | null
  academic_year: {
    id: string
    label: string
    start_date: string
    end_date: string
    status: string
  } | null
}

export type StudentAttendance = {
  id: string
  student_id: string
  academic_class_id: string
  academic_year_id: string
  academic_period_id: string
  attendance_date: string
  status: 'PRESENT' | 'ABSENT' | 'LATE'
  justified: boolean
  recorded_by: string | null
  version: number
}

export type StudentAttendanceResponse = {
  records: StudentAttendance[]
  statistics: {
    total_sessions: number
    absences: number
    justified_absences: number
    unjustified_absences: number
    lates: number
    attendance_rate: number | null
  }
}

export type StudentReportCard = {
  id: string
  student_id: string
  academic_period_id: string
  deliberation_id: string
  deliberation_version: number
  record_version: number
  report_version: number
  status: 'ISSUED'
  snapshot: Record<string, unknown>
  snapshot_hash: string
  created_at: string | null
  issued_at: string | null
}

export function getMyStudentProfile(): Promise<StudentPortalProfile> {
  return apiRequest<StudentPortalProfile>('/me/student', { authenticated: true })
}

export function getMyAcademicPeriods(): Promise<StudentAcademicPeriod[]> {
  return apiRequest<StudentAcademicPeriod[]>('/me/student/academic-periods', { authenticated: true })
}

export function getMyAcademicRecord(periodId: string): Promise<StudentAcademicRecord> {
  return apiRequest<StudentAcademicRecord>(
    `/me/student/academic-records/${encodeURIComponent(periodId)}`,
    { authenticated: true },
  )
}

export function getMyAttendance(periodId: string): Promise<StudentAttendanceResponse> {
  return apiRequest<StudentAttendanceResponse>(
    `/me/student/attendance/${encodeURIComponent(periodId)}`,
    { authenticated: true },
  )
}

export function getMyReportCards(): Promise<StudentReportCard[]> {
  return apiRequest<StudentReportCard[]>('/report-cards', { authenticated: true })
}

export function downloadMyReportCardPdf(reportCardId: string): Promise<Blob> {
  return apiRequestBlob(`/report-cards/${encodeURIComponent(reportCardId)}/pdf`, { authenticated: true })
}

