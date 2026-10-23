export type StudentStatus = 'active' | 'inactive'

export type Student = {
  id: string
  firstName: string
  lastName: string
  email?: string | null
  status: StudentStatus
  studentNumber?: string
  className?: string
}
