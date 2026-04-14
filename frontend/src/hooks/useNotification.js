import { useCallback } from 'react'
import { useApp } from '../context/AppContext'

export function useNotification() {
  const { addNotification, removeNotification, notifications } = useApp()

  const notify = useCallback(
    (message, type = 'info', options = {}) => {
      return addNotification({ message, type, ...options })
    },
    [addNotification]
  )

  const success = useCallback(
    (message, options = {}) => notify(message, 'success', options),
    [notify]
  )

  const error = useCallback(
    (message, options = {}) => notify(message, 'error', { duration: 6000, ...options }),
    [notify]
  )

  const warning = useCallback(
    (message, options = {}) => notify(message, 'warning', options),
    [notify]
  )

  const info = useCallback(
    (message, options = {}) => notify(message, 'info', options),
    [notify]
  )

  return { notify, success, error, warning, info, removeNotification, notifications }
}
