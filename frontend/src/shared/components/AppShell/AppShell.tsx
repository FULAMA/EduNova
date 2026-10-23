import { useState } from 'react'
import { Outlet } from 'react-router-dom'

import { Sidebar } from '../Sidebar/Sidebar'
import { Topbar } from '../Topbar/Topbar'

import './AppShell.css'

export function AppShell() {
  const [isMobileMenuOpen, setIsMobileMenuOpen] =
    useState(false)

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
