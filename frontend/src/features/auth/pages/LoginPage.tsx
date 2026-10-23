import { type FormEvent, useState } from 'react'
import { useLocation, useNavigate } from 'react-router-dom'

import { ApiError } from '../../../shared/api/client'
import { GoogleLoginButton } from '../components/GoogleLoginButton'
import {
  loginWithGoogle,
  login,
  saveSession,
  verifyLoginTwoFactor,
} from '../services/auth.service'

import './LoginPage.css'

type LoginLocationState = {
  from?: { pathname?: string }
}

function LoginPage() {
  const navigate = useNavigate()
  const location = useLocation()
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [tenantId, setTenantId] = useState('')
  const [twoFactorToken, setTwoFactorToken] = useState<string | null>(null)
  const [twoFactorCode, setTwoFactorCode] = useState('')
  const [error, setError] = useState<string | null>(null)
  const [isSubmitting, setIsSubmitting] = useState(false)

  const from = (location.state as LoginLocationState | null)?.from?.pathname

  async function handleLoginSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault()
    setError(null)
    setIsSubmitting(true)

    try {
      const response = await login({
        email: email.trim(),
        password,
        tenant_id: tenantId.trim(),
      })

      if (response.two_factor_required) {
        if (!response.two_factor_token) {
          setError('Le serveur n’a pas fourni de défi 2FA valide.')
          return
        }

        setPassword('')
        setTwoFactorToken(response.two_factor_token)
        return
      }

      if (
        !response.authenticated ||
        !response.access_token ||
        !response.refresh_token
      ) {
        setError('Connexion refusée par le serveur.')
        return
      }

      saveSession({
        accessToken: response.access_token,
        refreshToken: response.refresh_token,
        email: email.trim(),
        tenantId: tenantId.trim(),
      })
      navigate(from ?? '/app', { replace: true })
    } catch (cause) {
      if (cause instanceof ApiError && cause.status === 401) {
        setError('Adresse e-mail ou mot de passe incorrect.')
      } else if (cause instanceof ApiError && cause.status === 403) {
        setError('Votre compte n a pas acces a cet etablissement.')
      } else if (cause instanceof ApiError && cause.status === 422) {
        setError('L identifiant de l etablissement doit etre un UUID valide.')
      } else if (cause instanceof ApiError && cause.status === 0) {
        setError('Backend inaccessible. Demarrez l API puis reessayez.')
      } else if (cause instanceof ApiError && cause.status >= 500) {
        setError('Le serveur API a rencontre une erreur interne.')
      } else if (cause instanceof ApiError && cause.status === 400) {
        setError('Requete de connexion invalide.')
      } else {
        setError('Connexion impossible. Vérifiez votre serveur API.')
      }
    } finally {
      setIsSubmitting(false)
    }
  }

  async function handleTwoFactorSubmit(
    event: FormEvent<HTMLFormElement>,
  ) {
    event.preventDefault()
    setError(null)

    if (!twoFactorToken || !/^\d{6}$/.test(twoFactorCode)) {
      setError('Saisissez un code 2FA de 6 chiffres.')
      return
    }

    setIsSubmitting(true)

    try {
      const response = await verifyLoginTwoFactor(
        twoFactorToken,
        twoFactorCode,
      )

      if (!response.authenticated) {
        setError('La vérification 2FA a été refusée.')
        setTwoFactorCode('')
        return
      }

      saveSession({
        accessToken: response.access_token,
        refreshToken: response.refresh_token,
        email: email.trim(),
        tenantId: tenantId.trim(),
      })
      setTwoFactorCode('')
      navigate(from ?? '/app', { replace: true })
    } catch (cause) {
      setTwoFactorCode('')

      if (cause instanceof ApiError && cause.status === 400) {
        setError(
          cause.message.includes('Code 2FA')
            ? 'Code 2FA invalide.'
            : 'Le défi 2FA est invalide ou expiré. Recommencez.',
        )
      } else if (cause instanceof ApiError && cause.status === 404) {
        setError('La session 2FA n’est plus disponible. Recommencez.')
      } else {
        setError('Vérification impossible. Vérifiez votre serveur API.')
      }
    } finally {
      setIsSubmitting(false)
    }
  }

  async function handleGoogleCredential(idToken: string) {
    setError(null)
    setIsSubmitting(true)

    try {
      const response = await loginWithGoogle(idToken, tenantId.trim())

      if (response.two_factor_required) {
        if (!response.two_factor_token) {
          setError('Le serveur n a pas fourni de defi 2FA valide.')
          return
        }

        if (response.email) {
          setEmail(response.email)
        }
        setTwoFactorToken(response.two_factor_token)
        return
      }

      if (
        !response.authenticated ||
        !response.access_token ||
        !response.refresh_token
      ) {
        setError('Connexion Google refusee par le serveur.')
        return
      }

      const authenticatedEmail = response.email ?? email.trim()
      saveSession({
        accessToken: response.access_token,
        refreshToken: response.refresh_token,
        email: authenticatedEmail,
        tenantId: tenantId.trim(),
      })
      navigate(from ?? '/app', { replace: true })
    } catch (cause) {
      if (cause instanceof ApiError && cause.status === 401) {
        setError('Authentification Google refusee.')
      } else if (cause instanceof ApiError && cause.status === 403) {
        setError('Votre compte n a pas acces a cet etablissement.')
      } else if (cause instanceof ApiError && cause.status === 503) {
        setError('La connexion Google n est pas configuree.')
      } else {
        setError('Connexion Google impossible. Verifiez votre serveur API.')
      }
    } finally {
      setIsSubmitting(false)
    }
  }

  function restartLogin() {
    setTwoFactorToken(null)
    setTwoFactorCode('')
    setPassword('')
    setError(null)
  }

  return (
    <main className="login-page">
      <section className="login-card" aria-labelledby="login-title">
        <p className="login-card__eyebrow">EduNova</p>
        <h1 id="login-title">{twoFactorToken ? 'Verification' : 'Connexion'}</h1>
        <p className="login-card__description">
          {twoFactorToken
            ? 'Confirmez votre identite avec le code de votre application.'
            : 'Accedez a l’espace de votre etablissement.'}
        </p>

        {twoFactorToken ? (
          <form className="login-form" onSubmit={handleTwoFactorSubmit}>
            <div className="login-form__challenge">
              <h2>Double authentification</h2>
              <p>Saisissez le code a 6 chiffres genere par votre application.</p>
            </div>

            <label>
              Code de verification
              <input
                type="text"
                value={twoFactorCode}
                onChange={(event) =>
                  setTwoFactorCode(
                    event.target.value.replace(/\D/g, '').slice(0, 6),
                  )
                }
                inputMode="numeric"
                pattern="[0-9]{6}"
                minLength={6}
                maxLength={6}
                autoComplete="one-time-code"
                required
                autoFocus
              />
            </label>

            {error ? (
              <p className="login-form__error" role="alert">
                {error}
              </p>
            ) : null}

            <button type="submit" disabled={isSubmitting}>
              {isSubmitting ? 'Verification...' : 'Verifier le code'}
            </button>

            <button
              type="button"
              className="login-form__secondary-button"
              onClick={restartLogin}
              disabled={isSubmitting}
            >
              Retour a la connexion
            </button>
          </form>
        ) : (
          <form className="login-form" onSubmit={handleLoginSubmit}>
            <label>
              Adresse e-mail
              <input
                type="email"
                value={email}
                onChange={(event) => setEmail(event.target.value)}
                autoComplete="username"
                required
              />
            </label>

            <label>
              Mot de passe
              <input
                type="password"
                value={password}
                onChange={(event) => setPassword(event.target.value)}
                autoComplete="current-password"
                required
              />
            </label>

            <label>
              Identifiant de l’etablissement
              <input
                type="text"
                value={tenantId}
                onChange={(event) => setTenantId(event.target.value)}
                placeholder="UUID du tenant"
                required
              />
            </label>

            {error ? (
              <p className="login-form__error" role="alert">
                {error}
              </p>
            ) : null}

            <button type="submit" disabled={isSubmitting}>
              {isSubmitting ? 'Connexion...' : 'Se connecter'}
            </button>

            <GoogleLoginButton onCredential={handleGoogleCredential} />
          </form>
        )}
      </section>
    </main>
  )
}

export default LoginPage
