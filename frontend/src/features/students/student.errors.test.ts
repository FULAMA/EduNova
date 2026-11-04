import { describe, expect, it } from 'vitest'

import { ApiError } from '../../shared/api/client'
import { describeStudentError } from './student.errors'

describe('describeStudentError', () => {
  it('keeps a fixed message for forbidden and expired sessions', () => {
    expect(describeStudentError(new ApiError(403, 'Acces interdit.'), 'x')).toBe(
      'Votre rôle ne permet pas de gérer les élèves.',
    )
    expect(describeStudentError(new ApiError(401, 'Token invalide.'), 'x')).toBe(
      'Votre session a expiré. Reconnectez-vous.',
    )
  })

  it('surfaces validation messages from the API', () => {
    expect(
      describeStudentError(new ApiError(400, 'Le prenom ne peut pas etre vide.'), 'x'),
    ).toBe('Le prenom ne peut pas etre vide.')
  })
})
