import { PieChart, Pie, Cell, ResponsiveContainer } from 'recharts'
import { getRiskLevel } from '../utils/formatters'

function getScoreColor(score) {
  if (score >= 80) return '#ef4444'
  if (score >= 60) return '#f97316'
  if (score >= 30) return '#f59e0b'
  return '#10b981'
}

export default function RiskScoreDisplay({ score = 0, size = 'md' }) {
  const level = getRiskLevel(score)
  const color = getScoreColor(score)
  const remaining = 100 - score

  const data = [
    { value: score,     fill: color },
    { value: remaining, fill: '#e5e7eb' },
  ]

  const dims = { sm: 140, md: 180, lg: 220 }
  const dim = dims[size] || dims.md
  const innerRadius = dim * 0.32
  const outerRadius = dim * 0.45

  return (
    <div className="flex flex-col items-center gap-3">
      <div className="relative" style={{ width: dim, height: dim }}>
        <ResponsiveContainer width="100%" height="100%">
          <PieChart>
            <Pie
              data={data}
              cx="50%"
              cy="50%"
              startAngle={90}
              endAngle={-270}
              innerRadius={innerRadius}
              outerRadius={outerRadius}
              dataKey="value"
              strokeWidth={0}
            >
              {data.map((entry, index) => (
                <Cell key={index} fill={index === 1 ? 'var(--gauge-bg, #e5e7eb)' : entry.fill} />
              ))}
            </Pie>
          </PieChart>
        </ResponsiveContainer>

        {/* Center text */}
        <div className="absolute inset-0 flex flex-col items-center justify-center">
          <span
            className="font-bold tabular-nums leading-none"
            style={{
              fontSize: dim * 0.18,
              color,
            }}
          >
            {Math.round(score)}
          </span>
          <span
            className="text-gray-400 dark:text-gray-500 mt-1"
            style={{ fontSize: dim * 0.07 }}
          >
            / 100
          </span>
        </div>
      </div>

      {/* Risk level badge */}
      <div className="text-center">
        <span
          className={`inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-sm font-semibold ${level.bgColor} ${level.textColor} ${level.darkBgColor} ${level.darkTextColor}`}
        >
          <span>{level.icon}</span>
          {level.label}
        </span>
        <p className="mt-2 text-xs text-gray-400 dark:text-gray-500 max-w-[180px] text-center leading-relaxed">
          {level.description}
        </p>
      </div>
    </div>
  )
}
