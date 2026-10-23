import type { ReactNode } from 'react'

import type { DashboardResourceStatus } from '../../types/dashboard-resource.types'

import './DashboardResourceState.css'

type DashboardResourceStateProps = {
  status: DashboardResourceStatus
  error?: string | null
  loadingLabel?: string
  emptyLabel?: string
  errorTitle?: string
  onRetry?: () => void
  children?: ReactNode
}

export function DashboardResourceState({
  status,
  error,
  loadingLabel = 'Chargement des données…',
  emptyLabel = 'Aucune donnée disponible.',
  errorTitle = 'Impossible de charger les données.',
  onRetry,
  children,
}: DashboardResourceStateProps) {
  if (status === 'loading') {
    return (
      <div
        className="dashboard-resource-state"
        role="status"
        aria-live="polite"
      >
        <div
          className="dashboard-resource-state__skeleton"
          aria-hidden="true"
        />

        <p className="dashboard-resource-state__message">
          {loadingLabel}
        </p>
      </div>
    )
  }

  if (status === 'empty') {
    return (
      <div className="dashboard-resource-state dashboard-resource-state--empty">
        <p className="dashboard-resource-state__message">
          {emptyLabel}
        </p>
      </div>
    )
  }

  if (status === 'error') {
    return (
      <div
        className="dashboard-resource-state dashboard-resource-state--error"
        role="alert"
      >
        <strong className="dashboard-resource-state__title">
          {errorTitle}
        </strong>

        {error ? (
          <p className="dashboard-resource-state__message">
            {error}
          </p>
        ) : null}

        {onRetry ? (
          <button
            type="button"
            className="dashboard-resource-state__retry"
            onClick={onRetry}
          >
            Réessayer
          </button>
        ) : null}
      </div>
    )
  }

  return <>{children}</>
}

