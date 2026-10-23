import DashboardPage from '../../features/dashboard/pages/DashboardPage'
import StudentPortalPage from '../../features/students/pages/StudentPortalPage/StudentPortalPage'
import { useCurrentUser } from '../../features/auth/components/useCurrentUser'

export function HomePage() {
  const user = useCurrentUser()
  return user.role === 'STUDENT' ? <StudentPortalPage /> : <DashboardPage />
}
