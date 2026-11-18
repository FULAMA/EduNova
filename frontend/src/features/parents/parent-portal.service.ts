import { apiRequest, apiRequestBlob } from '../../shared/api/client'

export type ParentChild = {
  student: {
    id: string
    first_name: string
    last_name: string
    email: string | null
    registration_number: string | null
    active: boolean
  }
  relationship_type: string
}

export type ParentReportCard = {
  id: string
  academic_period_id: string
  report_version: number
  status: 'ISSUED'
  issued_at: string | null
}

export function getParentChildren(): Promise<ParentChild[]> {
  return apiRequest<ParentChild[]>('/parent-portal/students', { authenticated: true })
}

export function getChildReportCards(studentId: string): Promise<ParentReportCard[]> {
  return apiRequest<ParentReportCard[]>(
    `/parent-portal/students/${encodeURIComponent(studentId)}/report-cards`,
    { authenticated: true },
  )
}

export function downloadChildReportCardPdf(
  studentId: string,
  reportCardId: string,
): Promise<Blob> {
  return apiRequestBlob(
    `/parent-portal/students/${encodeURIComponent(studentId)}/report-cards/${encodeURIComponent(reportCardId)}/pdf`,
    { authenticated: true },
  )
}
