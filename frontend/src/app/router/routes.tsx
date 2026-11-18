import type { ReactNode } from 'react'
import { Navigate, type RouteObject } from 'react-router-dom'

import { RequireAuth } from '../../features/auth/components/RequireAuth'
import { RequireRole } from '../../features/auth/components/RequireRole'
import type { AppModule } from '../../features/auth/permissions'
import LoginPage from '../../features/auth/pages/LoginPage'
import RegisterEstablishmentPage from '../../features/auth/pages/RegisterEstablishmentPage'
import TenantSelectionPage from '../../features/auth/pages/TenantSelectionPage'
import TwoFactorPage from '../../features/auth/pages/TwoFactorPage'
import StudentsPage from '../../features/students/pages/StudentsPage/StudentsPage'
import StudentPortalPage from '../../features/students/pages/StudentPortalPage/StudentPortalPage'
import StudentDetailPage from '../../features/students/pages/StudentDetailPage/StudentDetailPage'
import ParentPortalPage from '../../features/parents/ParentPortalPage'
import TeacherPortalPage from '../../features/teachers/TeacherPortalPage'
import { AppShell } from '../../shared/components/AppShell/AppShell'
import AcademicCataloguesPage from '../../features/academic-catalogues/AcademicCataloguesPage'
import ClassesPage from '../../features/classes/ClassesPage'
import EnrollmentsPage from '../../features/enrollments/EnrollmentsPage'
import AttendancePage from '../../features/attendance/AttendancePage'
import FinancePage from '../../features/finance/FinancePage'
import { NotFoundPage } from '../../shared/components/NotFoundPage/NotFoundPage'
import { HomePage } from './HomePage'

// Preview routes - only included in development builds
// In production, Vite will dead-code-eliminate this entire block
const previewRoutes: RouteObject[] = import.meta.env.DEV
  ? [
      {
        path: '/preview',
        lazy: async () => {
          const { PreviewLayout } = await import('../../features/preview/components/PreviewLayout')
          return { Component: PreviewLayout }
        },
        children: [
          {
            index: true,
            lazy: async () => {
              const { PreviewDashboard } = await import('../../features/preview/pages/PreviewDashboard')
              return { Component: PreviewDashboard }
            },
          },
        ],
      },
    ]
  : []

function guarded(module: AppModule, element: ReactNode): ReactNode {
  return <RequireRole module={module}>{element}</RequireRole>
}

export const routes: RouteObject[] = [
  ...previewRoutes,
  { path: '/', element: <Navigate to="/app" replace /> },
  { path: '/login', element: <LoginPage /> },
  { path: '/register', element: <RegisterEstablishmentPage /> },
  { path: '/register-establishment', element: <Navigate to="/register" replace /> },
  { path: '/login/select-tenant', element: <TenantSelectionPage /> },
  { path: '/login/2fa', element: <TwoFactorPage /> },
  {
    path: '/app',
    element: (
      <RequireAuth>
        <AppShell />
      </RequireAuth>
    ),
    children: [
      { index: true, element: <HomePage /> },
      { path: 'students', element: guarded('students', <StudentsPage />) },
      { path: 'students/:studentId', element: guarded('students', <StudentDetailPage />) },
      { path: 'academic-catalogues', element: guarded('academic-catalogues', <AcademicCataloguesPage />) },
      { path: 'classes', element: guarded('classes', <ClassesPage />) },
      { path: 'enrollments', element: guarded('enrollments', <EnrollmentsPage />) },
      { path: 'attendance', element: guarded('attendance', <AttendancePage />) },
      { path: 'finance', element: guarded('finance', <FinancePage />) },
      { path: 'parent-portal', element: guarded('parent-portal', <ParentPortalPage />) },
      { path: 'student-portal', element: guarded('student-portal', <StudentPortalPage />) },
      { path: 'teacher-portal', element: guarded('teacher-portal', <TeacherPortalPage />) },
      { path: '*', element: <NotFoundPage /> },
    ],
  },
  { path: '*', element: <NotFoundPage /> },
]
