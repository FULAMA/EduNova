import type { ReactNode } from 'react'

import type { AuthenticatedUser } from '../services/auth.service'
import { CurrentUserContext } from './current-user.context'

export function CurrentUserProvider({
  user,
  children,
}: {
  user: AuthenticatedUser
  children?: ReactNode
}) {
  return (
    <CurrentUserContext.Provider value={user}>
      {children}
    </CurrentUserContext.Provider>
  )
}
