import { Routes, Route } from 'react-router-dom'
import Home from '../pages/Home'
import Upload from '../pages/Upload'
import Results from '../pages/Results'
import Dashboard from '../pages/Dashboard'
import ReportHistory from '../pages/ReportHistory'

function NotFound() {
  return (
    <div className="min-h-screen flex flex-col items-center justify-center bg-gray-50 dark:bg-gray-900 text-center px-4">
      <div className="text-8xl mb-4">🔍</div>
      <h1 className="text-4xl font-bold text-gray-900 dark:text-white mb-2">404</h1>
      <p className="text-lg text-gray-500 dark:text-gray-400 mb-6">页面不存在</p>
      <a
        href="/"
        className="px-5 py-2.5 bg-blue-600 hover:bg-blue-700 text-white rounded-xl font-medium transition-colors"
      >
        返回首页
      </a>
    </div>
  )
}

export default function AppRoutes() {
  return (
    <Routes>
      <Route path="/"                  element={<Home />} />
      <Route path="/upload"            element={<Upload />} />
      <Route path="/results/:reportId" element={<Results />} />
      <Route path="/dashboard"         element={<Dashboard />} />
      <Route path="/history"           element={<ReportHistory />} />
      <Route path="*"                  element={<NotFound />} />
    </Routes>
  )
}
