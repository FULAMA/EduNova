import type { StudentStatus } from '../../types/student.types'

export type StudentFiltersValue = {
  search: string
  status: StudentStatus | 'all'
}

export type StudentFiltersProps = {
  value: StudentFiltersValue
  onChange: (value: StudentFiltersValue) => void
}
