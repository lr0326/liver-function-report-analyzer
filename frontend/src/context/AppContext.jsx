import { createContext, useContext, useState, useCallback, useEffect } from 'react'

const AppContext = createContext(null)

const MOCK_USER = {
  id: 'user_001',
  name: '张三',
  email: 'zhangsan@example.com',
  avatar: null,
}

export function AppProvider({ children }) {
  const [currentReport, setCurrentReport] = useState(null)
  const [reports, setReports] = useState([])
  const [notifications, setNotifications] = useState([])
  const [theme, setTheme] = useState(() => {
    if (typeof window !== 'undefined') {
      return localStorage.getItem('theme') || 'light'
    }
    return 'light'
  })
  const [user] = useState(MOCK_USER)

  // Apply theme class to html element
  useEffect(() => {
    const root = document.documentElement
    if (theme === 'dark') {
      root.classList.add('dark')
    } else {
      root.classList.remove('dark')
    }
    localStorage.setItem('theme', theme)
  }, [theme])

  const toggleTheme = useCallback(() => {
    setTheme((prev) => (prev === 'light' ? 'dark' : 'light'))
  }, [])

  const addReport = useCallback((report) => {
    setReports((prev) => [report, ...prev])
  }, [])

  const addNotification = useCallback((notification) => {
    const id = Date.now().toString()
    const newNotification = { id, ...notification }
    setNotifications((prev) => [newNotification, ...prev.slice(0, 4)])

    if (notification.autoClose !== false) {
      setTimeout(() => {
        setNotifications((prev) => prev.filter((n) => n.id !== id))
      }, notification.duration || 4000)
    }

    return id
  }, [])

  const removeNotification = useCallback((id) => {
    setNotifications((prev) => prev.filter((n) => n.id !== id))
  }, [])

  const value = {
    currentReport,
    setCurrentReport,
    reports,
    addReport,
    notifications,
    addNotification,
    removeNotification,
    theme,
    toggleTheme,
    user,
  }

  return <AppContext.Provider value={value}>{children}</AppContext.Provider>
}

export function useApp() {
  const context = useContext(AppContext)
  if (!context) {
    throw new Error('useApp must be used within AppProvider')
  }
  return context
}
