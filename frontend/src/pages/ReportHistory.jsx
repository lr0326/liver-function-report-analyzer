import { useState, useMemo } from 'react'
import Layout from '../components/layout/Layout'
import Card from '../components/common/Card'
import ReportList from '../components/ReportList'
import { useApp } from '../context/AppContext'

const now = new Date()
const monthsAgo = (n) => {
  const d = new Date(now)
  d.setMonth(d.getMonth() - n)
  return d.toISOString().slice(0, 10)
}

const MOCK_REPORTS = [
  { id: 'r001', fileName: `肝功能_${monthsAgo(14).slice(0, 7)}.pdf`, createdAt: monthsAgo(14), status: 'completed', riskScore: 15 },
  { id: 'r002', fileName: `肝功能_${monthsAgo(11).slice(0, 7)}.pdf`, createdAt: monthsAgo(11), status: 'completed', riskScore: 18 },
  { id: 'r003', fileName: `体检报告_${monthsAgo(9).slice(0, 7)}.jpg`,  createdAt: monthsAgo(9),  status: 'completed', riskScore: 32 },
  { id: 'r004', fileName: `肝功能_${monthsAgo(5).slice(0, 7)}.pdf`,  createdAt: monthsAgo(5),  status: 'completed', riskScore: 42 },
  { id: 'demo', fileName: `肝功能_${monthsAgo(2).slice(0, 7)}.pdf`,  createdAt: monthsAgo(2),  status: 'completed', riskScore: 55 },
  { id: 'r006', fileName: `年度体检_${monthsAgo(17).slice(0, 7)}.pdf`, createdAt: monthsAgo(17), status: 'completed', riskScore: 20 },
]

const STATUS_OPTIONS = [
  { value: 'all',        label: '全部状态' },
  { value: 'completed',  label: '已完成' },
  { value: 'processing', label: '分析中' },
  { value: 'error',      label: '处理失败' },
]

const SORT_OPTIONS = [
  { value: 'date-desc',  label: '日期（最新）' },
  { value: 'date-asc',   label: '日期（最早）' },
  { value: 'risk-desc',  label: '风险分（高→低）' },
  { value: 'risk-asc',   label: '风险分（低→高）' },
]

const PAGE_SIZE = 6

export default function ReportHistory() {
  const { reports } = useApp()
  const [search, setSearch] = useState('')
  const [statusFilter, setStatusFilter] = useState('all')
  const [sortBy, setSortBy] = useState('date-desc')
  const [page, setPage] = useState(1)

  const allReports = reports.length ? reports : MOCK_REPORTS

  const filtered = useMemo(() => {
    let list = [...allReports]

    if (search.trim()) {
      const q = search.toLowerCase()
      list = list.filter((r) => r.fileName?.toLowerCase().includes(q) || r.id?.includes(q))
    }

    if (statusFilter !== 'all') {
      list = list.filter((r) => r.status === statusFilter)
    }

    list.sort((a, b) => {
      switch (sortBy) {
        case 'date-asc':
          return new Date(a.createdAt || a.date) - new Date(b.createdAt || b.date)
        case 'risk-desc':
          return (b.riskScore ?? 0) - (a.riskScore ?? 0)
        case 'risk-asc':
          return (a.riskScore ?? 0) - (b.riskScore ?? 0)
        default: // date-desc
          return new Date(b.createdAt || b.date) - new Date(a.createdAt || a.date)
      }
    })

    return list
  }, [allReports, search, statusFilter, sortBy])

  const totalPages = Math.ceil(filtered.length / PAGE_SIZE)
  const paginated = filtered.slice((page - 1) * PAGE_SIZE, page * PAGE_SIZE)

  const handleSearch = (e) => {
    setSearch(e.target.value)
    setPage(1)
  }

  const handleStatusChange = (e) => {
    setStatusFilter(e.target.value)
    setPage(1)
  }

  const handleSortChange = (e) => {
    setSortBy(e.target.value)
    setPage(1)
  }

  return (
    <Layout>
      {/* Header */}
      <div className="mb-6">
        <h1 className="text-2xl font-bold text-gray-900 dark:text-white">历史报告</h1>
        <p className="text-sm text-gray-500 dark:text-gray-400 mt-1">
          共 {filtered.length} 条记录
        </p>
      </div>

      {/* Filters */}
      <Card className="mb-5">
        <div className="flex flex-col sm:flex-row gap-3">
          {/* Search */}
          <div className="relative flex-1">
            <svg
              className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2}
                d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
            </svg>
            <input
              type="text"
              placeholder="搜索文件名..."
              value={search}
              onChange={handleSearch}
              className="w-full pl-9 pr-4 py-2.5 rounded-xl border border-gray-200 dark:border-gray-600 bg-gray-50 dark:bg-gray-700 text-sm text-gray-800 dark:text-gray-200 placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all"
            />
          </div>

          {/* Status filter */}
          <select
            value={statusFilter}
            onChange={handleStatusChange}
            className="px-3 py-2.5 rounded-xl border border-gray-200 dark:border-gray-600 bg-gray-50 dark:bg-gray-700 text-sm text-gray-800 dark:text-gray-200 focus:outline-none focus:ring-2 focus:ring-blue-500 cursor-pointer"
          >
            {STATUS_OPTIONS.map((o) => (
              <option key={o.value} value={o.value}>{o.label}</option>
            ))}
          </select>

          {/* Sort */}
          <select
            value={sortBy}
            onChange={handleSortChange}
            className="px-3 py-2.5 rounded-xl border border-gray-200 dark:border-gray-600 bg-gray-50 dark:bg-gray-700 text-sm text-gray-800 dark:text-gray-200 focus:outline-none focus:ring-2 focus:ring-blue-500 cursor-pointer"
          >
            {SORT_OPTIONS.map((o) => (
              <option key={o.value} value={o.value}>{o.label}</option>
            ))}
          </select>
        </div>
      </Card>

      {/* Report list */}
      <ReportList reports={paginated} emptyText="没有找到符合条件的报告" />

      {/* Pagination */}
      {totalPages > 1 && (
        <div className="mt-6 flex items-center justify-center gap-2">
          <button
            onClick={() => setPage((p) => Math.max(1, p - 1))}
            disabled={page === 1}
            className="px-3 py-1.5 rounded-lg text-sm font-medium border border-gray-200 dark:border-gray-600 text-gray-600 dark:text-gray-400 hover:bg-gray-100 dark:hover:bg-gray-700 disabled:opacity-40 disabled:cursor-not-allowed transition-colors"
          >
            上一页
          </button>

          {Array.from({ length: totalPages }, (_, i) => i + 1).map((p) => (
            <button
              key={p}
              onClick={() => setPage(p)}
              className={[
                'w-9 h-9 rounded-lg text-sm font-medium transition-colors',
                p === page
                  ? 'bg-blue-600 text-white shadow-sm'
                  : 'border border-gray-200 dark:border-gray-600 text-gray-600 dark:text-gray-400 hover:bg-gray-100 dark:hover:bg-gray-700',
              ].join(' ')}
            >
              {p}
            </button>
          ))}

          <button
            onClick={() => setPage((p) => Math.min(totalPages, p + 1))}
            disabled={page === totalPages}
            className="px-3 py-1.5 rounded-lg text-sm font-medium border border-gray-200 dark:border-gray-600 text-gray-600 dark:text-gray-400 hover:bg-gray-100 dark:hover:bg-gray-700 disabled:opacity-40 disabled:cursor-not-allowed transition-colors"
          >
            下一页
          </button>
        </div>
      )}
    </Layout>
  )
}
