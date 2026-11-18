import { apiRequest } from '../../../shared/api/client'
import type { DirectionDashboardData } from '../types/dashboard.types'

export async function getDirectionDashboard(): Promise<DirectionDashboardData> {
  return apiRequest<DirectionDashboardData>('/dashboard/direction', {
    authenticated: true,
  })
}
