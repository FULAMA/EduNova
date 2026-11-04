import type { ReactNode } from 'react'
import { Link } from 'react-router-dom'

import { canAccess, type AppModule } from '../permissions'
import { useCurrentUser } from './useCurrentUser'

type RequireRoleProps = {
  module: AppModule
  children: ReactNode
}

export function RequireRole({ module, children }: RequireRoleProps) {
  const user = useCurrentUser()

  if (!canAccess(user.role, module)) {
    return (
      <section role="alert" aria-labelledby="forbidden-title">
        <h1 id="forbidden-title">Accès non autorisé</h1>
        <p>Votre rôle ne permet pas de consulter cette section.</p>
        <Link to="/app">Retour au tableau de bord</Link>
      </section>
    )
  }

  return <>{children}</>
}