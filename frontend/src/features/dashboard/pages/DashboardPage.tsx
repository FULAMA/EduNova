import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'

import { ApiError } from '../../../shared/api/client'
import { formatMoney } from '../../../shared/utils/format'
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
import { getDirectionDashboard } from '../services/dashboard.service'
import type { DashboardMetric, DirectionDashboardData } from '../types/dashboard.types'

import './DashboardPage.css'

function messageForError(reason: unknown): string {
  if (reason instanceof ApiError && reason.status === 401) {
    return 'Votre session a expiré. Veuillez vous reconnecter.'
  }

  return 'Impossible de charger votre espace pour le moment.'
}

function roleLabel(role: string): string {
  if (role === 'ADMIN') return 'Administrateur'
  if (role === 'DIRECTION') return 'Direction'
  return role
}

function DashboardPage() {
  const session = getSession()
  const hasSession = session !== null

  const [user, setUser] = useState<AuthenticatedUser>()
  const [isLoadingUser, setIsLoadingUser] = useState(hasSession)
  const [userError, setUserError] = useState<string | null>(null)
  const [linkMessage, setLinkMessage] = useState<string | null>(null)
  const [linkPassword, setLinkPassword] = useState('')
  const [linkTotpCode, setLinkTotpCode] = useState('')

  // Metrics state from GET /dashboard/direction
  const [dashboardData, setDashboardData] = useState<DirectionDashboardData | null>(null)
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

  // Fetch real Direction Dashboard contract from API
  useEffect(() => {
    let active = true
    const currentSession = getSession()

    if (!currentSession) {
      return () => {
        active = false
      }
    }

    getDirectionDashboard()
      .then((data) => {
        if (!active) return
        setDashboardData(data)
        setMetricsStatus('success')
        setMetricsError(null)
      })
      .catch((reason: unknown) => {
        if (!active) return
        setMetricsStatus('error')
        if (reason instanceof ApiError && reason.status === 401) {
          setMetricsError('Session expirée lors du chargement des indicateurs.')
        } else {
          setMetricsError('Impossible de charger les indicateurs de pilotage de l’établissement.')
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

  async function handleGoogleLink(idToken: string, nonce: string) {
    setLinkMessage(null)
    if (!linkPassword) {
      setLinkMessage('Saisissez votre mot de passe EduNova pour confirmer la liaison.')
      return
    }
    if (user?.two_factor_enabled && !/^\d{6}$/.test(linkTotpCode)) {
      setLinkMessage('Saisissez votre code de vérification à deux facteurs.')
      return
    }
    try {
      await linkGoogleIdentity(idToken, nonce, linkPassword, linkTotpCode || undefined)
      setLinkMessage('Votre identité Google est maintenant liée à ce compte.')
    } catch (reason: unknown) {
      if (reason instanceof ApiError && reason.status === 409) {
        setLinkMessage('Cette identité Google est déjà liée à un autre compte.')
      } else if (reason instanceof ApiError && reason.status === 401) {
        setLinkMessage('La confirmation EduNova a échoué. Vérifiez le mot de passe et le code 2FA.')
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

  // Build stat cards from real direction dashboard contract
  const cards: DashboardMetric[] = []

  if (dashboardData) {
    cards.push({
      label: 'Élèves actifs',
      value: String(dashboardData.active_students),
      description: `${dashboardData.active_students} élève${dashboardData.active_students > 1 ? 's' : ''} actif${dashboardData.active_students > 1 ? 's' : ''} dans l’établissement`,
    })

    cards.push({
      label: 'Classes avec effectifs',
      value: String(dashboardData.headcount_by_class.length),
      description: `${dashboardData.headcount_by_class.length} classe${dashboardData.headcount_by_class.length > 1 ? 's' : ''} avec affectations actives`,
    })

    // Recovery rates per currency (USD & CDF separated per Decision 19 & 23)
    for (const rate of dashboardData.recovery_rates) {
      const remaining = dashboardData.remaining_amounts.find((r) => r.currency === rate.currency)
      const formattedRemaining = remaining ? formatMoney(String(remaining.amount), rate.currency) : ''
      cards.push({
        label: `Recouvrement (${rate.currency})`,
        value: rate.rate_percent !== null ? `${rate.rate_percent} %` : '—',
        description: remaining ? `Solde restant : ${formattedRemaining}` : 'Aucune obligation',
      })
    }

    // If no recovery rates exist yet, show a default monetary indicator
    if (dashboardData.recovery_rates.length === 0) {
      cards.push({
        label: 'Situation financière',
        value: 'À jour',
        description: 'Aucun frais ouvert enregistré pour le moment',
      })
    }
  }

  const isDirection = user?.role === 'DIRECTION'

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

          {/* Detailed breakdowns: Headcounts and Financials by Class */}
          {dashboardData ? (
            <section className="dashboard-page__grid-2" aria-label="Détails opérationnels">
              {/* Class Headcounts */}
              <div className="dashboard-page__panel">
                <h3 className="dashboard-page__panel-title">Effectifs par classe</h3>
                {dashboardData.headcount_by_class.length === 0 ? (
                  <p className="dashboard-page__empty-state">
                    Aucune classe avec élèves actifs pour le moment.
                  </p>
                ) : (
                  <div className="dashboard-page__table-scroll">
                    <table className="dashboard-page__table">
                      <thead>
                        <tr>
                          <th scope="col">Classe</th>
                          <th scope="col">Élèves actifs</th>
                        </tr>
                      </thead>
                      <tbody>
                        {dashboardData.headcount_by_class.map((item) => (
                          <tr key={item.class_id}>
                            <td>{item.class_name}</td>
                            <td>{item.active_students}</td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                )}
              </div>

              {/* Financial situation by class */}
              <div className="dashboard-page__panel">
                <h3 className="dashboard-page__panel-title">Situation financière par classe</h3>
                {dashboardData.financial_by_class.length === 0 ? (
                  <p className="dashboard-page__empty-state">
                    Aucune obligation financière enregistrée par classe.
                  </p>
                ) : (
                  <div className="dashboard-page__table-scroll">
                    <table className="dashboard-page__table">
                      <thead>
                        <tr>
                          <th scope="col">Classe</th>
                          <th scope="col">Attendu</th>
                          <th scope="col">Encaissé</th>
                          <th scope="col">Restant</th>
                        </tr>
                      </thead>
                      <tbody>
                        {dashboardData.financial_by_class.map((item) => (
                          <tr key={item.class_id}>
                            <td>{item.class_name}</td>
                            <td>
                              {item.expected.length > 0
                                ? item.expected.map((e) => formatMoney(String(e.amount), e.currency)).join(' / ')
                                : '0,00'}
                            </td>
                            <td>
                              {item.paid.length > 0
                                ? item.paid.map((p) => formatMoney(String(p.amount), p.currency)).join(' / ')
                                : '0,00'}
                            </td>
                            <td>
                              {item.remaining.length > 0
                                ? item.remaining.map((r) => formatMoney(String(r.amount), r.currency)).join(' / ')
                                : '0,00'}
                            </td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                )}
              </div>
            </section>
          ) : null}

          {/* Quick Access Navigation strictly tailored by role */}
          <section className="dashboard-page__section" aria-labelledby="dashboard-quicklinks-title">
            <h2 id="dashboard-quicklinks-title" className="dashboard-page__section-title">
              Accès rapides aux modules
            </h2>
            <div className="dashboard-page__quick-links">
              {/* Common modules for DIRECTION and ADMIN */}
              <Link to="/app/students" className="quick-link-card">
                <span className="quick-link-card__badge">Scolarité</span>
                <strong className="quick-link-card__title">Élèves & Dossiers</strong>
                <p className="quick-link-card__desc">
                  Consulter les élèves, fiches individuelles et parcours scolaires.
                </p>
              </Link>

              <Link to="/app/classes" className="quick-link-card">
                <span className="quick-link-card__badge">Structure</span>
                <strong className="quick-link-card__title">Classes & Effectifs</strong>
                <p className="quick-link-card__desc">
                  Consulter les classes et effectifs de votre établissement.
                </p>
              </Link>

              <Link to="/app/finance" className="quick-link-card">
                <span className="quick-link-card__badge">Finances</span>
                <strong className="quick-link-card__title">Situation financière</strong>
                <p className="quick-link-card__desc">
                  Consulter les frais, paiements, arriérés et reçus de caisse.
                </p>
              </Link>

              {/* ADMIN exclusive modules */}
              {!isDirection && (
                <>
                  <Link to="/app/enrollments" className="quick-link-card">
                    <span className="quick-link-card__badge">Inscriptions</span>
                    <strong className="quick-link-card__title">Années & Affectations</strong>
                    <p className="quick-link-card__desc">
                      Activer une année scolaire et gérer les inscriptions.
                    </p>
                  </Link>

                  <Link to="/app/academic-catalogues" className="quick-link-card">
                    <span className="quick-link-card__badge">Pédagogie</span>
                    <strong className="quick-link-card__title">Catalogues & Périodes</strong>
                    <p className="quick-link-card__desc">
                      Gérer les matières et périodes académiques de l’établissement.
                    </p>
                  </Link>

                  <Link to="/app/attendance" className="quick-link-card">
                    <span className="quick-link-card__badge">Suivi scolaire</span>
                    <strong className="quick-link-card__title">Présences & Risque</strong>
                    <p className="quick-link-card__desc">
                      Enregistrer les présences et évaluer le risque académique.
                    </p>
                  </Link>
                </>
              )}
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
              <p>Liaison de compte. Confirmez votre mot de passe EduNova
                {user.two_factor_enabled ? ' et votre code 2FA' : ''}.</p>
              <label>
                Mot de passe EduNova
                <input
                  type="password"
                  autoComplete="current-password"
                  value={linkPassword}
                  onChange={(event) => setLinkPassword(event.target.value)}
                />
              </label>
              {user.two_factor_enabled ? (
                <label>
                  Code 2FA
                  <input
                    inputMode="numeric"
                    autoComplete="one-time-code"
                    value={linkTotpCode}
                    onChange={(event) => setLinkTotpCode(event.target.value)}
                  />
                </label>
              ) : null}
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
