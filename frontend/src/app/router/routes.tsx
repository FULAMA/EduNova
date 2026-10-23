import { Navigate, type RouteObject } from 'react-router-dom'

import { RequireAuth } from '../../features/auth/components/RequireAuth'
import LoginPage from '../../features/auth/pages/LoginPage'
import StudentsPage from '../../features/students/pages/StudentsPage/StudentsPage'
import StudentDetailPage from '../../features/students/pages/StudentDetailPage/StudentDetailPage'
import { AppShell } from '../../shared/components/AppShell/AppShell'
import AcademicCataloguesPage from '../../features/academic-catalogues/AcademicCataloguesPage'
import ClassesPage from '../../features/classes/ClassesPage'
import EnrollmentsPage from '../../features/enrollments/EnrollmentsPage'
import AttendancePage from '../../features/attendance/AttendancePage'
import FinancePage from '../../features/finance/FinancePage'
import { NotFoundPage } from '../../shared/components/NotFoundPage/NotFoundPage'
import { HomePage } from './HomePage'

export const routes: RouteObject[] = [
  {
    path: '/',
    element: <Navigate to="/app" replace />,
  },
  {
    path: '/login',
    element: <LoginPage />,
  },
  {
    path: '/app',
    element: (
      <RequireAuth>
        <AppShell />
      </RequireAuth>
    ),
    children: [
      {
        index: true,
        element: <HomePage />,
      },
      {
        path: 'students',
        element: <StudentsPage />,
      },
      {
        path: 'students/:studentId',
        element: <StudentDetailPage />,
      },
      {
        path: 'academic-catalogues',
        element: <AcademicCataloguesPage />,
      },
      {
        path: 'classes',
        element: <ClassesPage />,
      },
      {
        path: 'enrollments',
        element: <EnrollmentsPage />,
      },
      {
        path: 'attendance',
        element: <AttendancePage />,
      },
      {
        path: 'finance',
        element: <FinancePage />,
      },
      {
        path: '*',
        element: <NotFoundPage />,
      },
    ],
  },
  {
    path: '*',
    element: <NotFoundPage />,
  },
]
