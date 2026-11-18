import { ApiError } from './client'

export { ApiError }

/**
 * Describe an API error in a user-friendly way.
 * Handles both ApiError instances and generic errors.
 */
export function describeAuthError(error: unknown): { message: string; status?: number } {
  if (error instanceof ApiError) {
    return { message: error.message, status: error.status }
  }

  if (error instanceof Error) {
    return { message: error.message }
  }

  return { message: 'Une erreur inconnue est survenue.' }
}
