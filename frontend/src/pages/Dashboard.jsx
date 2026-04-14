import { useMemo } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import Layout from '../components/layout/Layout'
import Card from '../components/common/Card'
import Button from '../components/common/Button'
import TrendChart from '../components/TrendChart'
import ReportList from '../components/ReportList'
import { useApp } from '../context/AppContext'
import { formatDate } from '../utils/formatters'

const now = new Date()
const monthsAgo = (n) => {
  const d = new Date(now)
  d.setMonth(d.getMonth() - n)
  return d.toISOString().slice(0, 10)
}

const MOCK_REPORTS = [
  { id: 'r001', fileName: `肝功能_${monthsAgo(8).slice(0, 7)}.pdf`, createdAt: monthsAgo(8), status: 'completed', riskScore: 18 },
  { id: 'r002', fileName: `肝功能_${monthsAgo(5).slice(0, 7)}.pdf`, createdAt: monthsAgo(5), status: 'completed', riskScore: 42 },
  { id: 'demo', fileName: `肝功能_${monthsAgo(2).slice(0, 7)}.pdf`, createdAt: monthsAgo(2), status: 'completed', riskScore: 55 },
]

const MOCK_TREND = [
  { date: monthsAgo(8), label: monthsAgo(8).slice(0, 7).replace('-', '/'), ALT: 35, AST: 36, GGT: 42 },
  { date: monthsAgo(6), label: monthsAgo(6).slice(0, 7).replace('-', '/'), ALT: 38, AST: 38, GGT: 50 },
  { date: monthsAgo(5), label: monthsAgo(5).slice(0, 7).replace('-', '/'), ALT: 67, AST: 48, GGT: 75 },
  { date: monthsAgo(2), label: monthsAgo(2).slice(0, 7).replace('-', '/'), ALT: 55, AST: 44, GGT: 65 },
]

function StatCard({ icon, label, value, sub, color = 'blue' }) {
  const colorMap = {
    blue:    'bg-blue-50 dark:bg-blue-900/20 text-blue-600 dark:text-blue-400',
    green:   'bg-emerald-50 dark:bg-emerald-900/20 text-emerald-600 dark:text-emerald-400',
    amber:   'bg-amber-50 dark:bg-amber-900/20 text-amber-600 dark:text-amber-400',
    red:     'bg-red-50 dark:bg-red-900/20 text-red-600 dark:text-red-400',
  }
  return (
    <div className="bg-white dark:bg-gray-800 rounded-2xl border border-gray-100 dark:border-gray-700 p-5 flex items-start gap-4">
      <div className={`w-12 h-12 rounded-xl flex items-center justify-center text-xl flex-shrink-0 ${colorMap[color]}`}>
        {icon}
      </div>
      <div>
        <p className="text-sm text-gray-500 dark:text-gray-400">{label}</p>
        <p className="text-2xl font-bold text-gray-900 dark:text-white mt-0.5">{value}</p>
        {sub && <p className="text-xs text-gray-400 dark:text-gray-500 mt-0.5">{sub}</p>}
      </div>
    </div>
  )
}

export default function Dashboard() {
  const { user, reports } = useApp()
  const navigate = useNavigate()

  const displayReports = useMemo(
    () => (reports.length ? reports.slice(0, 6) : MOCK_REPORTS),
    [reports]
  )

  const avgRisk = useMemo(() => {
    const list = reports.length ? reports : MOCK_REPORTS
    const withScore = list.filter((r) => r.riskScore !== undefined)
    if (!withScore.length) return 0
    return Math.round(withScore.reduce((sum, r) => sum + r.riskScore, 0) / withScore.length)
  }, [reports])

  const lastCheck = displayReports[0]?.createdAt
    ? formatDate(displayReports[0].createdAt)
    : '暂无记录'

  return (
    <Layout sidebar>
      {/* Welcome */}
      <div className="mb-6">
        <h1 className="text-2xl font-bold text-gray-900 dark:text-white">
          你好，{user?.name || '用户'} 👋
        </h1>
        <p className="text-sm text-gray-500 dark:text-gray-400 mt-1">
          今天是 {formatDate(new Date())}，以下是您的肝功能健康概况
        </p>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-1 sm:grid-cols-2 xl:grid-cols-4 gap-4 mb-6">
        <StatCard icon="📋" label="总报告数" value={`${displayReports.length} 份`} color="blue" />
        <StatCard icon="📅" label="最近检查" value={lastCheck} color="green" />
        <StatCard icon="📈" label="平均风险评分" value={`${avgRisk} 分`} sub="越低越好" color="amber" />
        <StatCard icon="⚠️" label="最新异常指标" value="3 项" sub="基于最近一次报告" color="red" />
      </div>

      {/* Trend + Quick actions */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 mb-6">
        <div className="lg:col-span-2">
          <Card title="指标趋势" subtitle="近期 ALT、AST、GGT 变化趋势">
            <TrendChart data={MOCK_TREND} selectedIndicators={['ALT', 'AST', 'GGT']} />
          </Card>
        </div>

        <div className="space-y-4">
          <Card title="快捷操作">
            <div className="space-y-2">
              <button
                onClick={() => navigate('/upload')}
                className="w-full flex items-center gap-3 p-3 rounded-xl hover:bg-gray-50 dark:hover:bg-gray-700/50 transition-colors text-left group"
              >
                <div className="w-9 h-9 rounded-lg bg-blue-100 dark:bg-blue-900/30 flex items-center justify-center text-blue-500 group-hover:scale-105 transition-transform">
                  <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-8l-4-4m0 0L8 8m4-4v12" />
                  </svg>
                </div>
                <div>
                  <p className="text-sm font-medium text-gray-800 dark:text-gray-200">上传新报告</p>
                  <p className="text-xs text-gray-400">PDF / JPG / PNG</p>
                </div>
              </button>

              <button
                onClick={() => navigate('/history')}
                className="w-full flex items-center gap-3 p-3 rounded-xl hover:bg-gray-50 dark:hover:bg-gray-700/50 transition-colors text-left group"
              >
                <div className="w-9 h-9 rounded-lg bg-purple-100 dark:bg-purple-900/30 flex items-center justify-center text-purple-500 group-hover:scale-105 transition-transform">
                  <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2" />
                  </svg>
                </div>
                <div>
                  <p className="text-sm font-medium text-gray-800 dark:text-gray-200">查看历史记录</p>
                  <p className="text-xs text-gray-400">所有报告列表</p>
                </div>
              </button>

              <Link
                to="/results/demo"
                className="w-full flex items-center gap-3 p-3 rounded-xl hover:bg-gray-50 dark:hover:bg-gray-700/50 transition-colors text-left group"
              >
                <div className="w-9 h-9 rounded-lg bg-emerald-100 dark:bg-emerald-900/30 flex items-center justify-center text-emerald-500 group-hover:scale-105 transition-transform">
                  <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" />
                  </svg>
                </div>
                <div>
                  <p className="text-sm font-medium text-gray-800 dark:text-gray-200">查看演示报告</p>
                  <p className="text-xs text-gray-400">示例分析结果</p>
                </div>
              </Link>
            </div>
          </Card>

          {/* Health tip */}
          <div className="rounded-2xl bg-gradient-to-br from-emerald-500 to-teal-500 p-5 text-white">
            <p className="text-sm font-semibold mb-1">健康小贴士</p>
            <p className="text-xs leading-relaxed opacity-90">
              每年定期检查肝功能，特别是有饮酒习惯、服用长期药物或肝脏疾病家族史的人群，建议每半年检查一次。
            </p>
          </div>
        </div>
      </div>

      {/* Recent reports */}
      <Card
        title="最近报告"
        subtitle="最新上传和分析的报告"
        footer={
          <Link to="/history" className="text-sm text-blue-600 dark:text-blue-400 hover:underline">
            查看全部报告 →
          </Link>
        }
      >
        <ReportList reports={displayReports} />
      </Card>
    </Layout>
  )
}
