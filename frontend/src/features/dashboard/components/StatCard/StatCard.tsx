import type { DashboardMetric } from '../../types/dashboard.types'
import './StatCard.css'

type StatCardProps = {
  metric: DashboardMetric
}

export function StatCard({ metric }: StatCardProps) {
  return (
    <article className="stat-card">
      <div className="stat-card__header">
        <span className="stat-card__label">{metric.label}</span>
      </div>
      <strong className="stat-card__value">{metric.value}</strong>
      <p className="stat-card__description">{metric.description}</p>
    </article>
  )
}

export default StatCard
