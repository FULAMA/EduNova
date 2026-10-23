import type { DashboardSummary } from '../types/dashboard.types'

export const demoDashboardSummary: DashboardSummary = {
  students: {
    label: 'Élèves',
    value: '1 248',
    description: 'Élèves inscrits',
  },
  classes: {
    label: 'Classes',
    value: '32',
    description: 'Classes actives',
  },
  teachers: {
    label: 'Enseignants',
    value: '84',
    description: 'Enseignants actifs',
  },
  attendance: {
    label: 'Présence',
    value: '94,2 %',
    description: 'Taux de présence',
  },
}
