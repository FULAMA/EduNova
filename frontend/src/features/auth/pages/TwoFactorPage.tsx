import type { FormEvent } from 'react'
import { useState, useEffect } from 'react'
import { useNavigate, useLocation } from 'react-router-dom'
import { verifyLoginTwoFactor, type VerifyLoginTwoFactorResponse } from '../services/auth.service'
import { saveSession } from '../services/auth.storage'
import { describeAuthError } from '../../../shared/api/client.errors'

/**
 * TwoFactorPage - Page de validation 2FA
 * 
 * Cette page est affichée après une authentification réussie
 * lorsque le 2FA est requis pour l'utilisateur.
 * 
 * Elle permet de saisir le code TOTP et appelle POST /auth/2fa/login
 * pour obtenir les tokens ordinaires.
 */
export default function TwoFactorPage() {
  const navigate = useNavigate()
  const location = useLocation()

  // Récupérer les données passées depuis LoginPage ou TenantSelectionPage
  const state = location.state as {
    email?: string
    twoFactorToken?: string
    tenantSelectionToken?: string | null
  } | null

  const [code, setCode] = useState('')
  const [isSubmitting, setIsSubmitting] = useState(false)
  const [error, setError] = useState<string | null>(null)

  // Données par défaut si pas de state
  const email = state?.email || ''
  const twoFactorToken = state?.twoFactorToken || ''

  // Redirection si pas de token 2FA
  useEffect(() => {
    if (!twoFactorToken) {
      navigate('/login', { replace: true })
    }
  }, [twoFactorToken, navigate])

  if (!twoFactorToken) {
    return null
  }

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault()
    setError(null)

    if (!code || code.length !== 6) {
      setError('Veuillez saisir un code à 6 chiffres')
      return
    }

    setIsSubmitting(true)

    try {
      const response: VerifyLoginTwoFactorResponse = await verifyLoginTwoFactor(
        twoFactorToken,
        code,
      )

      // Sauvegarde de la session
      saveSession({
        accessToken: response.access_token,
        refreshToken: response.refresh_token,
        email: email,
        tenantId: '',
      })

      // Redirection vers la page d'accueil
      navigate('/')

    } catch (err) {
      const error = describeAuthError(err)
      setError(error.message)
      
      // Nettoyage du code en cas d'erreur
      setCode('')
      
      // Si le token 2FA a expiré ou été consommé (pas juste "invalide" qui peut être le code)
      if (error.message.includes('Token 2FA') || error.message.includes('consomme')) {
        setError('Votre session 2FA a expiré. Veuillez vous reconnecter.')
        setTimeout(() => {
          navigate('/login', { replace: true })
        }, 3000)
      }
      
      // Si trop de tentatives
      if (error.message.includes('tentatives') || error.message.includes('2FA depasse')) {
        setTimeout(() => {
          navigate('/login', { replace: true })
        }, 5000)
      }
    } finally {
      setIsSubmitting(false)
    }
  }

  // Formatage automatique du code (6 chiffres max)
  function handleCodeChange(value: string) {
    const numericValue = value.replace(/\D/g, '').slice(0, 6)
    setCode(numericValue)
  }

  // Soumission automatique si 6 chiffres
  function handleCodeComplete(value: string) {
    if (value.length === 6 && !isSubmitting) {
      handleSubmit(new Event('submit') as any)
    }
  }

  return (
    <main className="two-factor-page">
      <div className="two-factor-page__container">
        <div className="two-factor-page__card">
          <h1 className="two-factor-page__title">
            Vérification à deux facteurs
          </h1>
          
          <p className="two-factor-page__description">
            Un code de vérification a été envoyé à votre application
            <br />
            d'authentification. Saisissez-le ci-dessous.
          </p>
          
          <p className="two-factor-page__email">
            Connecté en tant que : <strong>{email}</strong>
          </p>

          {error && (
            <div className="two-factor-page__error">
              {error}
            </div>
          )}

          <form onSubmit={handleSubmit} className="two-factor-page__form">
            <div className="two-factor-page__code-container">
              <label htmlFor="code" className="two-factor-page__code-label">
                Code à 6 chiffres
              </label>
              <input
                id="code"
                name="code"
                type="text"
                value={code}
                onChange={(e) => {
                  handleCodeChange(e.target.value)
                }}
                onPaste={(e) => {
                  const pasted = e.clipboardData.getData('text')
                  handleCodeChange(pasted)
                  handleCodeComplete(pasted)
                  e.preventDefault()
                }}
                inputMode="numeric"
                pattern="[0-9]*"
                autoComplete="one-time-code"
                autoFocus
                placeholder="123456"
                maxLength={6}
                className="two-factor-page__code-input"
                disabled={isSubmitting}
                aria-describedby={error ? 'code-error' : undefined}
              />
              <p className="two-factor-page__code-hint">
                Le code expire après 30 secondes
              </p>
            </div>

            <button
              type="submit"
              disabled={isSubmitting || code.length !== 6}
              className="two-factor-page__submit"
            >
              {isSubmitting ? (
                <>
                  <span className="two-factor-page__spinner" />
                  Vérification en cours...
                </>
              ) : (
                'Vérifier'
              )}
            </button>
          </form>

          <div className="two-factor-page__footer">
            <button
              type="button"
              onClick={() => navigate('/login', { replace: true })}
              className="two-factor-page__cancel"
              disabled={isSubmitting}
            >
              Retour à la connexion
            </button>
          </div>
        </div>
      </div>
    </main>
  )
}
