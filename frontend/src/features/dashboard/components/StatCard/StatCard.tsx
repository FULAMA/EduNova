import type { DashboardMetric } from '../../types/dashboard.types'
import './StatCard.css'

type StatCardProps = {
  metric: DashboardMetric
}

export function StatCard({ metric }: StatCardProps) {
  return (
    <article className="stat-card">
      <p className="stat-card__label">{metric.label}</p>
      <strong className="stat-card__value">{metric.value}</strong>
      <p className="stat-card__description">{metric.description}</p>
    </article>
  )
}
