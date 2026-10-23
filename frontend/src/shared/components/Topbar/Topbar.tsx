import './Topbar.css'

import { useState } from 'react'
import { useNavigate } from 'react-router-dom'

import { useCurrentUser } from '../../../features/auth/components/useCurrentUser'
import { clearSession } from '../../../features/auth/services/auth.service'

type TopbarProps = {
  onMenuOpen?: () => void
}

export function Topbar({ onMenuOpen }: TopbarProps) {
  const user = useCurrentUser()
  const navigate = useNavigate()
  const [isAccountMenuOpen, setIsAccountMenuOpen] = useState(false)

  function signOut() {
    clearSession()
    setIsAccountMenuOpen(false)
    navigate('/login', { replace: true })
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
          <span aria-hidden="true" />
          <span aria-hidden="true" />
          <span aria-hidden="true" />
        </button>

        <p className="topbar__context">
          Espace de gestion
        </p>
      </div>

      <div className="topbar__actions">
        <button
          type="button"
          className="topbar__user"
          aria-label={`Compte de ${user.email}`}
          aria-expanded={isAccountMenuOpen}
          aria-controls="topbar-account-menu"
          onClick={() => setIsAccountMenuOpen((open) => !open)}
          onKeyDown={(event) => {
            if (event.key === 'Escape') setIsAccountMenuOpen(false)
          }}
        >
          <span className="topbar__avatar" aria-hidden="true">
            {user.email.charAt(0).toLocaleUpperCase()}
          </span>

          <span className="topbar__user-info">
            <strong>{user.email}</strong>
            <small>{user.role}</small>
          </span>
        </button>

        {isAccountMenuOpen ? (
          <div className="topbar__account-menu" id="topbar-account-menu">
            <p>Connecté en tant que {user.email}</p>
            <button type="button" onClick={signOut}>
              Se déconnecter
            </button>
          </div>
        ) : null}
      </div>
    </header>
  )
}
