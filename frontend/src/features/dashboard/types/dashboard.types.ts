import type { DashboardResourceState } from './dashboard-resource.types'

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
