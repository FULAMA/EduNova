import { ApiError } from '../../shared/api/client'

export function describeStudentError(reason: unknown, fallback: string): string {
  if (reason instanceof ApiError) {
    if (reason.status === 401) return 'Votre session a expiré. Reconnectez-vous.'
    if (reason.status === 403) return 'Votre rôle ne permet pas de gérer les élèves.'
    if ([0, 400, 404, 409, 422].includes(reason.status)) return reason.message
  }
  return fallback
}
