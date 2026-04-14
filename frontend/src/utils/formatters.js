import { RISK_LEVELS } from '../constants/indicators'

export function formatDate(date, options = {}) {
  if (!date) return '—'
  const d = typeof date === 'string' ? new Date(date) : date
  if (isNaN(d.getTime())) return '—'

  const defaultOptions = {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    ...options,
  }
  return d.toLocaleDateString('zh-CN', defaultOptions)
}

export function formatDateTime(date) {
  if (!date) return '—'
  const d = typeof date === 'string' ? new Date(date) : date
  if (isNaN(d.getTime())) return '—'
  return d.toLocaleString('zh-CN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit',
  })
}

export function formatRiskScore(score) {
  if (score === null || score === undefined) return { label: '未知', colorClass: 'text-gray-500' }
  const level = getRiskLevel(score)
  return {
    label: level.label,
    colorClass: `${level.textColor} ${level.darkTextColor}`,
    bgClass: `${level.bgColor} ${level.darkBgColor}`,
    color: level.color,
    icon: level.icon,
  }
}

export function getRiskLevel(score) {
  if (score === null || score === undefined) return RISK_LEVELS.Normal
  if (score >= 80) return RISK_LEVELS.Severe
  if (score >= 60) return RISK_LEVELS.Moderate
  if (score >= 30) return RISK_LEVELS.Mild
  return RISK_LEVELS.Normal
}

export function formatIndicatorValue(value, unit) {
  if (value === null || value === undefined) return '—'
  const num = typeof value === 'number' ? value : parseFloat(value)
  if (isNaN(num)) return String(value)
  const formatted = Number.isInteger(num) ? num.toString() : num.toFixed(1)
  return unit ? `${formatted} ${unit}` : formatted
}

export function formatFileSize(bytes) {
  if (!bytes || bytes === 0) return '0 B'
  const units = ['B', 'KB', 'MB', 'GB']
  const i = Math.floor(Math.log(bytes) / Math.log(1024))
  const size = (bytes / Math.pow(1024, i)).toFixed(i > 0 ? 1 : 0)
  return `${size} ${units[i]}`
}

export function getIndicatorStatus(value, normalRange) {
  if (value === null || value === undefined || !normalRange) return 'unknown'
  const num = parseFloat(value)
  if (isNaN(num)) return 'unknown'
  const { min, max } = normalRange

  const lowerBound = typeof min === 'number' ? min : -Infinity
  const upperBound = typeof max === 'number' ? max : Infinity

  if (num < lowerBound) {
    const ratio = (lowerBound - num) / lowerBound
    if (ratio > 0.3) return 'severe'
    if (ratio > 0.1) return 'moderate'
    return 'mild'
  }
  if (num > upperBound) {
    const ratio = (num - upperBound) / upperBound
    if (ratio > 1.0) return 'severe'
    if (ratio > 0.5) return 'moderate'
    if (ratio > 0.1) return 'mild'
    return 'mild'
  }
  return 'normal'
}

export function getStatusConfig(status) {
  const configs = {
    normal:   { label: '正常', bgClass: 'bg-emerald-100 dark:bg-emerald-900/30', textClass: 'text-emerald-700 dark:text-emerald-300', dot: 'bg-emerald-500' },
    mild:     { label: '轻度偏高', bgClass: 'bg-amber-100 dark:bg-amber-900/30', textClass: 'text-amber-700 dark:text-amber-300', dot: 'bg-amber-500' },
    moderate: { label: '中度偏高', bgClass: 'bg-orange-100 dark:bg-orange-900/30', textClass: 'text-orange-700 dark:text-orange-300', dot: 'bg-orange-500' },
    severe:   { label: '严重异常', bgClass: 'bg-red-100 dark:bg-red-900/30', textClass: 'text-red-700 dark:text-red-300', dot: 'bg-red-500' },
    unknown:  { label: '未知', bgClass: 'bg-gray-100 dark:bg-gray-700', textClass: 'text-gray-600 dark:text-gray-300', dot: 'bg-gray-400' },
  }
  return configs[status] || configs.unknown
}
