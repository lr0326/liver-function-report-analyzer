import { Link } from 'react-router-dom'
import { formatDate, formatRiskScore } from '../utils/formatters'

const STATUS_CONFIG = {
  completed:  { label: '已完成', dot: 'bg-emerald-500', text: 'text-emerald-600 dark:text-emerald-400' },
  processing: { label: '分析中', dot: 'bg-blue-500 animate-pulse', text: 'text-blue-600 dark:text-blue-400' },
  error:      { label: '处理失败', dot: 'bg-red-500', text: 'text-red-600 dark:text-red-400' },
  pending:    { label: '等待处理', dot: 'bg-gray-400', text: 'text-gray-500 dark:text-gray-400' },
}

function ReportCard({ report }) {
  const statusConfig = STATUS_CONFIG[report.status] || STATUS_CONFIG.pending
  const riskInfo = report.riskScore !== undefined ? formatRiskScore(report.riskScore) : null

  return (
    <div className="bg-white dark:bg-gray-800 rounded-xl border border-gray-200 dark:border-gray-700 p-4 hover:shadow-md transition-all duration-200 hover:-translate-y-0.5">
      <div className="flex items-start justify-between gap-3">
        <div className="flex items-start gap-3 min-w-0">
          {/* File icon */}
          <div className="w-10 h-10 rounded-lg bg-blue-50 dark:bg-blue-900/30 flex items-center justify-center flex-shrink-0">
            <svg className="w-5 h-5 text-blue-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5}
                d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
            </svg>
          </div>
          <div className="min-w-0">
            <p className="text-sm font-medium text-gray-900 dark:text-white truncate">
              {report.fileName || `报告 #${report.id?.slice(-6) || '未知'}`}
            </p>
            <p className="text-xs text-gray-400 dark:text-gray-500 mt-0.5">
              {formatDate(report.createdAt || report.date)}
            </p>
          </div>
        </div>

        {/* Risk score badge */}
        {riskInfo && (
          <span className={`flex-shrink-0 text-xs px-2 py-0.5 rounded-full font-semibold ${riskInfo.bgClass}`}>
            {Math.round(report.riskScore)}分
          </span>
        )}
      </div>

      <div className="mt-3 flex items-center justify-between">
        {/* Status */}
        <div className={`flex items-center gap-1.5 text-xs font-medium ${statusConfig.text}`}>
          <div className={`w-1.5 h-1.5 rounded-full ${statusConfig.dot}`} />
          {statusConfig.label}
        </div>

        {/* Action */}
        {report.status === 'completed' ? (
          <Link
            to={`/results/${report.id}`}
            className="text-xs font-medium text-blue-600 dark:text-blue-400 hover:text-blue-700 dark:hover:text-blue-300 flex items-center gap-1 transition-colors"
          >
            查看详情
            <svg className="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
            </svg>
          </Link>
        ) : (
          <span className="text-xs text-gray-400">—</span>
        )}
      </div>
    </div>
  )
}

export default function ReportList({ reports = [], emptyText = '暂无报告记录' }) {
  if (!reports.length) {
    return (
      <div className="flex flex-col items-center justify-center py-12 text-center text-gray-400 dark:text-gray-500">
        <svg className="w-14 h-14 mb-3 opacity-40" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5}
            d="M9 13h6m-3-3v6m5 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
        </svg>
        <p className="text-sm">{emptyText}</p>
        <Link to="/upload" className="mt-3 text-sm text-blue-600 dark:text-blue-400 hover:underline">
          立即上传报告 →
        </Link>
      </div>
    )
  }

  return (
    <div className="grid grid-cols-1 sm:grid-cols-2 xl:grid-cols-3 gap-3">
      {reports.map((report) => (
        <ReportCard key={report.id} report={report} />
      ))}
    </div>
  )
}
