import { NavLink } from 'react-router-dom'

import './Sidebar.css'

type NavigationItem = {
  label: string
  to: string
}

type SidebarProps = {
  isMobileOpen?: boolean
  onClose?: () => void
}

const navigationItems: NavigationItem[] = [
  {
    label: 'Tableau de bord',
    to: '/app',
  },
  {
    label: 'Élèves',
    to: '/app/students',
  },
  {
    label: 'Classes',
    to: '/app/classes',
  },
  {
    label: 'Inscriptions',
    to: '/app/enrollments',
  },
  {
    label: 'Presences',
    to: '/app/attendance',
  },
  {
    label: 'Finances',
    to: '/app/finance',
  },
  {
    label: 'Configuration scolaire',
    to: '/app/academic-catalogues',
  },
]

export function Sidebar({
  isMobileOpen = false,
  onClose,
}: SidebarProps) {
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
        className={`sidebar ${
          isMobileOpen ? 'sidebar--mobile-open' : ''
        }`}
        aria-label="Navigation principale"
      >
        <div className="sidebar__brand">
          <span className="sidebar__mark" aria-hidden="true">
            E
          </span>

          <span className="sidebar__name">
            EduNova
          </span>

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
          <p className="sidebar__section-label">
            Principal
          </p>

          <ul className="sidebar__list">
            {navigationItems.map((item) => (
              <li key={item.to}>
                <NavLink
                  to={item.to}
                  end={item.to === '/app'}
                  aria-label={item.label}
                  className={({ isActive }) =>
                    `sidebar__item ${
                      isActive
                        ? 'sidebar__item--active'
                        : ''
                    }`
                  }
                  onClick={onClose}
                >
                  <span
                    className="sidebar__indicator"
                    aria-hidden="true"
                  />

                  <span>{item.label}</span>
                </NavLink>
              </li>
            ))}
          </ul>
        </nav>

        <div className="sidebar__footer">
          <span className="sidebar__version">
            EduNova v0.1.0
          </span>
        </div>
      </aside>
    </>
  )
}
