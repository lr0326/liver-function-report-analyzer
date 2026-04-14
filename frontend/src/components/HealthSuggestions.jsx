const PRIORITY_ICONS = {
  medication: '💊',
  diet:       '🥗',
  exercise:   '🏃',
  hospital:   '🏥',
  rest:       '😴',
  water:      '💧',
  alcohol:    '🚫',
  checkup:    '🔬',
  default:    '📋',
}

const PRIORITY_COLORS = {
  high:   { bar: 'bg-red-500',    badge: 'bg-red-100 dark:bg-red-900/30 text-red-700 dark:text-red-300',    label: '高优先' },
  medium: { bar: 'bg-amber-500',  badge: 'bg-amber-100 dark:bg-amber-900/30 text-amber-700 dark:text-amber-300', label: '中优先' },
  low:    { bar: 'bg-emerald-500', badge: 'bg-emerald-100 dark:bg-emerald-900/30 text-emerald-700 dark:text-emerald-300', label: '低优先' },
}

function SuggestionCard({ suggestion, index }) {
  const icon = PRIORITY_ICONS[suggestion.type] || PRIORITY_ICONS.default
  const priorityConfig = PRIORITY_COLORS[suggestion.priority] || PRIORITY_COLORS.low

  return (
    <div className="flex gap-4 p-4 rounded-xl border border-gray-100 dark:border-gray-700 bg-white dark:bg-gray-800 hover:shadow-sm transition-shadow animate-fade-in"
      style={{ animationDelay: `${index * 50}ms` }}
    >
      <div className="w-11 h-11 rounded-xl bg-gray-50 dark:bg-gray-700 flex items-center justify-center text-xl flex-shrink-0">
        {icon}
      </div>
      <div className="flex-1 min-w-0">
        <div className="flex items-start justify-between gap-2">
          <h4 className="text-sm font-semibold text-gray-900 dark:text-white leading-snug">
            {suggestion.title}
          </h4>
          <span className={`flex-shrink-0 text-xs px-2 py-0.5 rounded-full font-medium ${priorityConfig.badge}`}>
            {priorityConfig.label}
          </span>
        </div>
        <p className="mt-1 text-sm text-gray-500 dark:text-gray-400 leading-relaxed">
          {suggestion.content}
        </p>
      </div>
    </div>
  )
}

export default function HealthSuggestions({ suggestions = [] }) {
  if (!suggestions.length) {
    return (
      <div className="text-center py-10 text-gray-400 dark:text-gray-500">
        <span className="text-4xl">🌿</span>
        <p className="mt-2 text-sm">暂无健康建议</p>
      </div>
    )
  }

  const byPriority = {
    high:   suggestions.filter((s) => s.priority === 'high'),
    medium: suggestions.filter((s) => s.priority === 'medium'),
    low:    suggestions.filter((s) => s.priority === 'low' || !s.priority),
  }

  return (
    <div className="space-y-6">
      {byPriority.high.length > 0 && (
        <section>
          <div className="flex items-center gap-2 mb-3">
            <div className="w-1 h-4 rounded-full bg-red-500" />
            <h3 className="text-sm font-semibold text-gray-700 dark:text-gray-300">立即关注</h3>
          </div>
          <div className="space-y-2">
            {byPriority.high.map((s, i) => (
              <SuggestionCard key={i} suggestion={s} index={i} />
            ))}
          </div>
        </section>
      )}

      {byPriority.medium.length > 0 && (
        <section>
          <div className="flex items-center gap-2 mb-3">
            <div className="w-1 h-4 rounded-full bg-amber-500" />
            <h3 className="text-sm font-semibold text-gray-700 dark:text-gray-300">需要改善</h3>
          </div>
          <div className="space-y-2">
            {byPriority.medium.map((s, i) => (
              <SuggestionCard key={i} suggestion={s} index={i} />
            ))}
          </div>
        </section>
      )}

      {byPriority.low.length > 0 && (
        <section>
          <div className="flex items-center gap-2 mb-3">
            <div className="w-1 h-4 rounded-full bg-emerald-500" />
            <h3 className="text-sm font-semibold text-gray-700 dark:text-gray-300">日常保健</h3>
          </div>
          <div className="space-y-2">
            {byPriority.low.map((s, i) => (
              <SuggestionCard key={i} suggestion={s} index={i} />
            ))}
          </div>
        </section>
      )}
    </div>
  )
}
