import { apiRequest } from '../../shared/api/client'

export type ReportCardAIFeedback = {
  report_card_id: string
  student_name: string
  encouraging: string
  analytical: string
  demanding: string
}

export type StudentRiskAIDiagnosis = {
  student_id: string
  student_name: string
  academic_period_id: string
  risk_level: string
  risk_score: number
  diagnostic_summary: string
  root_causes: string[]
  action_plan: string[]
}

export type ParentPortalAISummary = {
  student_id: string
  report_card_id: string
  period_name: string
  headline: string
  summary: string
  tips_for_home: string[]
}

export function getReportCardAIFeedback(reportCardId: string): Promise<ReportCardAIFeedback> {
  return apiRequest<ReportCardAIFeedback>(
    `/ai/report-cards/${encodeURIComponent(reportCardId)}/feedback`,
    {
      method: 'POST',
      authenticated: true,
    },
  )
}

export function getStudentRiskAIDiagnosis(
  studentId: string,
  academicPeriodId: string,
): Promise<StudentRiskAIDiagnosis> {
  return apiRequest<StudentRiskAIDiagnosis>(
    `/ai/students/${encodeURIComponent(studentId)}/risk-diagnosis?academic_period_id=${encodeURIComponent(academicPeriodId)}`,
    {
      method: 'POST',
      authenticated: true,
    },
  )
}

export function getParentPortalAISummary(
  studentId: string,
  reportCardId: string,
): Promise<ParentPortalAISummary> {
  return apiRequest<ParentPortalAISummary>(
    `/parent-portal/students/${encodeURIComponent(studentId)}/report-cards/${encodeURIComponent(reportCardId)}/ai-summary`,
    {
      method: 'GET',
      authenticated: true,
    },
  )
}
