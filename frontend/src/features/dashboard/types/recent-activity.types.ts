import type { DashboardResourceState } from './dashboard-resource.types'

export type RecentActivity = {
  id: string
  title: string
  description: string
  occurredAt: string
}

export type DashboardRecentActivities = {
  activities: RecentActivity[]
}

export type DashboardRecentActivitiesState =
  DashboardResourceState<DashboardRecentActivities>
