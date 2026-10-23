import { apiRequest } from '../../shared/api/client'

export type AcademicClass = {
  id: string
  name: string
  active: boolean
}

export type ClassSubject = {
  id: string
  academic_class_id: string
  subject_id: string
  coefficient: number
  academic_option_id: string | null
  active: boolean
}

export type AssignSubjectToClassInput = {
  subject_id: string
  coefficient: number
  academic_option_id?: string | null
}

export function listAcademicClasses(): Promise<AcademicClass[]> {
  return apiRequest('/classes', { authenticated: true })
}

export function assignSubjectToClass(
  classId: string,
  payload: AssignSubjectToClassInput,
): Promise<ClassSubject> {
  return apiRequest<ClassSubject>(`/classes/${encodeURIComponent(classId)}/subjects`, {
    method: 'POST',
    authenticated: true,
    body: JSON.stringify(payload),
  })
}
