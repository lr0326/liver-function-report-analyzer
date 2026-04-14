const SIZE_CLASSES = {
  xs: 'w-4 h-4 border-2',
  sm: 'w-6 h-6 border-2',
  md: 'w-8 h-8 border-2',
  lg: 'w-12 h-12 border-3',
  xl: 'w-16 h-16 border-4',
}

export default function Loading({
  size = 'md',
  text,
  fullScreen = false,
  className = '',
}) {
  const spinner = (
    <div className={`inline-flex flex-col items-center gap-3 ${className}`}>
      <div
        className={[
          'rounded-full border-blue-200 dark:border-blue-900 border-t-blue-600 dark:border-t-blue-400 animate-spin',
          SIZE_CLASSES[size] || SIZE_CLASSES.md,
        ].join(' ')}
      />
      {text && (
        <span className="text-sm text-gray-500 dark:text-gray-400">{text}</span>
      )}
    </div>
  )

  if (fullScreen) {
    return (
      <div className="fixed inset-0 z-50 flex items-center justify-center bg-white/80 dark:bg-gray-900/80 backdrop-blur-sm">
        {spinner}
      </div>
    )
  }

  return spinner
}

export function PageLoading({ text = '加载中...' }) {
  return (
    <div className="flex items-center justify-center min-h-[300px]">
      <Loading size="lg" text={text} />
    </div>
  )
}
