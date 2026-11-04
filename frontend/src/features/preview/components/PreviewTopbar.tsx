import { Link } from 'react-router-dom'
import './PreviewTopbar.css'

export function PreviewTopbar() {
  return (
    <header className="preview-topbar">
      <div className="preview-topbar__leading">
        <button
          type="button"
          className="preview-topbar__menu"
          aria-label="Menu"
          disabled
        >
          <span aria-hidden="true" />
          <span aria-hidden="true" />
          <span aria-hidden="true" />
        </button>

        <p className="preview-topbar__context">
          Espace de gestion
        </p>
      </div>

      <div className="preview-topbar__actions">
        <div className="preview-topbar__demo-badge">
          MODE DÉMONSTRATION
        </div>

        <Link to="/login" className="preview-topbar__login-link">
          <span className="preview-topbar__avatar" aria-hidden="true">
            A
          </span>
          <span className="preview-topbar__user-info">
            <strong>admin@edunova-demo.local</strong>
            <small>ADMIN</small>
          </span>
        </Link>
      </div>
    </header>
  )
}
