import { apiRequest } from '../../shared/api/client'

export type TeacherAssignment = {
  tenant_id: string
  teacher_user_id: string
  academic_class_id: string
  subject_id: string
  academic_year_id: string
  assigned_by: string
  assigned_at: string
}

export function getMyTeacherAssignments(): Promise<TeacherAssignment[]> {
  return apiRequest<TeacherAssignment[]>('/teacher/assignments', { authenticated: true })
}
