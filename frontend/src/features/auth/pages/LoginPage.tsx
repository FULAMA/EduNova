import type { FormEvent } from 'react'
import { useState } from 'react'
import { Link, useLocation, useNavigate } from 'react-router-dom'

import { ApiError } from '../../../shared/api/client'
import { GoogleLoginButton } from '../components/GoogleLoginButton'
import {
  loginWithGoogle,
  login,
  saveSession,
} from '../services/auth.service'
import type { LoginResponse } from '../services/auth.service'

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
    if (value.trim() && !/^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$/i.test(value.trim())) {
      return 'L\'identifiant du tenant doit être un UUID valide'
    }
    return null
  }

  function validateForm(): boolean {
    const newEmailError = validateEmail(email)
    const newPasswordError = validatePassword(password)
    const newTenantIdError = tenantId ? validateTenantId(tenantId) : null

    setEmailError(newEmailError)
    setPasswordError(newPasswordError)
    setTenantIdError(newTenantIdError)

    return !newEmailError && !newPasswordError && !newTenantIdError
  }

  /**
   * Gère la réponse de login et redirige selon le scénario
   */
  function handleLoginResponse(response: LoginResponse): void {
    // Scénario A : Utilisateur mono-tenant avec tokens ordinaires directement
    if (response.authenticated && response.access_token && response.refresh_token) {
      saveSession({
        accessToken: response.access_token,
        refreshToken: response.refresh_token,
        email: response.email || email.trim(),
        tenantId: tenantId.trim() || '',
      })
      navigate(from ?? '/app', { replace: true })
      return
    }

    // Scénario B : Sélection de tenant requise
    if (response.tenant_selection_required && response.tenant_selection_token && response.available_tenants) {
      navigate('/login/select-tenant', {
        state: {
          email: response.email || email.trim(),
          tenantSelectionToken: response.tenant_selection_token,
          availableTenants: response.available_tenants,
        },
        replace: true,
      })
      return
    }

    // Scénario C : 2FA requis (après sélection de tenant ou mono-tenant)
    if (response.two_factor_required && response.two_factor_token) {
      navigate('/login/2fa', {
        state: {
          email: response.email || email.trim(),
          twoFactorToken: response.two_factor_token,
          tenantSelectionToken: null,
        },
        replace: true,
      })
      return
    }

    // Cas d'erreur : pas de tokens et pas de redirection claire
    setError('La réponse du serveur ne contient pas de jeton de session valide.')
  }

  async function handleLoginSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault()
    setError(null)
    
    // Reset validation errors
    setEmailError(null)
    setPasswordError(null)
    setTenantIdError(null)
    setTouched({ email: true, password: true, tenantId: Boolean(tenantId) })

    if (!validateForm()) {
      return
    }

    setIsSubmitting(true)

    try {
      const response: LoginResponse = await login({
        email: email.trim(),
        password,
        tenant_id: tenantId.trim() || undefined,
      })

      handleLoginResponse(response)

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

  async function handleGoogleCredential(idToken: string, nonce: string) {
    setError(null)
    setIsSubmitting(true)

    try {
      const response: LoginResponse = await loginWithGoogle(idToken, tenantId.trim(), nonce)

      handleLoginResponse(response)

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
          <h1 id="login-title">Connexion</h1>
          <p className="login-card__description">
            Accédez à l\'espace de votre établissement.
          </p>
        </div>

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
            Identifiant de l\'établissement (optionnel)
            <input
              type="text"
              value={tenantId}
              onChange={(e) => { setTenantId(e.target.value); setTouched({...touched, tenantId: false}); }}
              onBlur={() => { setTouched({...touched, tenantId: true}); setTenantIdError(validateTenantId(tenantId)); }}
              placeholder="UUID de l'édablissement (ex: 00000000-0000-0000-0000-000000000001)"
              autoComplete="off"
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
          
          <p className="login-form__register-link">
            Nouvel établissement ?{' '}
            <Link to="/register" className="login-form__register-link--action">
              Créer un compte
            </Link>
          </p>
        </form>
      </section>
    </main>
  )
}

export default LoginPage
