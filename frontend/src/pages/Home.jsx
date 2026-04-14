import { Link } from 'react-router-dom'
import Layout from '../components/layout/Layout'
import Button from '../components/common/Button'

const FEATURES = [
  {
    icon: '🔍',
    title: 'OCR 智能识别',
    desc: '支持 PDF、JPG、PNG 格式，自动识别报告中的检验指标数值，准确率高达 95%+',
    color: 'from-blue-500 to-cyan-400',
  },
  {
    icon: '🧠',
    title: 'AI 深度分析',
    desc: '结合医学知识库，对 11 项核心肝功能指标进行综合分析，生成个性化评估报告',
    color: 'from-purple-500 to-pink-400',
  },
  {
    icon: '📊',
    title: '可视化展示',
    desc: '直观的图表展示各指标状态，趋势图帮助您了解肝功能变化规律',
    color: 'from-emerald-500 to-teal-400',
  },
  {
    icon: '💡',
    title: '健康建议',
    desc: '基于检测结果提供个性化健康建议，包括饮食、运动、用药等方面的指导',
    color: 'from-amber-500 to-orange-400',
  },
]

const STATS = [
  { value: '10,000+', label: '累计分析报告' },
  { value: '11',      label: '支持检测指标' },
  { value: '95%+',    label: '识别准确率' },
  { value: '< 30s',   label: '平均分析时间' },
]

const INDICATORS = ['ALT', 'AST', 'ALP', 'GGT', 'TBIL', 'DBIL', 'IBIL', 'ALB', 'GLB', 'TP', 'A/G']

export default function Home() {
  return (
    <Layout>
      {/* Hero */}
      <section className="relative overflow-hidden rounded-3xl bg-gradient-to-br from-blue-600 via-blue-700 to-cyan-600 text-white px-6 py-14 sm:px-12 sm:py-20 mb-10">
        {/* Background decoration */}
        <div className="absolute inset-0 overflow-hidden pointer-events-none">
          <div className="absolute -top-10 -right-10 w-72 h-72 rounded-full bg-white/5 blur-2xl" />
          <div className="absolute bottom-0 left-0 w-56 h-56 rounded-full bg-cyan-400/10 blur-2xl" />
        </div>

        <div className="relative max-w-3xl">
          <div className="inline-flex items-center gap-2 bg-white/15 rounded-full px-4 py-1.5 text-sm mb-6">
            <span className="w-2 h-2 rounded-full bg-green-400 animate-pulse" />
            AI 驱动的肝功能分析平台
          </div>

          <h1 className="text-3xl sm:text-5xl font-bold leading-tight mb-4">
            肝功能报告
            <br />
            <span className="text-cyan-300">智能分析系统</span>
          </h1>

          <p className="text-base sm:text-lg text-blue-100 leading-relaxed mb-8 max-w-xl">
            上传您的肝功能检验报告，系统将自动识别指标数值，结合 AI 技术进行深度分析，
            为您提供清晰的健康评估和个性化建议。
          </p>

          <div className="flex flex-wrap gap-3">
            <Link to="/upload">
              <Button
                variant="primary"
                size="lg"
                className="bg-white text-blue-700 hover:bg-blue-50 shadow-lg"
              >
                立即上传报告
                <svg className="w-4 h-4 ml-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M14 5l7 7m0 0l-7 7m7-7H3" />
                </svg>
              </Button>
            </Link>
            <Link to="/dashboard">
              <Button
                variant="ghost"
                size="lg"
                className="text-white hover:bg-white/15 border border-white/30"
              >
                查看控制台
              </Button>
            </Link>
          </div>
        </div>
      </section>

      {/* Stats */}
      <section className="grid grid-cols-2 sm:grid-cols-4 gap-4 mb-10">
        {STATS.map((s) => (
          <div
            key={s.label}
            className="bg-white dark:bg-gray-800 rounded-2xl border border-gray-100 dark:border-gray-700 p-5 text-center shadow-sm"
          >
            <p className="text-2xl sm:text-3xl font-bold text-blue-600 dark:text-blue-400">{s.value}</p>
            <p className="text-xs sm:text-sm text-gray-500 dark:text-gray-400 mt-1">{s.label}</p>
          </div>
        ))}
      </section>

      {/* Features */}
      <section className="mb-10">
        <div className="text-center mb-8">
          <h2 className="text-2xl font-bold text-gray-900 dark:text-white">核心功能</h2>
          <p className="mt-2 text-gray-500 dark:text-gray-400">专业、准确、便捷的肝功能报告分析体验</p>
        </div>
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
          {FEATURES.map((f) => (
            <div
              key={f.title}
              className="bg-white dark:bg-gray-800 rounded-2xl border border-gray-100 dark:border-gray-700 p-6 hover:shadow-md transition-shadow duration-200"
            >
              <div className={`w-12 h-12 rounded-2xl bg-gradient-to-br ${f.color} flex items-center justify-center text-2xl mb-4 shadow-sm`}>
                {f.icon}
              </div>
              <h3 className="text-base font-semibold text-gray-900 dark:text-white mb-2">{f.title}</h3>
              <p className="text-sm text-gray-500 dark:text-gray-400 leading-relaxed">{f.desc}</p>
            </div>
          ))}
        </div>
      </section>

      {/* Indicators */}
      <section className="bg-white dark:bg-gray-800 rounded-3xl border border-gray-100 dark:border-gray-700 p-6 sm:p-8">
        <h2 className="text-xl font-bold text-gray-900 dark:text-white mb-2">支持的检测指标</h2>
        <p className="text-sm text-gray-500 dark:text-gray-400 mb-5">
          系统可识别并分析以下 11 项核心肝功能检测指标
        </p>
        <div className="flex flex-wrap gap-2">
          {INDICATORS.map((ind) => (
            <span
              key={ind}
              className="px-3 py-1.5 rounded-lg bg-blue-50 dark:bg-blue-900/30 text-blue-700 dark:text-blue-300 text-sm font-medium"
            >
              {ind}
            </span>
          ))}
        </div>

        <div className="mt-6 pt-6 border-t border-gray-100 dark:border-gray-700 flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
          <div>
            <p className="text-sm font-medium text-gray-700 dark:text-gray-300">准备好了吗？</p>
            <p className="text-sm text-gray-400 dark:text-gray-500">上传您的报告，30 秒内获得分析结果</p>
          </div>
          <Link to="/upload">
            <Button variant="primary">开始分析</Button>
          </Link>
        </div>
      </section>
    </Layout>
  )
}
