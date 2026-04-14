import Navbar from './Navbar'
import Sidebar from './Sidebar'
import { useApp } from '../../context/AppContext'
import Alert from '../common/Alert'

function NotificationStack() {
  const { notifications, removeNotification } = useApp()
  if (!notifications.length) return null

  return (
    <div className="fixed bottom-4 right-4 z-50 flex flex-col gap-2 max-w-sm w-full no-print">
      {notifications.map((n) => (
        <Alert
          key={n.id}
          type={n.type}
          message={n.message}
          dismissible
          onDismiss={() => removeNotification(n.id)}
          className="shadow-lg"
        />
      ))}
    </div>
  )
}

export default function Layout({ children, sidebar = false }) {
  return (
    <div className="min-h-screen flex flex-col bg-gray-50 dark:bg-gray-900 transition-colors duration-200">
      <Navbar />

      <div className="flex flex-1 overflow-hidden">
        {sidebar && <Sidebar />}

        <main className="flex-1 overflow-auto">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
            {children}
          </div>
        </main>
      </div>

      <footer className="bg-white dark:bg-gray-800 border-t border-gray-200 dark:border-gray-700 py-4 no-print">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <p className="text-center text-xs text-gray-400 dark:text-gray-500">
            © {new Date().getFullYear()} 肝功能报告分析系统 &nbsp;·&nbsp; 本系统仅供参考，不构成医疗诊断依据
          </p>
        </div>
      </footer>

      <NotificationStack />
    </div>
  )
}
