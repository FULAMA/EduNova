import { useContext, useState } from 'react'
import { Outlet } from 'react-router-dom'

import { CurrentUserContext } from '../../../features/auth/components/current-user.context'
import { Sidebar } from '../Sidebar/Sidebar'
import { Topbar } from '../Topbar/Topbar'

import './AppShell.css'

export function AppShell() {
  const user = useContext(CurrentUserContext)
  const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false)

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

        <main className="app-shell__main">
          <Outlet />
        </main>
      </div>
    </div>
  )
}