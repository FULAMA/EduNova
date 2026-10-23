import { apiRequest } from '../../../shared/api/client'
import type { Student } from '../types/student.types'
import type { AcademicRecord, AcademicPeriod, AcademicPeriodId, AcademicRecordHistory, Deliberation, EligibleSubject } from '../types/student-detail.types'

type StudentSummaryResponse = {
  id: string
  first_name: string
  last_name: string
  email: string | null
  active: boolean
}

export type EligibleAcademicPeriod = {
  id: string
  name: string
  academic_year_id: string
  academic_year_label: string
  has_record?: boolean
}

export type { EligibleSubject }

function toStudent(student: StudentSummaryResponse): Student {
  return {
    id: student.id,
    firstName: student.first_name,
    lastName: student.last_name,
    email: student.email,
    status: student.active ? 'active' : 'inactive',
  }
}

export async function listStudents(): Promise<Student[]> {
  const students = await apiRequest<StudentSummaryResponse[]>('/students', {
    authenticated: true,
  })

  return students.map(toStudent)
}

export async function getStudent(studentId: string): Promise<Student> {
  const student = await apiRequest<StudentSummaryResponse>(
    `/students/${encodeURIComponent(studentId)}`,
    { authenticated: true },
  )

  return toStudent(student)
}

export async function listStudentAcademicPeriods(studentId: string): Promise<AcademicPeriod[]> {
  return apiRequest<AcademicPeriod[]>(
    `/academic-records/students/${encodeURIComponent(studentId)}/periods`,
    { authenticated: true },
  )
}

export function listEligibleStudentPeriods(studentId: string): Promise<EligibleAcademicPeriod[]> {
  return apiRequest(`/academic-records/students/${encodeURIComponent(studentId)}/available-periods`, {
    authenticated: true,
  })
}

export function listEligibleStudentSubjects(studentId: string, periodId: string): Promise<EligibleSubject[]> {
  return apiRequest(`/academic-records/students/${encodeURIComponent(studentId)}/periods/${encodeURIComponent(periodId)}/subjects`, {
    authenticated: true,
  })
}

export function createStudentAcademicRecord(studentId: string, periodId: string, totalCredits: number) {
  return apiRequest('/academic-records', {
    method: 'POST', authenticated: true,
    body: JSON.stringify({ student_id: studentId, academic_period_id: periodId, total_credits: totalCredits }),
  })
}

export function addStudentSubjectResult(studentId: string, periodId: string, subjectId: string, average: number) {
  return apiRequest(`/academic-records/${encodeURIComponent(studentId)}/${encodeURIComponent(periodId)}/subjects`, {
    method: 'POST', authenticated: true,
    body: JSON.stringify({ subject_id: subjectId, average }),
  })
}

export async function getStudentAcademicRecord(
  studentId: string,
  academicPeriodId: AcademicPeriodId,
): Promise<AcademicRecord> {
  return apiRequest<AcademicRecord>(
    `/academic-records/${encodeURIComponent(studentId)}/${encodeURIComponent(academicPeriodId)}`,
    { authenticated: true },
  )
}

export function getStudentDeliberation(studentId: string, academicPeriodId: AcademicPeriodId): Promise<Deliberation> {
  return apiRequest<Deliberation>(
    `/academic-records/${encodeURIComponent(studentId)}/${encodeURIComponent(academicPeriodId)}/deliberation`,
    { authenticated: true },
  )
}

export function validateStudentDeliberation(
  deliberationId: string,
  expectedVersion: number,
): Promise<Deliberation> {
  return apiRequest<Deliberation>(
    '/academic-records/deliberations/' + encodeURIComponent(deliberationId) + '/validate',
    {
      method: 'POST',
      authenticated: true,
      body: JSON.stringify({ expected_version: expectedVersion }),
    },
  )
}

export function getStudentAcademicHistory(studentId: string, academicPeriodId: AcademicPeriodId): Promise<AcademicRecordHistory[]> {
  return apiRequest<AcademicRecordHistory[]>(
    `/academic-records/${encodeURIComponent(studentId)}/${encodeURIComponent(academicPeriodId)}/history`,
    { authenticated: true },
  )
}

export async function validateStudentAcademicRecord(
  studentId: string,
  academicPeriodId: AcademicPeriodId,
  expectedVersion: number,
): Promise<AcademicRecord> {
  return apiRequest<AcademicRecord>(
    `/academic-records/${encodeURIComponent(studentId)}/${encodeURIComponent(academicPeriodId)}/validate`,
    { method: 'POST', authenticated: true, body: JSON.stringify({ expected_version: expectedVersion }) },
  )
}

export async function correctStudentAcademicRecord(
  studentId: string,
  academicPeriodId: AcademicPeriodId,
  payload: Pick<AcademicRecord, 'general_average' | 'failed_subjects' | 'credits_obtained'> & { expected_version: number; reason: string },
): Promise<AcademicRecord> {
  return apiRequest<AcademicRecord>(
    `/academic-records/${encodeURIComponent(studentId)}/${encodeURIComponent(academicPeriodId)}/correct`,
    { method: 'POST', authenticated: true, body: JSON.stringify(payload) },
  )
}
