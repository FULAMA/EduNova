import type { FormEvent } from 'react'
import { useState } from 'react'
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
  const [showPassword, setShowPassword] = useState(false)
  const [emailError, setEmailError] = useState<string | null>(null)
  const [passwordError, setPasswordError] = useState<string | null>(null)
  const [tenantIdError, setTenantIdError] = useState<string | null>(null)
  const [touched, setTouched] = useState({ email: false, password: false, tenantId: false })

  const from = (location.state as LoginLocationState | null)?.from?.pathname

  function validateEmail(value: string): string | null {
    if (!value.trim()) return 'L\'adresse e-mail est requise'
    if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(value)) {
      return 'Adresse e-mail invalide'
    }
    return null
  }

  function validatePassword(value: string): string | null {
    if (!value) return 'Le mot de passe est requis'
    if (value.length < 8) return 'Le mot de passe doit contenir au moins 8 caractères'
    return null
  }

  function validateTenantId(value: string): string | null {
    if (!value.trim()) return 'L\'identifiant du tenant est requis'
    // Basic UUID validation (8-4-4-4-12 hex format)
    if (!/^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$/i.test(value.trim())) {
      return 'L\'identifiant du tenant doit être un UUID valide'
    }
    return null
  }

  function validateForm(): boolean {
    const newEmailError = validateEmail(email)
    const newPasswordError = validatePassword(password)
    const newTenantIdError = validateTenantId(tenantId)

    setEmailError(newEmailError)
    setPasswordError(newPasswordError)
    setTenantIdError(newTenantIdError)

    return !newEmailError && !newPasswordError && !newTenantIdError
  }

  async function handleLoginSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault()
    setError(null)
    
    // Reset validation errors
    setEmailError(null)
    setPasswordError(null)
    setTenantIdError(null)
    setTouched({ email: true, password: true, tenantId: true })

    if (!validateForm()) {
      return
    }

    setIsSubmitting(true)

    try {
      const response = await login({
        email: email.trim(),
        password,
        tenant_id: tenantId.trim(),
      })

      if (response.two_factor_required) {
        if (!response.two_factor_token) {
          setError('Le serveur n\'a pas fourni de défi 2FA valide.')
          return
        }

        setPassword('')
        setShowPassword(false)
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
        setError('Votre compte n\'a pas accès à cet établissement.')
      } else if (cause instanceof ApiError && cause.status === 422) {
        setError('L\'identifiant de l\'établissement doit être un UUID valide.')
      } else if (cause instanceof ApiError && cause.status === 0) {
        setError('Backend inaccessible. Démarrez l\'API puis réessayez.')
      } else if (cause instanceof ApiError && cause.status >= 500) {
        setError('Le serveur API a rencontré une erreur interne.')
      } else if (cause instanceof ApiError && cause.status === 400) {
        setError('Requête de connexion invalide.')
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
        setError('La session 2FA n\'est plus disponible. Recommencez.')
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
          setError('Le serveur n\'a pas fourni de défi 2FA valide.')
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
        setError('Connexion Google refusée par le serveur.')
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
        setError('Authentification Google refusée.')
      } else if (cause instanceof ApiError && cause.status === 403) {
        setError('Votre compte n\'a pas accès à cet établissement.')
      } else if (cause instanceof ApiError && cause.status === 503) {
        setError('La connexion Google n\'est pas configurée.')
      } else {
        setError('Connexion Google impossible. Vérifiez votre serveur API.')
      }
    } finally {
      setIsSubmitting(false)
    }
  }

  function restartLogin() {
    setTwoFactorToken(null)
    setTwoFactorCode('')
    setPassword('')
    setShowPassword(false)
    setError(null)
  }



  function togglePasswordVisibility() {
    setShowPassword(!showPassword)
  }

  function getInputClassName(fieldError: string | null): string {
    return fieldError ? 'login-form__input--error' : ''
  }

  return (
    <main className="login-page">
      <section className="login-card" aria-labelledby="login-title">
        <div className="login-card__header">
          <p className="login-card__eyebrow">EduNova</p>
          <h1 id="login-title">{twoFactorToken ? 'Vérification' : 'Connexion'}</h1>
          <p className="login-card__description">
            {twoFactorToken
              ? 'Confirmez votre identité avec le code de votre application.'
              : 'Accédez à l\'espace de votre établissement.'}
          </p>
        </div>

        {twoFactorToken ? (
          <form className="login-form" onSubmit={handleTwoFactorSubmit}>
            <div className="login-form__challenge">
              <h2>Double authentification</h2>
              <p>Saisissez le code à 6 chiffres généré par votre application.</p>
            </div>

            <label>
              Code de vérification
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
                className={getInputClassName(null)}
              />
            </label>

            {error ? (
              <p className="login-form__error" role="alert">
                {error}
              </p>
            ) : null}

            <button type="submit" disabled={isSubmitting}>
              {isSubmitting ? 'Vérification...' : 'Vérifier le code'}
            </button>

            <button
              type="button"
              className="login-form__secondary-button"
              onClick={restartLogin}
              disabled={isSubmitting}
            >
              Retour à la connexion
            </button>
          </form>
        ) : (
          <form className="login-form" onSubmit={handleLoginSubmit}>
            <label className="login-form__label">
              Adresse e-mail
              <input
                type="email"
                value={email}
                onChange={(e) => { setEmail(e.target.value); setTouched({...touched, email: false}); }}
                onBlur={() => { setTouched({...touched, email: true}); setEmailError(validateEmail(email)); }}
                autoComplete="username"
                required
                className={getInputClassName(touched.email ? emailError : null)}
                aria-invalid={touched.email && !!emailError}
                aria-describedby={touched.email && emailError ? 'email-error' : undefined}
              />
              {touched.email && emailError && (
                <span className="login-form__field-error" id="email-error">
                  {emailError}
                </span>
              )}
            </label>

            <label className="login-form__label">
              Mot de passe
              <div className="login-form__password-wrapper">
                <input
                  type={showPassword ? 'text' : 'password'}
                  value={password}
                  onChange={(e) => { setPassword(e.target.value); setTouched({...touched, password: false}); }}
                  onBlur={() => { setTouched({...touched, password: true}); setPasswordError(validatePassword(password)); }}
                  autoComplete="current-password"
                  required
                  className={getInputClassName(touched.password ? passwordError : null)}
                  aria-invalid={touched.password && !!passwordError}
                  aria-describedby={touched.password && passwordError ? 'password-error' : undefined}
                />
                <button
                  type="button"
                  className="login-form__password-toggle"
                  onClick={togglePasswordVisibility}
                  aria-label={showPassword ? 'Masquer le mot de passe' : 'Afficher le mot de passe'}
                >
                  {showPassword ? '👁️‍🗨️' : '👁️'}
                </button>
              </div>
              {touched.password && passwordError && (
                <span className="login-form__field-error" id="password-error">
                  {passwordError}
                </span>
              )}
            </label>

            <label className="login-form__label">
              Identifiant de l\'établissement
              <input
                type="text"
                value={tenantId}
                onChange={(e) => { setTenantId(e.target.value); setTouched({...touched, tenantId: false}); }}
                onBlur={() => { setTouched({...touched, tenantId: true}); setTenantIdError(validateTenantId(tenantId)); }}
                placeholder="UUID du tenant (ex: 00000000-0000-0000-0000-000000000001)"
                autoComplete="off"
                required
                className={getInputClassName(touched.tenantId ? tenantIdError : null)}
                aria-invalid={touched.tenantId && !!tenantIdError}
                aria-describedby={touched.tenantId && tenantIdError ? 'tenant-error' : undefined}
              />
              {touched.tenantId && tenantIdError && (
                <span className="login-form__field-error" id="tenant-error">
                  {tenantIdError}
                </span>
              )}
            </label>

            {error && !emailError && !passwordError && !tenantIdError ? (
              <p className="login-form__error" role="alert">
                {error}
              </p>
            ) : null}

            <button
              type="submit"
              disabled={isSubmitting}
              className="login-form__submit"
            >
              {isSubmitting ? (
                <>
                  <span className="login-form__spinner" />
                  Connexion en cours...
                </>
              ) : (
                'Se connecter'
              )}
            </button>

            <GoogleLoginButton onCredential={handleGoogleCredential} />
          </form>
        )}
      </section>
    </main>
  )
}

export default LoginPage
