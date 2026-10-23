import { Link } from 'react-router-dom'

import './NotFoundPage.css'

export function NotFoundPage() {
  return (
    <main className="not-found-page">
      <p className="not-found-page__code">404</p>
      <h1>Page introuvable</h1>
      <p>Cette adresse ne correspond à aucune page disponible.</p>
      <Link className="not-found-page__link" to="/app">
        Retour au tableau de bord
      </Link>
    </main>
  )
}
