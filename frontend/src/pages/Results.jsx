import { useEffect, useState } from 'react'
import { useParams, useNavigate, Link } from 'react-router-dom'
import Layout from '../components/layout/Layout'
import Tabs from '../components/common/Tabs'
import Card from '../components/common/Card'
import Button from '../components/common/Button'
import Alert from '../components/common/Alert'
import { PageLoading } from '../components/common/Loading'
import IndicatorTable from '../components/IndicatorTable'
import RiskScoreDisplay from '../components/RiskScoreDisplay'
import HealthSuggestions from '../components/HealthSuggestions'
import AnalysisSummary from '../components/AnalysisSummary'
import { getAnalysisResult } from '../services/api'
import { getIndicatorStatus } from '../utils/formatters'
import { INDICATOR_INFO } from '../constants/indicators'

const MOCK_DATA = {
  id: 'demo',
  fileName: '肝功能检验报告_示例.pdf',
  createdAt: new Date().toISOString(),
  riskScore: 42,
  overallAssessment: 'ALT、AST 轻度升高，提示可能存在轻微肝细胞损伤。建议注意休息，避免饮酒，一个月后复查。其他指标均在正常范围内。',
  keyFindings: [
    'ALT 偏高（67 U/L），超过正常上限 67.5%',
    'AST 轻度升高（48 U/L），超出正常范围 20%',
    'GGT 轻度升高，提示可能存在脂肪肝或酒精性肝损伤风险',
  ],
  indicators: [
    { key: 'ALT',  value: 67,   unit: 'U/L',     referenceRange: '7-40' },
    { key: 'AST',  value: 48,   unit: 'U/L',     referenceRange: '13-40' },
    { key: 'ALP',  value: 82,   unit: 'U/L',     referenceRange: '44-147' },
    { key: 'GGT',  value: 75,   unit: 'U/L',     referenceRange: '8-61' },
    { key: 'TBIL', value: 12.3, unit: 'μmol/L',  referenceRange: '3.4-17.1' },
    { key: 'DBIL', value: 4.1,  unit: 'μmol/L',  referenceRange: '0-6.8' },
    { key: 'IBIL', value: 8.2,  unit: 'μmol/L',  referenceRange: '1.7-10.2' },
    { key: 'ALB',  value: 42,   unit: 'g/L',     referenceRange: '35-55' },
    { key: 'GLB',  value: 28,   unit: 'g/L',     referenceRange: '20-40' },
    { key: 'TP',   value: 70,   unit: 'g/L',     referenceRange: '65-85' },
    { key: 'AG',   value: 1.5,  unit: '',        referenceRange: '1.2-2.4' },
  ],
  suggestions: [
    { title: '立即停止饮酒', content: 'ALT 和 GGT 升高提示酒精可能是重要诱因，建议立即戒酒或严格限酒。', type: 'alcohol', priority: 'high' },
    { title: '一个月后复查肝功能', content: '建议 4-6 周后复查肝功能全套，观察指标是否恢复正常。', type: 'checkup', priority: 'high' },
    { title: '调整饮食结构', content: '减少高脂肪、高糖食物摄入，增加蔬菜、水果比例，避免暴饮暴食。', type: 'diet', priority: 'medium' },
    { title: '适量有氧运动', content: '每周 3-5 次，每次 30-45 分钟的有氧运动，有助于改善脂肪代谢。', type: 'exercise', priority: 'medium' },
    { title: '充足睡眠', content: '保证每天 7-8 小时高质量睡眠，肝脏主要在夜间进行自我修复。', type: 'rest', priority: 'low' },
    { title: '多喝水', content: '每天饮水 1500-2000ml，帮助代谢废物排出体外。', type: 'water', priority: 'low' },
  ],
  aiReport: `## 肝功能分析报告

**检查日期：** ${new Date().toLocaleDateString('zh-CN')}

### 一、检测结果概述

本次肝功能检测共检测 11 项指标，其中 3 项出现异常，综合风险评分为 42 分，属于**轻度异常**范围。

### 二、异常指标分析

**1. ALT（丙氨酸氨基转移酶）：67 U/L（参考值：7-40 U/L）**

ALT 是反映肝细胞损伤最敏感的指标。当前数值超出正常上限约 67.5%，属于轻中度升高。可能原因包括：
- 酒精摄入过多
- 脂肪肝
- 病毒性肝炎（早期）
- 某些药物影响

**2. AST（天冬氨酸氨基转移酶）：48 U/L（参考值：13-40 U/L）**

AST 轻度升高，超出正常范围约 20%。AST/ALT 比值约为 0.72，提示以肝细胞损伤为主（比值 < 1 更倾向于病毒性或非酒精性肝损伤）。

**3. GGT（γ-谷氨酰转移酶）：75 U/L（参考值：8-61 U/L）**

GGT 对酒精性肝损伤极为敏感。当前升高提示需要关注酒精摄入情况和胆道状态。

### 三、正常指标

ALP、TBIL、DBIL、IBIL、ALB、GLB、TP、A/G 均在正常参考范围内，提示胆道功能、肝脏合成功能基本正常。

### 四、综合评估与建议

结合当前检测结果，建议：
1. **立即** 停止或严格限制酒精摄入
2. **近期** 进行腹部 B 超检查，排查脂肪肝可能
3. **4-6 周后** 复查肝功能全套，评估恢复情况
4. 如出现乏力、纳差、黄疸等症状，请立即就医

---

*本报告由 AI 系统自动生成，仅供参考，不构成医疗诊断依据。如有疑问，请咨询专业医师。*`,
}

const TABS = [
  { key: 'overview',     label: '概览',   icon: '📊' },
  { key: 'indicators',   label: '指标详情', icon: '🔬' },
  { key: 'suggestions',  label: '健康建议', icon: '💡' },
  { key: 'ai-report',    label: 'AI 报告',  icon: '🤖' },
]

export default function Results() {
  const { reportId } = useParams()
  const navigate = useNavigate()
  const [activeTab, setActiveTab] = useState('overview')
  const [loading, setLoading] = useState(true)
  const [data, setData] = useState(null)
  const [error, setError] = useState(null)

  useEffect(() => {
    let cancelled = false
    async function fetchData() {
      setLoading(true)
      setError(null)
      try {
        if (reportId === 'demo') {
          await new Promise((r) => setTimeout(r, 600))
          if (!cancelled) setData(MOCK_DATA)
          return
        }
        const result = await getAnalysisResult(reportId)
        if (!cancelled) setData(result?.data || result || MOCK_DATA)
      } catch {
        if (!cancelled) {
          // Fall back to mock data for demo purposes
          setData({ ...MOCK_DATA, id: reportId })
        }
      } finally {
        if (!cancelled) setLoading(false)
      }
    }
    fetchData()
    return () => { cancelled = true }
  }, [reportId])

  useEffect(() => {
    if (data) setLoading(false)
  }, [data])

  const handlePrint = () => window.print()

  if (loading) {
    return (
      <Layout>
        <PageLoading text="正在获取分析结果..." />
      </Layout>
    )
  }

  if (error && !data) {
    return (
      <Layout>
        <div className="max-w-lg mx-auto text-center py-20">
          <Alert type="error" message={error} />
          <Button variant="primary" className="mt-4" onClick={() => navigate('/upload')}>
            重新上传
          </Button>
        </div>
      </Layout>
    )
  }

  const analysis = {
    riskScore: data?.riskScore ?? 0,
    overallAssessment: data?.overallAssessment,
    keyFindings: data?.keyFindings || [],
    totalCount: data?.indicators?.length ?? 0,
    abnormalCount: data?.indicators?.filter((ind) => {
      const info = INDICATOR_INFO[ind.key] || {}
      const status = getIndicatorStatus(ind.value, info.normalRange)
      return status !== 'normal' && status !== 'unknown'
    }).length ?? 0,
  }

  return (
    <Layout>
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 mb-6">
        <div>
          <div className="flex items-center gap-2 text-sm text-gray-400 dark:text-gray-500 mb-1">
            <Link to="/history" className="hover:text-blue-600 dark:hover:text-blue-400 transition-colors">
              历史报告
            </Link>
            <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
            </svg>
            <span className="text-gray-600 dark:text-gray-300">分析结果</span>
          </div>
          <h1 className="text-2xl font-bold text-gray-900 dark:text-white">
            {data?.fileName || '肝功能分析报告'}
          </h1>
        </div>
        <div className="flex gap-2 no-print">
          <Button variant="secondary" size="sm" onClick={handlePrint}>
            <svg className="w-4 h-4 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 17h2a2 2 0 002-2v-4a2 2 0 00-2-2H5a2 2 0 00-2 2v4a2 2 0 002 2h2m2 4h6a2 2 0 002-2v-4a2 2 0 00-2-2H9a2 2 0 00-2 2v4a2 2 0 002 2zm8-12V5a2 2 0 00-2-2H9a2 2 0 00-2 2v4h10z" />
            </svg>
            打印报告
          </Button>
          <Button variant="primary" size="sm" onClick={() => navigate('/upload')}>
            上传新报告
          </Button>
        </div>
      </div>

      {/* Demo notice */}
      {(reportId === 'demo' || !reportId) && (
        <Alert
          type="info"
          message="当前显示的是演示数据，请上传真实报告以获得个性化分析结果。"
          dismissible
          className="mb-4"
        />
      )}

      {/* Tabs */}
      <Tabs tabs={TABS} activeTab={activeTab} onChange={setActiveTab} className="mb-6" />

      {/* Tab content */}
      {activeTab === 'overview' && (
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 animate-fade-in">
          <div className="lg:col-span-2">
            <Card title="综合概览">
              <AnalysisSummary analysis={analysis} />
            </Card>
          </div>
          <div>
            <Card title="风险评分" bodyClass="p-5 flex justify-center">
              <RiskScoreDisplay score={data?.riskScore ?? 0} size="lg" />
            </Card>
          </div>
        </div>
      )}

      {activeTab === 'indicators' && (
        <Card title="指标详情" subtitle={`共 ${data?.indicators?.length ?? 0} 项检测指标`} className="animate-fade-in">
          <IndicatorTable indicators={data?.indicators || []} />
        </Card>
      )}

      {activeTab === 'suggestions' && (
        <Card title="健康建议" className="animate-fade-in">
          <HealthSuggestions suggestions={data?.suggestions || []} />
        </Card>
      )}

      {activeTab === 'ai-report' && (
        <Card title="AI 分析报告" className="animate-fade-in">
          <div className="prose prose-sm dark:prose-invert max-w-none">
            <pre className="whitespace-pre-wrap font-sans text-sm text-gray-700 dark:text-gray-300 leading-relaxed bg-gray-50 dark:bg-gray-900/50 rounded-xl p-5 border border-gray-100 dark:border-gray-700">
              {data?.aiReport || '暂无 AI 分析报告'}
            </pre>
          </div>
        </Card>
      )}
    </Layout>
  )
}
