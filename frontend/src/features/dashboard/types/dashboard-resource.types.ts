export type DashboardResourceStatus =
  | 'loading'
  | 'success'
  | 'empty'
  | 'error'

export type DashboardResourceState<T> =
  | {
      status: 'loading'
      data: null
      error: null
    }
  | {
      status: 'success'
      data: T
      error: null
    }
  | {
      status: 'empty'
      data: null
      error: null
    }
  | {
      status: 'error'
      data: null
      error: string
    }
