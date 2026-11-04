export type AppModule =
  | 'dashboard'
  | 'students'
  | 'classes'
  | 'enrollments'
  | 'attendance'
  | 'finance'
  | 'academic-catalogues'

const FINANCE_ROLES = ['ADMIN', 'DIRECTION', 'ACCOUNTANT', 'CASHIER'] as const
const STUDENT_DIRECTORY_ROLES = ['ADMIN', 'DIRECTION'] as const

// Miroir de require_role() côté backend. Le backend reste l'autorité :
// cette matrice sert uniquement à ne pas proposer des écrans voués au 403.
const MODULE_ROLES: Record<AppModule, readonly string[]> = {
  dashboard: ['ADMIN', 'DIRECTION', 'ACCOUNTANT', 'CASHIER', 'STUDENT'],
  students: STUDENT_DIRECTORY_ROLES,
  classes: ['ADMIN'],
  enrollments: ['ADMIN'],
  attendance: ['ADMIN'],
  'academic-catalogues': ['ADMIN'],
  finance: FINANCE_ROLES,
}

export function canAccess(role: string | undefined, module: AppModule): boolean {
  return role !== undefined && MODULE_ROLES[module].includes(role)
}

const FEE_CATALOG_MANAGERS: readonly string[] = ['ADMIN', 'DIRECTION']

// Miroir de FINANCE_MANAGEMENT_ROLES (backend) : création, publication, archivage, attribution.
export function canManageFeeCatalog(role: string | undefined): boolean {
  return role !== undefined && FEE_CATALOG_MANAGERS.includes(role)
}

export function canManageStudents(role: string | undefined): boolean {
  return role !== undefined && STUDENT_DIRECTORY_ROLES.includes(role as never)
}