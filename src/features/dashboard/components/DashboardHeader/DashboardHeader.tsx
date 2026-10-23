import './DashboardHeader.css'

type DashboardHeaderProps = {
  title?: string
  description?: string
}

export function DashboardHeader({
  title = 'Tableau de bord',
  description = "Vue d’ensemble de l’établissement.",
}: DashboardHeaderProps) {
  return (
    <header className="dashboard-header">
      <p className="dashboard-header__eyebrow">
        Administration
      </p>

      <h1 className="dashboard-header__title">
        {title}
      </h1>

      <p className="dashboard-header__description">
        {description}
      </p>
    </header>
  )
}
