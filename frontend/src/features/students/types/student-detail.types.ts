export type StudentDetail = import('./student.types').Student
export type AcademicPeriod = { id: string; name: string | null; academic_year_id?: string; academic_year_label?: string; has_record?: boolean }
export type EligibleSubject = { id: string; name: string; coefficient: number }
export type AcademicPeriodId = string

export type SubjectResult = {
  subject_id: string
  subject_name?: string | null
  average: number
  coefficient: number
}

export type AcademicRecord = {
  student_id: string
  academic_period_id: AcademicPeriodId
  academic_period_name?: string | null
  general_average: number
  failed_subjects: number
  credits_obtained: number
  total_credits: number
  subject_results: SubjectResult[]
  status: 'DRAFT' | 'VALIDATED'
  version: number
}

export type Deliberation = {
  student_id: string
  academic_period_id: string
  record_version: number
  average: number
  failed_subjects: number
  decision: 'ADMITTED' | 'CONDITIONAL' | 'FAILED'
  deliberation_id?: string
  deliberation_status?: 'PREPARED' | 'VALIDATED' | 'SUPERSEDED'
  deliberation_version?: number
}

export type AcademicRecordHistory = {
  version: number
  status: 'DRAFT' | 'VALIDATED'
  operation: string
  recorded_at: string
  actor_id?: string | null
  reason?: string | null
  snapshot: Record<string, unknown>
}
