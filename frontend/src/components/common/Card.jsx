export default function Card({
  children,
  title,
  subtitle,
  footer,
  className = '',
  bodyClass = '',
  noPadding = false,
  hover = false,
}) {
  return (
    <div
      className={[
        'bg-white dark:bg-gray-800 rounded-xl border border-gray-200 dark:border-gray-700 shadow-sm',
        hover ? 'hover:shadow-md transition-shadow duration-200' : '',
        className,
      ]
        .filter(Boolean)
        .join(' ')}
    >
      {(title || subtitle) && (
        <div className="px-5 pt-5 pb-0">
          {title && (
            <h3 className="text-base font-semibold text-gray-900 dark:text-white">{title}</h3>
          )}
          {subtitle && (
            <p className="mt-0.5 text-sm text-gray-500 dark:text-gray-400">{subtitle}</p>
          )}
        </div>
      )}

      <div className={noPadding ? '' : bodyClass || 'p-5'}>{children}</div>

      {footer && (
        <div className="px-5 py-3 border-t border-gray-100 dark:border-gray-700 bg-gray-50 dark:bg-gray-800/50 rounded-b-xl">
          {footer}
        </div>
      )}
    </div>
  )
}
