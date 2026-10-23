import { apiRequest } from '../../shared/api/client'

export type AcademicYear = {
  id: string
  label: string
  start_date: string
  end_date: string
  status: 'DRAFT' | 'ACTIVE' | 'CLOSED'
}

export type StudentAssignment = {
  id: string
  student_id: string
  academic_year_id: string
  academic_class_id: string
  academic_option_id: string | null
  status: 'DRAFT' | 'ACTIVE' | 'CLOSED' | 'CANCELLED'
}

export function listAcademicYears(): Promise<AcademicYear[]> {
  return apiRequest('/academic-years', { authenticated: true })
}

export function createAcademicYear(payload: Pick<AcademicYear, 'label' | 'start_date' | 'end_date'>) {
  return apiRequest<AcademicYear>('/academic-years', {
    method: 'POST',
    authenticated: true,
    body: JSON.stringify(payload),
  })
}

export function activateAcademicYear(yearId: string) {
  return apiRequest<AcademicYear>(`/academic-years/${encodeURIComponent(yearId)}/activate`, {
    method: 'POST',
    authenticated: true,
  })
}

export function listStudentAssignments(studentId: string): Promise<StudentAssignment[]> {
  return apiRequest(`/student-assignments?student_id=${encodeURIComponent(studentId)}`, {
    authenticated: true,
  })
}

export function createStudentAssignment(payload: Omit<StudentAssignment, 'id' | 'status' | 'academic_option_id'> & { academic_option_id?: string }) {
  return apiRequest<StudentAssignment>('/student-assignments', {
    method: 'POST',
    authenticated: true,
    body: JSON.stringify(payload),
  })
}

export function changeStudentAssignmentStatus(assignmentId: string, action: 'activate' | 'cancel' | 'close') {
  return apiRequest<StudentAssignment>(`/student-assignments/${encodeURIComponent(assignmentId)}/${action}`, {
    method: 'POST',
    authenticated: true,
  })
}

export function promoteStudent(payload: {
  source_assignment_id: string
  deliberation_id: string
  target_year_id: string
  target_class_id: string
}): Promise<StudentAssignment> {
  return apiRequest<StudentAssignment>('/student-assignments/promote', {
    method: 'POST',
    authenticated: true,
    body: JSON.stringify(payload),
  })
}
