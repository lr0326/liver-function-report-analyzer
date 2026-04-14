import { formatRiskScore } from '../utils/formatters'

function StatItem({ label, value, highlight }) {
  return (
    <div className="flex items-center justify-between py-2 border-b border-gray-100 dark:border-gray-700 last:border-0">
      <span className="text-sm text-gray-500 dark:text-gray-400">{label}</span>
      <span
        className={[
          'text-sm font-semibold',
          highlight ? 'text-red-600 dark:text-red-400' : 'text-gray-900 dark:text-white',
        ].join(' ')}
      >
        {value}
      </span>
    </div>
  )
}

export default function AnalysisSummary({ analysis }) {
  if (!analysis) return null

  const riskInfo = formatRiskScore(analysis.riskScore)
  const abnormalCount = analysis.abnormalCount ?? 0
  const totalCount = analysis.totalCount ?? 0
  const normalCount = totalCount - abnormalCount

  return (
    <div className="space-y-4">
      {/* Overall assessment */}
      {analysis.overallAssessment && (
        <div className="p-4 rounded-xl bg-blue-50 dark:bg-blue-900/20 border border-blue-100 dark:border-blue-800">
          <div className="flex gap-2">
            <svg className="w-5 h-5 text-blue-500 flex-shrink-0 mt-0.5" fill="currentColor" viewBox="0 0 20 20">
              <path fillRule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2v-3a1 1 0 00-1-1H9z" clipRule="evenodd" />
            </svg>
            <div>
              <p className="text-sm font-semibold text-blue-800 dark:text-blue-200 mb-1">综合评估</p>
              <p className="text-sm text-blue-700 dark:text-blue-300 leading-relaxed">
                {analysis.overallAssessment}
              </p>
            </div>
          </div>
        </div>
      )}

      {/* Stats */}
      <div className="rounded-xl border border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-800 px-4 py-2">
        <StatItem label="检测指标总数" value={`${totalCount} 项`} />
        <StatItem label="正常指标" value={`${normalCount} 项`} />
        <StatItem label="异常指标" value={`${abnormalCount} 项`} highlight={abnormalCount > 0} />
        <StatItem
          label="风险等级"
          value={
            <span className={`${riskInfo.bgClass} ${riskInfo.colorClass} px-2 py-0.5 rounded-full text-xs font-semibold`}>
              {riskInfo.icon} {riskInfo.label}
            </span>
          }
        />
      </div>

      {/* Key findings */}
      {analysis.keyFindings?.length > 0 && (
        <div>
          <h4 className="text-sm font-semibold text-gray-700 dark:text-gray-300 mb-2">
            主要发现
          </h4>
          <ul className="space-y-1.5">
            {analysis.keyFindings.map((finding, i) => (
              <li
                key={i}
                className="flex items-start gap-2 text-sm text-gray-600 dark:text-gray-400"
              >
                <svg className="w-4 h-4 text-amber-500 flex-shrink-0 mt-0.5" fill="currentColor" viewBox="0 0 20 20">
                  <path fillRule="evenodd" d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z" clipRule="evenodd" />
                </svg>
                {finding}
              </li>
            ))}
          </ul>
        </div>
      )}
    </div>
  )
}
