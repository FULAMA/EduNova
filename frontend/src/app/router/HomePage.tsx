import { Navigate } from 'react-router-dom'

import DashboardPage from '../../features/dashboard/pages/DashboardPage'
import StudentPortalPage from '../../features/students/pages/StudentPortalPage/StudentPortalPage'
import { useCurrentUser } from '../../features/auth/components/useCurrentUser'
import { canAccess } from '../../features/auth/permissions'

export function HomePage() {
  const user = useCurrentUser()

  if (user.role === 'STUDENT') return <StudentPortalPage />
  if (user.role === 'ADMIN') return <DashboardPage />

  // Le tableau de bord appelle des routes réservées à ADMIN :
  // les rôles financiers arrivent directement sur leur espace.
  if (canAccess(user.role, 'finance')) {
    return <Navigate to="/app/finance" replace />
  }

  return (
    <section role="alert">
      <h1>Aucun espace disponible</h1>
      <p>Votre rôle n'a pas encore d'écran associé dans cette application.</p>
    </section>
  )
}