import type { AuthenticatedUser } from '../../../features/auth/services/auth.service'
import type { DashboardMetric } from '../../dashboard/types/dashboard.types'

// Utilisateur fictif pour le mode démo
export const DEMO_USER: AuthenticatedUser = {
  id: 'demo-admin-0000-0000-0000-000000000000',
  email: 'admin@edunova-demo.local',
  role: 'ADMIN',
  is_active: true,
  two_factor_enabled: false,
}

// Données fictives pour les métriques du dashboard
export const DEMO_METRICS: DashboardMetric[] = [
  {
    label: 'Élèves inscrits',
    value: '248',
    description: '215 actifs sur 248',
  },
  {
    label: 'Classes pédagogiques',
    value: '12',
    description: '12 classes configurées',
  },
  {
    label: 'Matières enseignées',
    value: '18',
    description: 'Catalogue actif de l’établissement',
  },
  {
    label: 'Année scolaire active',
    value: '2024-2025',
    description: 'Du 01/09/2024 au 30/06/2025',
  },
]

// Liens rapides pour la démo
export type PreviewQuickLink = {
  badge: string
  title: string
  description: string
}

export const DEMO_QUICK_LINKS: PreviewQuickLink[] = [
  {
    badge: 'Années & Affectations',
    title: 'Inscriptions',
    description: 'Activer une année scolaire, inscrire des élèves et gérer le cycle de vie des affectations.',
  },
  {
    badge: 'Structure scolaire',
    title: 'Classes & Matières',
    description: 'Consulter les promotions, associer les matières et définir les coefficients.',
  },
  {
    badge: 'Scolarité',
    title: 'Élèves & Dossiers',
    description: 'Accéder à la liste des élèves, fiches individuelles et parcours académiques.',
  },
  {
    badge: 'Pédagogie',
    title: 'Catalogue & Périodes',
    description: 'Définir les matières au niveau établissement et consulter les périodes académiques.',
  },
  {
    badge: 'Suivi scolaire',
    title: 'Présences & Risque',
    description: 'Enregistrer les présences et suivre le risque académique calculé.',
  },
]
