import type { DashboardSummaryState } from '../types/dashboard.types'
import type { DashboardRecentActivitiesState } from '../types/recent-activity.types'

import { demoDashboardSummary } from './dashboard-summary.data'
import { demoRecentActivities } from './recent-activities.data'

export const demoDashboardSummaryState: DashboardSummaryState = {
  status: 'success',
  data: demoDashboardSummary,
  error: null,
}

export const demoDashboardRecentActivitiesState:
  DashboardRecentActivitiesState = {
    status: 'success',
    data: demoRecentActivities,
    error: null,
  }
