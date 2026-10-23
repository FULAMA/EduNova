import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'

import { ApiError } from '../../../shared/api/client'
import {
  getCurrentUser,
  getSession,
  linkGoogleIdentity,
  type AuthenticatedUser,
} from '../../auth/services/auth.service'
import { GoogleLoginButton } from '../../auth/components/GoogleLoginButton'
import { DashboardHeader } from '../components/DashboardHeader/DashboardHeader'
import { StatCard } from '../components/StatCard/StatCard'
import { DashboardResourceState } from '../components/DashboardResourceState/DashboardResourceState'
import { listStudents } from '../../students/services/student.service'
import { listAcademicClasses } from '../../classes/classes.service'
import { listAcademicYears, type AcademicYear } from '../../enrollments/enrollment.service'
import { listSubjects } from '../../academic-catalogues/academic-catalogue.service'
import type { DashboardMetric } from '../types/dashboard.types'

import './DashboardPage.css'

function messageForError(reason: unknown): string {
  if (reason instanceof ApiError && reason.status === 401) {
    return 'Votre session a expiré. Veuillez vous reconnecter.'
  }

  return 'Impossible de charger votre espace pour le moment.'
}

function roleLabel(role: string): string {
  return role === 'ADMIN' ? 'Administrateur' : role
}

type MetricsData = {
  totalStudents: number
  activeStudents: number
  totalClasses: number
  activeClasses: number
  activeSubjects: number
  activeYear: AcademicYear | null
}

function DashboardPage() {
  const session = getSession()
  const hasSession = session !== null

  const [user, setUser] = useState<AuthenticatedUser>()
  const [isLoadingUser, setIsLoadingUser] = useState(hasSession)
  const [userError, setUserError] = useState<string | null>(null)
  const [linkMessage, setLinkMessage] = useState<string | null>(null)

  // Metrics state
  const [metrics, setMetrics] = useState<MetricsData | null>(null)
  const [metricsStatus, setMetricsStatus] = useState<'loading' | 'success' | 'error'>(
    hasSession ? 'loading' : 'error',
  )
  const [metricsError, setMetricsError] = useState<string | null>(
    hasSession ? null : 'Session requise pour charger les indicateurs.',
  )

  const [requestVersion, setRequestVersion] = useState(0)

  // Fetch session / user
  useEffect(() => {
    let active = true
    const currentSession = getSession()

    if (!currentSession) {
      return () => {
        active = false
      }
    }

    void getCurrentUser(currentSession.accessToken)
      .then((currentUser) => {
        if (active) {
          setUser(currentUser)
          setUserError(null)
        }
      })
      .catch((reason: unknown) => {
        if (active) setUserError(messageForError(reason))
      })
      .finally(() => {
        if (active) setIsLoadingUser(false)
      })

    return () => {
      active = false
    }
  }, [requestVersion])

  // Fetch business metrics in parallel without blocking user session
  useEffect(() => {
    let active = true
    const currentSession = getSession()

    if (!currentSession) {
      return () => {
        active = false
      }
    }

    Promise.all([
      listStudents(),
      listAcademicClasses(),
      listAcademicYears(),
      listSubjects(),
    ])
      .then(([students, classes, years, subjects]) => {
        if (!active) return

        const totalStudents = students.length
        const activeStudents = students.filter((s) => s.status === 'active').length

        const totalClasses = classes.length
        const activeClasses = classes.filter((c) => c.active).length

        const activeSubjects = subjects.filter((s) => s.active).length

        // Strictly verify active year: status === 'ACTIVE'
        const activeYear = years.find((y) => y.status === 'ACTIVE') ?? null

        setMetrics({
          totalStudents,
          activeStudents,
          totalClasses,
          activeClasses,
          activeSubjects,
          activeYear,
        })
        setMetricsStatus('success')
      })
      .catch((reason: unknown) => {
        if (!active) return
        setMetricsStatus('error')
        if (reason instanceof ApiError && reason.status === 401) {
          setMetricsError('Session expirée lors du chargement des indicateurs.')
        } else {
          setMetricsError('Impossible de charger les indicateurs de pilotage.')
        }
      })

    return () => {
      active = false
    }
  }, [requestVersion])

  const effectiveLoading = hasSession && isLoadingUser
  const effectiveError =
    userError ??
    (!hasSession
      ? 'Votre session est indisponible. Veuillez vous reconnecter.'
      : null)

  async function handleGoogleLink(idToken: string) {
    setLinkMessage(null)
    try {
      await linkGoogleIdentity(idToken)
      setLinkMessage('Votre identité Google est maintenant liée à ce compte.')
    } catch (reason: unknown) {
      if (reason instanceof ApiError && reason.status === 409) {
        setLinkMessage('Cette identité Google est déjà liée à un autre compte.')
      } else {
        setLinkMessage('La liaison Google n’a pas pu être effectuée.')
      }
    }
  }

  function retryAll() {
    setIsLoadingUser(true)
    setMetricsStatus('loading')
    setMetricsError(null)
    setRequestVersion((v) => v + 1)
  }

  // Build stat cards from real metrics
  const cards: DashboardMetric[] = metrics
    ? [
        {
          label: 'Élèves inscrits',
          value: metrics.totalStudents.toString(),
          description: `${metrics.activeStudents} actif${metrics.activeStudents > 1 ? 's' : ''} sur ${metrics.totalStudents}`,
        },
        {
          label: 'Classes pédagogiques',
          value: metrics.activeClasses.toString(),
          description: `${metrics.totalClasses} classe${metrics.totalClasses > 1 ? 's' : ''} configurée${metrics.totalClasses > 1 ? 's' : ''}`,
        },
        {
          label: 'Matières enseignées',
          value: metrics.activeSubjects.toString(),
          description: 'Catalogue actif de l’établissement',
        },
        {
          label: 'Année scolaire active',
          value: metrics.activeYear ? metrics.activeYear.label : 'Aucune active',
          description: metrics.activeYear
            ? `Du ${metrics.activeYear.start_date} au ${metrics.activeYear.end_date}`
            : 'Aucune année avec le statut ACTIVE',
        },
      ]
    : []

  return (
    <section className="dashboard-page">
      <DashboardHeader
        title="Tableau de bord de pilotage"
        description="Indicateurs de gestion et pilotage opérationnel de votre établissement scolaire."
      />

      {effectiveLoading ? (
        <div className="dashboard-page__account" role="status" aria-busy="true">
          Chargement de votre session...
        </div>
      ) : effectiveError ? (
        <div className="dashboard-page__account dashboard-page__account--error" role="alert">
          <strong>Espace indisponible</strong>
          <p>{effectiveError}</p>
          <button
            type="button"
            className="dashboard-page__retry"
            onClick={retryAll}
          >
            Réessayer
          </button>
        </div>
      ) : user ? (
        <>
          {/* Active Academic Year Status Alert if None Active */}
          {metrics && !metrics.activeYear && (
            <div className="dashboard-page__banner dashboard-page__banner--warning" role="status">
              <div className="dashboard-page__banner-content">
                <strong>Attention : aucune année scolaire n’est actuellement active.</strong>
                <p>
                  Les affectations d’élèves et saisies académiques nécessitent une année scolaire active.
                </p>
              </div>
              <Link to="/app/enrollments" className="dashboard-page__banner-action">
                Gérer les années scolaires &rarr;
              </Link>
            </div>
          )}

          {/* Business KPI Metrics Grid */}
          <section className="dashboard-page__section" aria-labelledby="dashboard-metrics-title">
            <h2 id="dashboard-metrics-title" className="dashboard-page__section-title">
              Indicateurs clés
            </h2>

            <DashboardResourceState
              status={metricsStatus === 'loading' ? 'loading' : metricsStatus === 'error' ? 'error' : 'success'}
              error={metricsError}
              loadingLabel="Chargement des indicateurs réels de l’établissement…"
              errorTitle="Indicateurs indisponibles"
              onRetry={retryAll}
            >
              <div className="dashboard-page__metrics" data-testid="dashboard-metrics-grid">
                {cards.map((metric) => (
                  <StatCard key={metric.label} metric={metric} />
                ))}
              </div>
            </DashboardResourceState>
          </section>

          {/* Quick Access Navigation */}
          <section className="dashboard-page__section" aria-labelledby="dashboard-quicklinks-title">
            <h2 id="dashboard-quicklinks-title" className="dashboard-page__section-title">
              Accès rapides aux modules
            </h2>
            <div className="dashboard-page__quick-links">
              <Link to="/app/enrollments" className="quick-link-card">
                <span className="quick-link-card__badge">Années & Affectations</span>
                <strong className="quick-link-card__title">Inscriptions</strong>
                <p className="quick-link-card__desc">
                  Activer une année scolaire, inscrire des élèves et gérer le cycle de vie des affectations.
                </p>
              </Link>

              <Link to="/app/classes" className="quick-link-card">
                <span className="quick-link-card__badge">Structure scolaire</span>
                <strong className="quick-link-card__title">Classes & Matières</strong>
                <p className="quick-link-card__desc">
                  Consulter les promotions, associer les matières et définir les coefficients.
                </p>
              </Link>

              <Link to="/app/students" className="quick-link-card">
                <span className="quick-link-card__badge">Scolarité</span>
                <strong className="quick-link-card__title">Élèves & Dossiers</strong>
                <p className="quick-link-card__desc">
                  Accéder à la liste des élèves, fiches individuelles et parcours académiques.
                </p>
              </Link>

              <Link to="/app/academic-catalogues" className="quick-link-card">
                <span className="quick-link-card__badge">Pédagogie</span>
                <strong className="quick-link-card__title">Catalogue & Périodes</strong>
                <p className="quick-link-card__desc">
                  Définir les matières au niveau établissement et consulter les périodes académiques.
                </p>
              </Link>

              <Link to="/app/attendance" className="quick-link-card">
                <span className="quick-link-card__badge">Suivi scolaire</span>
                <strong className="quick-link-card__title">Présences & Risque</strong>
                <p className="quick-link-card__desc">
                  Enregistrer les présences et suivre le risque académique calculé par l API.
                </p>
              </Link>
            </div>
          </section>

          {/* User Session and Security Account Block */}
          <section className="dashboard-page__account" aria-labelledby="dashboard-account-title">
            <div>
              <p className="dashboard-page__eyebrow">Session active</p>
              <h2 id="dashboard-account-title">{roleLabel(user.role)}</h2>
              <p>{user.email}</p>
            </div>
            <dl className="dashboard-page__account-facts">
              <div>
                <dt>Compte</dt>
                <dd>{user.is_active ? 'Actif' : 'Inactif'}</dd>
              </div>
              <div>
                <dt>Deux facteurs</dt>
                <dd>{user.two_factor_enabled ? 'Activés' : 'Non activés'}</dd>
              </div>
            </dl>
            <div className="dashboard-page__google-link">
              <p>Liaison de compte</p>
              <GoogleLoginButton onCredential={handleGoogleLink} />
              {linkMessage ? <p role="status">{linkMessage}</p> : null}
            </div>
          </section>
        </>
      ) : null}
    </section>
  )
}

export default DashboardPage
