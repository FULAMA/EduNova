import type { FormEvent } from 'react'
import { useState, useEffect } from 'react'
import { useNavigate, useLocation } from 'react-router-dom'
import { selectTenant, type LoginResponse, type TenantOption } from '../services/auth.service'
import { saveSession } from '../services/auth.storage'
import { describeAuthError } from '../../../shared/api/client.errors'

/**
 * TenantSelectionPage - Page de sélection d'établissement
 * 
 * Cette page est affichée après une authentification réussie
 * lorsque l'utilisateur a accès à plusieurs tenants.
 * 
 * Elle permet de sélectionner un établissement parmi ceux disponibles,
 * puis appelle POST /auth/select-tenant pour obtenir les tokens ordinaires.
 */
export default function TenantSelectionPage() {
  const navigate = useNavigate()
  const location = useLocation()
  
  // Récupérer les données passées depuis LoginPage
  const state = location.state as {
    email?: string
    tenantSelectionToken?: string
    availableTenants?: TenantOption[]
  } | null

  const [isSubmitting, setIsSubmitting] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [selectedTenantId, setSelectedTenantId] = useState<string | null>(null)

  // Données par défaut si pas de state
  const tenantSelectionToken = state?.tenantSelectionToken || ''
  const availableTenants = state?.availableTenants || []
  const email = state?.email || ''

  // Redirection si pas de données nécessaires
  useEffect(() => {
    if (!tenantSelectionToken || availableTenants.length === 0) {
      navigate('/login', { replace: true })
    }
  }, [tenantSelectionToken, availableTenants.length, navigate])

  if (!tenantSelectionToken || availableTenants.length === 0) {
    return null
  }

  // Sélection automatique si un seul tenant
  if (availableTenants.length === 1 && !selectedTenantId) {
    setSelectedTenantId(availableTenants[0].tenant_id)
  }

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault()
    setError(null)

    if (!selectedTenantId) {
      setError('Veuillez sélectionner un établissement')
      return
    }

    setIsSubmitting(true)

    try {
      const response: LoginResponse = await selectTenant({
        tenant_selection_token: tenantSelectionToken,
        tenant_id: selectedTenantId,
      })

      // Si on obtient directement des tokens ordinaires
      if (response.access_token && response.refresh_token) {
        saveSession({
          accessToken: response.access_token,
          refreshToken: response.refresh_token,
          email: response.email || email,
          tenantId: selectedTenantId,
        })
        navigate('/')
        return
      }

      // Si 2FA est requis après sélection du tenant
      if (response.two_factor_required && response.two_factor_token) {
        navigate('/login/2fa', {
          state: {
            email: response.email || email,
            twoFactorToken: response.two_factor_token,
            tenantSelectionToken: null,
          },
          replace: true,
        })
        return
      }

      // Si une nouvelle sélection de tenant est requise (cas edge)
      if (response.tenant_selection_required && response.tenant_selection_token && response.available_tenants) {
        navigate('/login/select-tenant', {
          state: {
            email: response.email || email,
            tenantSelectionToken: response.tenant_selection_token,
            availableTenants: response.available_tenants,
          },
          replace: true,
        })
        return
      }

      // Cas par défaut : redirection vers login
      navigate('/login', { replace: true })

    } catch (err) {
      const error = describeAuthError(err)
      setError(error.message)
      
      // Si le token de sélection a expiré ou été consommé
      if (error.message.includes('Jeton de selection') || error.message.includes('consomme')) {
        setError('Votre session de sélection a expiré. Veuillez vous reconnecter.')
        setTimeout(() => {
          navigate('/login', { replace: true })
        }, 3000)
      }
    } finally {
      setIsSubmitting(false)
    }
  }

  return (
    <main className="tenant-selection-page">
      <div className="tenant-selection-page__container">
        <div className="tenant-selection-page__card">
          <h1 className="tenant-selection-page__title">
            Sélectionner un établissement
          </h1>
          
          <p className="tenant-selection-page__description">
            Vous êtes connecté en tant que <strong>{email}</strong>.
            <br />
            Veuillez choisir l'établissement que vous souhaitez gérer.
          </p>

          {error && (
            <div className="tenant-selection-page__error">
              {error}
            </div>
          )}

          <form onSubmit={handleSubmit} className="tenant-selection-page__form">
            <fieldset className="tenant-selection-page__fieldset">
              <legend className="tenant-selection-page__legend">
                Établissements disponibles
              </legend>
              
              <div className="tenant-selection-page__tenants">
                {availableTenants.map((tenant) => (
                  <label
                    key={tenant.tenant_id}
                    className={`tenant-selection-page__tenant ${selectedTenantId === tenant.tenant_id ? 'tenant-selection-page__tenant--selected' : ''}`}
                  >
                    <input
                      type="radio"
                      name="tenant_id"
                      value={tenant.tenant_id}
                      checked={selectedTenantId === tenant.tenant_id}
                      onChange={() => setSelectedTenantId(tenant.tenant_id)}
                      className="tenant-selection-page__tenant-radio"
                      disabled={isSubmitting}
                    />
                    <div className="tenant-selection-page__tenant-info">
                      <span className="tenant-selection-page__tenant-name">
                        {tenant.tenant_name}
                      </span>
                      <span className="tenant-selection-page__tenant-role">
                        Rôle : {tenant.role}
                      </span>
                    </div>
                  </label>
                ))}
              </div>
            </fieldset>

            <div className="tenant-selection-page__actions">
              <button
                type="submit"
                disabled={isSubmitting || !selectedTenantId}
                className="tenant-selection-page__submit"
              >
                {isSubmitting ? (
                  <>
                    <span className="tenant-selection-page__spinner" />
                    Connexion en cours...
                  </>
                ) : (
                  'Continuer'
                )}
              </button>
              
              <button
                type="button"
                onClick={() => navigate('/login', { replace: true })}
                className="tenant-selection-page__cancel"
                disabled={isSubmitting}
              >
                Retour à la connexion
              </button>
            </div>
          </form>
        </div>
      </div>
    </main>
  )
}
