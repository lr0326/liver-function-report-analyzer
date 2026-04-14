import { useState, useCallback } from 'react'

export function useApi(apiFunc) {
  const [data, setData] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)

  const execute = useCallback(
    async (...args) => {
      setLoading(true)
      setError(null)
      try {
        const result = await apiFunc(...args)
        setData(result)
        return { data: result, error: null }
      } catch (err) {
        const errorMessage = err.message || '请求失败'
        setError(errorMessage)
        return { data: null, error: errorMessage }
      } finally {
        setLoading(false)
      }
    },
    [apiFunc]
  )

  const reset = useCallback(() => {
    setData(null)
    setLoading(false)
    setError(null)
  }, [])

  return { data, loading, error, execute, reset }
}
