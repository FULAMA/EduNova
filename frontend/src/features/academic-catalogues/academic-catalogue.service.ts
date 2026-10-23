import { apiRequest } from '../../shared/api/client'

export type Subject = { id: string; name: string; code: string; coefficient: number; active: boolean }
export type SubjectInput = Omit<Subject, 'id' | 'active'>
export type SubjectUpdateInput = Pick<Subject, 'name' | 'code'>
export type AcademicPeriod = { id: string; name: string; start_date: string; end_date: string; academic_year_id?: string | null }
export type AcademicPeriodInput = Pick<AcademicPeriod, 'name' | 'start_date' | 'end_date'> & { academic_year_id: string }

export function listSubjects(search = ''): Promise<Subject[]> {
  const query = search.trim() ? `?search=${encodeURIComponent(search.trim())}` : ''
  return apiRequest(`/academic-catalogues/subjects${query}`, { authenticated: true })
}

export function createSubject(data: SubjectInput): Promise<Subject> {
  return apiRequest('/academic-catalogues/subjects', {
    method: 'POST', body: JSON.stringify(data), authenticated: true,
  })
}

export function updateSubject(id: string, data: SubjectUpdateInput): Promise<Subject> {
  return apiRequest(`/academic-catalogues/subjects/${encodeURIComponent(id)}`, {
    method: 'PUT', body: JSON.stringify(data), authenticated: true,
  })
}

export function listAcademicPeriods(): Promise<AcademicPeriod[]> {
  return apiRequest('/academic-catalogues/periods', { authenticated: true })
}

export function createAcademicPeriod(data: AcademicPeriodInput): Promise<AcademicPeriod> {
  return apiRequest('/academic-catalogues/periods', {
    method: 'POST', authenticated: true, body: JSON.stringify(data),
  })
}
