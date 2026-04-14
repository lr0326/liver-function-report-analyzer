import { useState, useMemo } from 'react'
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ReferenceArea,
  ResponsiveContainer,
} from 'recharts'
import { INDICATOR_INFO } from '../constants/indicators'
import { formatDate } from '../utils/formatters'

const COLORS = ['#3b82f6', '#10b981', '#f59e0b', '#ef4444', '#8b5cf6', '#06b6d4']

function CustomTooltip({ active, payload, label }) {
  if (!active || !payload?.length) return null
  return (
    <div className="bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-600 rounded-lg shadow-lg p-3 text-sm">
      <p className="font-medium text-gray-700 dark:text-gray-300 mb-2">{label}</p>
      {payload.map((p, i) => (
        <div key={i} className="flex items-center gap-2">
          <div className="w-2.5 h-2.5 rounded-full" style={{ backgroundColor: p.color }} />
          <span className="text-gray-600 dark:text-gray-400">{p.name}:</span>
          <span className="font-semibold text-gray-900 dark:text-white">
            {p.value} {INDICATOR_INFO[p.dataKey]?.unit || ''}
          </span>
        </div>
      ))}
    </div>
  )
}

export default function TrendChart({ data = [], selectedIndicators }) {
  const availableKeys = useMemo(() => {
    if (!data.length) return []
    const keys = new Set()
    data.forEach((d) => {
      Object.keys(d).forEach((k) => {
        if (k !== 'date' && k !== 'label') keys.add(k)
      })
    })
    return Array.from(keys)
  }, [data])

  const [activeKeys, setActiveKeys] = useState(
    () => selectedIndicators || availableKeys.slice(0, 3)
  )

  const toggleKey = (key) => {
    setActiveKeys((prev) =>
      prev.includes(key) ? prev.filter((k) => k !== key) : [...prev, key]
    )
  }

  const formattedData = useMemo(
    () =>
      data.map((d) => ({
        ...d,
        label: d.label || formatDate(d.date),
      })),
    [data]
  )

  if (!data.length) {
    return (
      <div className="flex items-center justify-center h-48 text-gray-400 dark:text-gray-500">
        <div className="text-center">
          <svg className="w-10 h-10 mx-auto mb-2 opacity-40" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5}
              d="M7 12l3-3 3 3 4-4M8 21l4-4 4 4M3 4h18M4 4h16v12a1 1 0 01-1 1H5a1 1 0 01-1-1V4z" />
          </svg>
          <p className="text-sm">暂无趋势数据</p>
        </div>
      </div>
    )
  }

  return (
    <div className="space-y-4">
      {/* Indicator selector */}
      <div className="flex flex-wrap gap-2">
        {availableKeys.map((key, i) => {
          const info = INDICATOR_INFO[key]
          const isActive = activeKeys.includes(key)
          const color = COLORS[i % COLORS.length]
          return (
            <button
              key={key}
              onClick={() => toggleKey(key)}
              className={[
                'flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-medium border transition-all',
                isActive
                  ? 'text-white border-transparent shadow-sm'
                  : 'bg-white dark:bg-gray-800 text-gray-500 dark:text-gray-400 border-gray-200 dark:border-gray-600',
              ].join(' ')}
              style={isActive ? { backgroundColor: color, borderColor: color } : {}}
            >
              <span
                className="w-2 h-2 rounded-full"
                style={{ backgroundColor: isActive ? 'white' : color }}
              />
              {info?.shortName || key}
            </button>
          )
        })}
      </div>

      {/* Chart */}
      <ResponsiveContainer width="100%" height={280}>
        <LineChart data={formattedData} margin={{ top: 5, right: 20, left: 0, bottom: 5 }}>
          <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" className="dark:opacity-20" />
          <XAxis
            dataKey="label"
            tick={{ fontSize: 12, fill: '#6b7280' }}
            tickLine={false}
            axisLine={{ stroke: '#e5e7eb' }}
          />
          <YAxis
            tick={{ fontSize: 12, fill: '#6b7280' }}
            tickLine={false}
            axisLine={false}
            width={40}
          />
          <Tooltip content={<CustomTooltip />} />
          <Legend
            formatter={(value) => INDICATOR_INFO[value]?.shortName || value}
            wrapperStyle={{ fontSize: '12px' }}
          />

          {activeKeys.map((key, i) => {
            const info = INDICATOR_INFO[key]
            const color = COLORS[i % COLORS.length]
            return (
              <Line
                key={key}
                type="monotone"
                dataKey={key}
                stroke={color}
                strokeWidth={2}
                dot={{ r: 4, fill: color, strokeWidth: 2, stroke: 'white' }}
                activeDot={{ r: 6 }}
                name={info?.shortName || key}
              />
            )
          })}

          {/* Reference areas for normal range of first active indicator */}
          {activeKeys[0] && INDICATOR_INFO[activeKeys[0]]?.normalRange && (() => {
            const { min, max } = INDICATOR_INFO[activeKeys[0]].normalRange
            return (
              <ReferenceArea
                y1={min}
                y2={max}
                fill="#10b981"
                fillOpacity={0.05}
                stroke="#10b981"
                strokeOpacity={0.2}
                label={{ value: '正常范围', fontSize: 10, fill: '#10b981', position: 'insideTopRight' }}
              />
            )
          })()}
        </LineChart>
      </ResponsiveContainer>
    </div>
  )
}
