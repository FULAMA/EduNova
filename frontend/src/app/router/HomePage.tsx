import { Navigate } from 'react-router-dom'

import DashboardPage from '../../features/dashboard/pages/DashboardPage'
import StudentPortalPage from '../../features/students/pages/StudentPortalPage/StudentPortalPage'
import { useCurrentUser } from '../../features/auth/components/useCurrentUser'
import { canAccess } from '../../features/auth/permissions'

export function HomePage() {
  const user = useCurrentUser()

  if (user.role === 'STUDENT') return <StudentPortalPage />
  if (user.role === 'PARENT') return <Navigate to="/app/parent-portal" replace />
  if (user.role === 'PROF' || user.role === 'TEACHER') {
    return <Navigate to="/app/teacher-portal" replace />
  }
  if (user.role === 'ADMIN' || user.role === 'DIRECTION') return <DashboardPage />

  // Les rôles financiers exclusifs (ACCOUNTANT, CASHIER) arrivent directement sur leur espace.
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
