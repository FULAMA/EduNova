import { useContext } from 'react'

import type { AuthenticatedUser } from '../services/auth.service'
import { CurrentUserContext } from './current-user.context'

export function useCurrentUser(): AuthenticatedUser {
  const user = useContext(CurrentUserContext)

  if (!user) {
    throw new Error('useCurrentUser must be used inside CurrentUserProvider')
  }

  return user
}
