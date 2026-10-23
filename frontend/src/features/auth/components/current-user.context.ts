import { createContext } from 'react'

import type { AuthenticatedUser } from '../services/auth.service'

export const CurrentUserContext = createContext<AuthenticatedUser | null>(null)
