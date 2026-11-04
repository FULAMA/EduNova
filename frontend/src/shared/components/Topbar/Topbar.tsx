import { useEffect, useRef, useState } from 'react'
import { useNavigate } from 'react-router-dom'

import { useCurrentUser } from '../../../features/auth/components/useCurrentUser'
import { clearSession } from '../../../features/auth/services/auth.service'

import './Topbar.css'

type TopbarProps = {
  onMenuOpen?: () => void
}

export function Topbar({ onMenuOpen }: TopbarProps) {
  const user = useCurrentUser()
  const navigate = useNavigate()
  const [isAccountMenuOpen, setIsAccountMenuOpen] = useState(false)
  const menuRef = useRef<HTMLDivElement>(null)

  function signOut() {
    clearSession()
    setIsAccountMenuOpen(false)
    navigate('/login', { replace: true })
  }

  // Fermer le menu si on clique à l'extérieur
  useEffect(() => {
    function handleClickOutside(event: MouseEvent) {
      if (menuRef.current && !menuRef.current.contains(event.target as Node)) {
        setIsAccountMenuOpen(false)
      }
    }

    if (isAccountMenuOpen) {
      document.addEventListener('mousedown', handleClickOutside)
    }

    return () => {
      document.removeEventListener('mousedown', handleClickOutside)
    }
  }, [isAccountMenuOpen])

  function toggleAccountMenu() {
    setIsAccountMenuOpen((open) => !open)
  }

  function handleKeyDown(event: React.KeyboardEvent) {
    if (event.key === 'Escape') {
      setIsAccountMenuOpen(false)
    }
  }

  function getInitials(email: string): string {
    return email.charAt(0).toLocaleUpperCase()
  }

  function getRoleLabel(role: string): string {
    const roleLabels: Record<string, string> = {
      ADMIN: 'Administrateur',
      DIRECTION: 'Direction',
      ACCOUNTANT: 'Comptable',
      CASHIER: 'Caissier',
      STUDENT: 'Élève',
    }
    return roleLabels[role] || role
  }

  return (
    <header className="topbar">
      <div className="topbar__leading">
        <button
          type="button"
          className="topbar__menu"
          aria-label="Ouvrir la navigation"
          onClick={onMenuOpen}
        >
          <span className="topbar__menu-bar" aria-hidden="true" />
          <span className="topbar__menu-bar" aria-hidden="true" />
          <span className="topbar__menu-bar" aria-hidden="true" />
        </button>

        <p className="topbar__context">
          Espace de gestion
        </p>
      </div>

      <div className="topbar__actions" ref={menuRef}>
        <button
          type="button"
          className="topbar__user"
          aria-label={`Compte de ${user.email}`}
          aria-expanded={isAccountMenuOpen}
          aria-controls="topbar-account-menu"
          onClick={toggleAccountMenu}
          onKeyDown={handleKeyDown}
        >
          <span className="topbar__avatar" aria-hidden="true">
            {getInitials(user.email)}
          </span>

          <span className="topbar__user-info">
            <strong className="topbar__user-email">{user.email}</strong>
            <small className="topbar__user-role">{getRoleLabel(user.role)}</small>
          </span>
        </button>

        {isAccountMenuOpen ? (
          <div className="topbar__account-menu" id="topbar-account-menu">
            <div className="topbar__account-menu-header">
              <span className="topbar__account-menu-avatar" aria-hidden="true">
                {getInitials(user.email)}
              </span>
              <div>
                <strong className="topbar__account-menu-email">{user.email}</strong>
                <small className="topbar__account-menu-role">
                  {getRoleLabel(user.role)}
                </small>
              </div>
            </div>

            <div className="topbar__account-menu-divider" />

            <div className="topbar__account-menu-items">
              <div className="topbar__account-menu-item">
                <span className="topbar__account-menu-item-label">Statut</span>
                <span className={`topbar__account-menu-item-value ${
                  user.is_active ? 'topbar__account-menu-item-value--active' : 'topbar__account-menu-item-value--inactive'
                }`}>
                  {user.is_active ? 'Actif' : 'Inactif'}
                </span>
              </div>

              <div className="topbar__account-menu-item">
                <span className="topbar__account-menu-item-label">2FA</span>
                <span className={`topbar__account-menu-item-value ${
                  user.two_factor_enabled
                    ? 'topbar__account-menu-item-value--enabled'
                    : 'topbar__account-menu-item-value--disabled'
                }`}>
                  {user.two_factor_enabled ? 'Activé' : 'Désactivé'}
                </span>
              </div>
            </div>

            <div className="topbar__account-menu-divider" />

            <button
              type="button"
              className="topbar__account-menu-signout"
              onClick={signOut}
            >
              Se déconnecter
            </button>
          </div>
        ) : null}
      </div>
    </header>
  )
}

export default Topbar
