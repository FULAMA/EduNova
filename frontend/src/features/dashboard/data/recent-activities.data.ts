import type { DashboardRecentActivities } from '../types/recent-activity.types'

export const demoRecentActivities: DashboardRecentActivities = {
  activities: [
    {
      id: 'activity-001',
      title: 'Nouvel élève inscrit',
      description: 'Une nouvelle inscription a été enregistrée.',
      occurredAt: 'Il y a 10 min',
    },
    {
      id: 'activity-002',
      title: 'Classe créée',
      description: 'La classe 6e des Humanités a été ajoutée.',
      occurredAt: 'Il y a 25 min',
    },
    {
      id: 'activity-003',
      title: 'Note enregistrée',
      description: 'Une nouvelle évaluation a été enregistrée.',
      occurredAt: 'Il y a 42 min',
    },
    {
      id: 'activity-004',
      title: 'Bulletin généré',
      description: 'Un bulletin scolaire a été généré.',
      occurredAt: 'Il y a 1 h',
    },
  ],
}
