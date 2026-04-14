import { INDICATOR_INFO } from '../constants/indicators'
import { getIndicatorStatus, getStatusConfig } from '../utils/formatters'

function StatusBadge({ value, normalRange }) {
  const status = getIndicatorStatus(value, normalRange)
  const config = getStatusConfig(status)
  return (
    <span className={`inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-xs font-medium ${config.bgClass} ${config.textClass}`}>
      <span className={`w-1.5 h-1.5 rounded-full ${config.dot}`} />
      {config.label}
    </span>
  )
}

export default function IndicatorTable({ indicators = [] }) {
  if (!indicators.length) {
    return (
      <div className="flex items-center justify-center py-12 text-gray-400 dark:text-gray-500">
        <div className="text-center">
          <svg className="w-12 h-12 mx-auto mb-3 opacity-40" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5}
              d="M9 17v-2m3 2v-4m3 4v-6m2 10H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
          </svg>
          <p className="text-sm">暂无指标数据</p>
        </div>
      </div>
    )
  }

  return (
    <div className="overflow-x-auto rounded-xl border border-gray-200 dark:border-gray-700">
      <table className="min-w-full divide-y divide-gray-200 dark:divide-gray-700">
        <thead>
          <tr className="bg-gray-50 dark:bg-gray-800/50">
            {['指标', '数值', '单位', '参考范围', '状态'].map((h) => (
              <th
                key={h}
                className="px-4 py-3 text-left text-xs font-semibold text-gray-500 dark:text-gray-400 uppercase tracking-wider"
              >
                {h}
              </th>
            ))}
          </tr>
        </thead>
        <tbody className="bg-white dark:bg-gray-800 divide-y divide-gray-100 dark:divide-gray-700/50">
          {indicators.map((item) => {
            const info = INDICATOR_INFO[item.key] || {}
            const normalRange = info.normalRange || {}
            const status = getIndicatorStatus(item.value, normalRange)
            const isAbnormal = status !== 'normal' && status !== 'unknown'

            return (
              <tr
                key={item.key}
                className={[
                  'transition-colors',
                  isAbnormal
                    ? 'bg-red-50/40 dark:bg-red-900/10 hover:bg-red-50/70 dark:hover:bg-red-900/20'
                    : 'hover:bg-gray-50 dark:hover:bg-gray-700/30',
                ].join(' ')}
              >
                <td className="px-4 py-3">
                  <div>
                    <p className="text-sm font-medium text-gray-900 dark:text-white">
                      {info.shortName || item.key}
                    </p>
                    <p className="text-xs text-gray-400 dark:text-gray-500">{info.name || ''}</p>
                  </div>
                </td>
                <td className="px-4 py-3">
                  <span
                    className={[
                      'text-sm font-semibold tabular-nums',
                      isAbnormal ? 'text-red-600 dark:text-red-400' : 'text-gray-900 dark:text-white',
                    ].join(' ')}
                  >
                    {item.value ?? '—'}
                  </span>
                </td>
                <td className="px-4 py-3 text-sm text-gray-500 dark:text-gray-400">
                  {info.unit || item.unit || '—'}
                </td>
                <td className="px-4 py-3 text-sm text-gray-500 dark:text-gray-400 whitespace-nowrap">
                  {normalRange.min !== undefined && normalRange.max !== undefined
                    ? `${normalRange.min} – ${normalRange.max}`
                    : item.referenceRange || '—'}
                </td>
                <td className="px-4 py-3">
                  <StatusBadge value={item.value} normalRange={normalRange} />
                </td>
              </tr>
            )
          })}
        </tbody>
      </table>
    </div>
  )
}
