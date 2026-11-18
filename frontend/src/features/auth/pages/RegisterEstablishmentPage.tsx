import type { FormEvent } from 'react'
import { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'

import { ApiError } from '../../../shared/api/client'
import { registerEstablishment } from '../services/auth.service'

import './RegisterEstablishmentPage.css'

function RegisterEstablishmentPage() {
  const navigate = useNavigate()
  const [schoolName, setSchoolName] = useState('')
  const [adminName, setAdminName] = useState('')
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [confirmPassword, setConfirmPassword] = useState('')
  const [error, setError] = useState<string | null>(null)
  const [success, setSuccess] = useState<string | null>(null)
  const [isSubmitting, setIsSubmitting] = useState(false)
  const [showPassword, setShowPassword] = useState(false)
  const [showConfirmPassword, setShowConfirmPassword] = useState(false)

  // Validation states
  const [schoolNameError, setSchoolNameError] = useState<string | null>(null)
  const [adminNameError, setAdminNameError] = useState<string | null>(null)
  const [emailError, setEmailError] = useState<string | null>(null)
  const [passwordError, setPasswordError] = useState<string | null>(null)
  const [confirmPasswordError, setConfirmPasswordError] = useState<string | null>(null)

  const [touched, setTouched] = useState({
    schoolName: false,
    adminName: false,
    email: false,
    password: false,
    confirmPassword: false,
  })

  function validateSchoolName(value: string): string | null {
    if (!value.trim()) return "Le nom de l'établissement est requis"
    if (value.trim().length < 2) return "Le nom doit contenir au moins 2 caractères"
    if (value.trim().length > 200) return "Le nom ne peut pas dépasser 200 caractères"
    return null
  }

  function validateAdminName(value: string): string | null {
    if (!value.trim()) return "Le nom complet est requis"
    if (value.trim().length < 2) return "Le nom doit contenir au moins 2 caractères"
    if (value.trim().length > 150) return "Le nom ne peut pas dépasser 150 caractères"
    return null
  }

  function validateEmail(value: string): string | null {
    if (!value.trim()) return "L'adresse e-mail est requise"
    if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(value.trim())) {
      return "Adresse e-mail invalide"
    }
    if (value.trim().length < 5 || value.trim().length > 255) {
      return "L'adresse e-mail doit contenir entre 5 et 255 caractères"
    }
    return null
  }

  function validatePassword(value: string): string | null {
    if (!value) return "Le mot de passe est requis"
    if (value.length < 8) return "Le mot de passe doit contenir au moins 8 caractères"
    if (value.length > 128) return "Le mot de passe ne peut pas dépasser 128 caractères"
    return null
  }

  function validateConfirmPassword(value: string): string | null {
    if (!value) return "La confirmation du mot de passe est requise"
    if (value !== password) return "Les mots de passe ne correspondent pas"
    return null
  }

  function validateForm(): boolean {
    const newSchoolNameError = validateSchoolName(schoolName)
    const newAdminNameError = validateAdminName(adminName)
    const newEmailError = validateEmail(email)
    const newPasswordError = validatePassword(password)
    const newConfirmPasswordError = validateConfirmPassword(confirmPassword)

    setSchoolNameError(newSchoolNameError)
    setAdminNameError(newAdminNameError)
    setEmailError(newEmailError)
    setPasswordError(newPasswordError)
    setConfirmPasswordError(newConfirmPasswordError)

    return !newSchoolNameError && !newAdminNameError && !newEmailError && !newPasswordError && !newConfirmPasswordError
  }

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault()
    setError(null)
    setSuccess(null)

    // Reset validation errors
    setSchoolNameError(null)
    setAdminNameError(null)
    setEmailError(null)
    setPasswordError(null)
    setConfirmPasswordError(null)
    setTouched({
      schoolName: true,
      adminName: true,
      email: true,
      password: true,
      confirmPassword: true,
    })

    if (!validateForm()) {
      return
    }

    setIsSubmitting(true)

    try {
      const response = await registerEstablishment({
        school_name: schoolName.trim(),
        admin_name: adminName.trim(),
        email: email.trim(),
        password: password,
      })

      setSuccess(
        `Inscription réussie ! Un établissement a été créé pour ${response.admin_name}. ` +
        `Vous pouvez maintenant vous connecter avec ${response.email}.`
      )

      // Clear form on success
      setSchoolName('')
      setAdminName('')
      setEmail('')
      setPassword('')
      setConfirmPassword('')
      setShowPassword(false)
      setShowConfirmPassword(false)
      setTouched({
        schoolName: false,
        adminName: false,
        email: false,
        password: false,
        confirmPassword: false,
      })

      // Optionally redirect to login after a delay
      setTimeout(() => {
        navigate('/login')
      }, 3000)

    } catch (cause) {
      if (cause instanceof ApiError) {
        if (cause.status === 400) {
          setError(cause.message || 'Requête invalide. Vérifiez vos informations.')
        } else if (cause.status === 409) {
          setError('Cette adresse e-mail est déjà utilisée.')
        } else if (cause.status === 422) {
          setError('Données invalides. Vérifiez les champs.')
        } else if (cause.status === 429) {
          setError('Trop de tentatives. Veuillez réessayer plus tard.')
        } else if (cause.status === 0) {
          setError('Backend inaccessible. Démarrez l\'API puis réessayez.')
        } else if (cause.status >= 500) {
          setError('Le serveur a rencontré une erreur interne.')
        } else {
          setError('Une erreur est survenue. Vérifiez votre serveur API.')
        }
      } else {
        setError('Une erreur est survenue. Vérifiez votre serveur API.')
      }
    } finally {
      setIsSubmitting(false)
    }
  }

  function togglePasswordVisibility() {
    setShowPassword(!showPassword)
  }

  function toggleConfirmPasswordVisibility() {
    setShowConfirmPassword(!showConfirmPassword)
  }

  function getInputClassName(fieldError: string | null): string {
    return fieldError ? 'register-form__input--error' : ''
  }

  return (
    <main className="register-page">
      <section className="register-card" aria-labelledby="register-title">
        <div className="register-card__header">
          <p className="register-card__eyebrow">EduNova</p>
          <h1 id="register-title">Créer un établissement</h1>
          <p className="register-card__description">
            Inscription gratuite pour les établissements éducatifs.
          </p>
        </div>

        {success ? (
          <div className="register-form__success" role="alert">
            {success}
          </div>
        ) : null}

        {error ? (
          <p className="register-form__error" role="alert">
            {error}
          </p>
        ) : null}

        <form className="register-form" onSubmit={handleSubmit}>
          <label className="register-form__label">
            Nom de l'établissement
            <input
              name="school_name"
              type="text"
              value={schoolName}
              onChange={(e) => { setSchoolName(e.target.value); setTouched({...touched, schoolName: false}); }}
              onBlur={() => { setTouched({...touched, schoolName: true}); setSchoolNameError(validateSchoolName(schoolName)); }}
              placeholder="Ex: École Primaire Saint-Martin"
              autoComplete="organization"
              required
              className={getInputClassName(touched.schoolName ? schoolNameError : null)}
              aria-invalid={touched.schoolName && !!schoolNameError}
              aria-describedby={touched.schoolName && schoolNameError ? 'school-name-error' : undefined}
            />
            {touched.schoolName && schoolNameError && (
              <span className="register-form__field-error" id="school-name-error">
                {schoolNameError}
              </span>
            )}
          </label>

          <label className="register-form__label">
            Nom complet du responsable
            <input
              name="admin_name"
              type="text"
              value={adminName}
              onChange={(e) => { setAdminName(e.target.value); setTouched({...touched, adminName: false}); }}
              onBlur={() => { setTouched({...touched, adminName: true}); setAdminNameError(validateAdminName(adminName)); }}
              placeholder="Ex: Jean Dupont"
              autoComplete="name"
              required
              className={getInputClassName(touched.adminName ? adminNameError : null)}
              aria-invalid={touched.adminName && !!adminNameError}
              aria-describedby={touched.adminName && adminNameError ? 'admin-name-error' : undefined}
            />
            {touched.adminName && adminNameError && (
              <span className="register-form__field-error" id="admin-name-error">
                {adminNameError}
              </span>
            )}
          </label>

          <label className="register-form__label">
            Adresse e-mail
            <input
              name="email"
              type="email"
              value={email}
              onChange={(e) => { setEmail(e.target.value); setTouched({...touched, email: false}); }}
              onBlur={() => { setTouched({...touched, email: true}); setEmailError(validateEmail(email)); }}
              placeholder="Ex: jean.dupont@ecole.fr"
              autoComplete="email"
              required
              className={getInputClassName(touched.email ? emailError : null)}
              aria-invalid={touched.email && !!emailError}
              aria-describedby={touched.email && emailError ? 'email-error' : undefined}
            />
            {touched.email && emailError && (
              <span className="register-form__field-error" id="email-error">
                {emailError}
              </span>
            )}
          </label>

          <label className="register-form__label">
            Mot de passe
            <div className="register-form__password-wrapper">
              <input
                name="password"
                type={showPassword ? 'text' : 'password'}
                value={password}
                onChange={(e) => { setPassword(e.target.value); setTouched({...touched, password: false}); }}
                onBlur={() => { setTouched({...touched, password: true}); setPasswordError(validatePassword(password)); }}
                placeholder="Min. 8 caractères"
                autoComplete="new-password"
                required
                className={getInputClassName(touched.password ? passwordError : null)}
                aria-invalid={touched.password && !!passwordError}
                aria-describedby={touched.password && passwordError ? 'password-error' : undefined}
              />
              <button
                type="button"
                className="register-form__password-toggle"
                onClick={togglePasswordVisibility}
                aria-label={showPassword ? 'Masquer le mot de passe' : 'Afficher le mot de passe'}
              >
                {showPassword ? '👁️‍🗨️' : '👁️'}
              </button>
            </div>
            {touched.password && passwordError && (
              <span className="register-form__field-error" id="password-error">
                {passwordError}
              </span>
            )}
          </label>

          <label className="register-form__label">
            Confirmer le mot de passe
            <div className="register-form__password-wrapper">
              <input
                name="confirm_password"
                type={showConfirmPassword ? 'text' : 'password'}
                value={confirmPassword}
                onChange={(e) => { setConfirmPassword(e.target.value); setTouched({...touched, confirmPassword: false}); }}
                onBlur={() => { setTouched({...touched, confirmPassword: true}); setConfirmPasswordError(validateConfirmPassword(confirmPassword)); }}
                placeholder="Confirmez votre mot de passe"
                autoComplete="new-password"
                required
                className={getInputClassName(touched.confirmPassword ? confirmPasswordError : null)}
                aria-invalid={touched.confirmPassword && !!confirmPasswordError}
                aria-describedby={touched.confirmPassword && confirmPasswordError ? 'confirm-password-error' : undefined}
              />
              <button
                type="button"
                className="register-form__password-toggle"
                onClick={toggleConfirmPasswordVisibility}
                aria-label={showConfirmPassword ? 'Masquer le mot de passe' : 'Afficher le mot de passe'}
              >
                {showConfirmPassword ? '👁️‍🗨️' : '👁️'}
              </button>
            </div>
            {touched.confirmPassword && confirmPasswordError && (
              <span className="register-form__field-error" id="confirm-password-error">
                {confirmPasswordError}
              </span>
            )}
          </label>

          <button
            type="submit"
            disabled={isSubmitting}
            className="register-form__submit"
          >
            {isSubmitting ? (
              <>
                <span className="register-form__spinner" />
                Inscription en cours...
              </>
            ) : (
              'Créer mon établissement'
            )}
          </button>

          <p className="register-form__login-link">
            Déjà un compte ?{' '}
            <Link to="/login" className="register-form__login-link--action">
              Se connecter
            </Link>
          </p>
        </form>
      </section>
    </main>
  )
}

export default RegisterEstablishmentPage
