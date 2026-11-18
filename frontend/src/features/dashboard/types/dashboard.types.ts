import type { DashboardResourceState } from './dashboard-resource.types'

export type Currency = 'USD' | 'CDF'

export type CurrencyAmount = {
  currency: Currency
  amount: string | number
}

export type RecoveryRate = {
  currency: Currency
  rate_percent: string | number | null
}

export type ClassHeadcount = {
  class_id: string
  class_name: string
  active_students: number
}

export type ClassFinancialSituation = {
  class_id: string
  class_name: string
  expected: CurrencyAmount[]
  paid: CurrencyAmount[]
  remaining: CurrencyAmount[]
}

export type DirectionDashboardData = {
  active_students: number
  headcount_by_class: ClassHeadcount[]
  expected_amounts: CurrencyAmount[]
  paid_amounts: CurrencyAmount[]
  remaining_amounts: CurrencyAmount[]
  recovery_rates: RecoveryRate[]
  financial_by_class: ClassFinancialSituation[]
}

export type DashboardMetric = {
  label: string
  value: string
  description: string
}

export type DashboardSummary = {
  students: DashboardMetric
  classes: DashboardMetric
  teachers: DashboardMetric
  attendance: DashboardMetric
}

export type DashboardSummaryState =
  DashboardResourceState<DashboardSummary>
