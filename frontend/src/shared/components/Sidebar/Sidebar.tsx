import { NavLink } from 'react-router-dom'

import { canAccess, type AppModule } from '../../../features/auth/permissions'

import './Sidebar.css'

type NavigationItem = {
  label: string
  to: string
  module: AppModule
  icon: string
}

type SidebarProps = {
  isMobileOpen?: boolean
  onClose?: () => void
  role?: string
}

const navigationItems: NavigationItem[] = [
  { label: 'Tableau de bord', to: '/app', module: 'dashboard', icon: '📊' },
  { label: 'Élèves', to: '/app/students', module: 'students', icon: '👥' },
  { label: 'Classes', to: '/app/classes', module: 'classes', icon: '🏫' },
  { label: 'Inscriptions', to: '/app/enrollments', module: 'enrollments', icon: '📋' },
  { label: 'Présences', to: '/app/attendance', module: 'attendance', icon: '✅' },
  { label: 'Finances', to: '/app/finance', module: 'finance', icon: '💰' },
  {
    label: 'Configuration scolaire',
    to: '/app/academic-catalogues',
    module: 'academic-catalogues',
    icon: '⚙️',
  },
]

export function Sidebar({
  isMobileOpen = false,
  onClose,
  role,
}: SidebarProps) {
  const visibleItems =
    role === undefined
      ? navigationItems
      : navigationItems.filter((item) => canAccess(role, item.module))

  return (
    <>
      {isMobileOpen ? (
        <button
          type="button"
          className="sidebar__overlay"
          aria-label="Fermer la navigation"
          onClick={onClose}
        />
      ) : null}

      <aside
        className={`sidebar ${isMobileOpen ? 'sidebar--mobile-open' : ''}`}
        aria-label="Navigation principale"
      >
        <div className="sidebar__brand">
          <span className="sidebar__mark" aria-hidden="true">
            E
          </span>

          <span className="sidebar__name">EduNova</span>

          <button
            type="button"
            className="sidebar__close"
            aria-label="Fermer la navigation"
            onClick={onClose}
          >
            ×
          </button>
        </div>

        <nav className="sidebar__navigation">
          <p className="sidebar__section-label">Principal</p>

          <ul className="sidebar__list">
            {visibleItems.map((item) => (
              <li key={item.to}>
                <NavLink
                  to={item.to}
                  end={item.to === '/app'}
                  aria-label={item.label}
                  className={({ isActive }) =>
                    `sidebar__item ${isActive ? 'sidebar__item--active' : ''}`
                  }
                  onClick={onClose}
                >
                  <span className="sidebar__icon" aria-hidden="true">
                    {item.icon}
                  </span>
                  <span className="sidebar__indicator" aria-hidden="true" />
                  <span className="sidebar__label">{item.label}</span>
                </NavLink>
              </li>
            ))}
          </ul>
        </nav>

        <div className="sidebar__footer">
          <span className="sidebar__version">EduNova v0.1.0</span>
        </div>
      </aside>
    </>
  )
}

export default Sidebar
