import { useContext, useEffect, useState } from 'react'
import { Outlet } from 'react-router-dom'

import { CurrentUserContext } from '../../../features/auth/components/current-user.context'
import { Sidebar } from '../Sidebar/Sidebar'
import { Topbar } from '../Topbar/Topbar'

import './AppShell.css'

export function AppShell() {
  const user = useContext(CurrentUserContext)
  const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false)
  const [isOffline, setIsOffline] = useState(() => !navigator.onLine)

  useEffect(() => {
    const updateConnection = () => setIsOffline(!navigator.onLine)
    window.addEventListener('online', updateConnection)
    window.addEventListener('offline', updateConnection)
    return () => {
      window.removeEventListener('online', updateConnection)
      window.removeEventListener('offline', updateConnection)
    }
  }, [])

  const openMobileMenu = () => {
    setIsMobileMenuOpen(true)
  }

  const closeMobileMenu = () => {
    setIsMobileMenuOpen(false)
  }

  return (
    <div className="app-shell">
      <Sidebar
        isMobileOpen={isMobileMenuOpen}
        onClose={closeMobileMenu}
        role={user?.role}
      />

      <div className="app-shell__content">
        <Topbar onMenuOpen={openMobileMenu} />

        {isOffline ? (
          <p className="app-shell__offline-banner" role="status" aria-live="polite">
            Hors connexion. Les informations scolaires privées ne sont pas enregistrées sur cet appareil.
          </p>
        ) : null}

        <main className="app-shell__main">
          <Outlet />
        </main>
      </div>
    </div>
  )
}
