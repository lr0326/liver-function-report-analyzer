import { useNavigate } from 'react-router-dom'
import Layout from '../components/layout/Layout'
import FileUpload from '../components/common/FileUpload'
import Button from '../components/common/Button'
import Alert from '../components/common/Alert'
import Card from '../components/common/Card'
import { useUpload } from '../hooks/useUpload'
import { useNotification } from '../hooks/useNotification'
import { useApp } from '../context/AppContext'

const TIPS = [
  '请确保报告图片清晰，文字可读',
  '支持 PDF、JPG、PNG 格式，最大 20MB',
  '请上传完整的肝功能检验报告页面',
  '扫描件请保持原始分辨率，不要压缩',
]

export default function Upload() {
  const navigate = useNavigate()
  const { addReport } = useApp()
  const { success: notifySuccess, error: notifyError } = useNotification()
  const { file, progress, uploading, error, selectFile, upload, reset } = useUpload()

  const handleUpload = async () => {
    const result = await upload()
    if (result) {
      const reportId = result.report_id || result.id || result.reportId
      const newReport = {
        id: reportId,
        fileName: file?.name,
        createdAt: new Date().toISOString(),
        status: 'completed',
        riskScore: result.riskScore,
      }
      addReport(newReport)
      notifySuccess('报告上传成功，正在跳转到分析结果...')
      setTimeout(() => navigate(`/results/${reportId}`), 800)
    } else {
      notifyError('上传失败，请检查网络连接后重试')
    }
  }

  return (
    <Layout>
      <div className="max-w-2xl mx-auto">
        {/* Header */}
        <div className="mb-6">
          <h1 className="text-2xl font-bold text-gray-900 dark:text-white">上传检验报告</h1>
          <p className="mt-1 text-sm text-gray-500 dark:text-gray-400">
            上传您的肝功能检验报告，系统将自动识别并分析各项指标
          </p>
        </div>

        <div className="space-y-5">
          {/* Upload area */}
          <Card title="选择文件">
            <FileUpload
              onFileSelect={selectFile}
              disabled={uploading}
            />
          </Card>

          {/* Error message */}
          {error && (
            <Alert type="error" message={error} dismissible />
          )}

          {/* Upload progress */}
          {uploading && (
            <Card>
              <div className="space-y-2">
                <div className="flex justify-between text-sm">
                  <span className="text-gray-600 dark:text-gray-400 font-medium">正在上传并分析...</span>
                  <span className="text-blue-600 dark:text-blue-400 font-semibold tabular-nums">{progress}%</span>
                </div>
                <div className="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-2 overflow-hidden">
                  <div
                    className="bg-blue-600 h-full rounded-full transition-all duration-300 ease-out"
                    style={{ width: `${progress}%` }}
                  />
                </div>
                <p className="text-xs text-gray-400 dark:text-gray-500">
                  请耐心等待，AI 分析通常需要 15-30 秒
                </p>
              </div>
            </Card>
          )}

          {/* Action buttons */}
          <div className="flex gap-3">
            <Button
              variant="primary"
              size="lg"
              fullWidth
              loading={uploading}
              disabled={!file || uploading}
              onClick={handleUpload}
            >
              {uploading ? '分析中...' : '上传并分析'}
            </Button>
            {file && !uploading && (
              <Button variant="secondary" size="lg" onClick={reset}>
                重新选择
              </Button>
            )}
          </div>

          {/* Tips */}
          <Card title="上传须知" className="bg-amber-50/50 dark:bg-amber-900/10 border-amber-100 dark:border-amber-800/30">
            <ul className="space-y-2">
              {TIPS.map((tip, i) => (
                <li key={i} className="flex items-start gap-2 text-sm text-gray-600 dark:text-gray-400">
                  <svg className="w-4 h-4 text-amber-500 flex-shrink-0 mt-0.5" fill="currentColor" viewBox="0 0 20 20">
                    <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
                  </svg>
                  {tip}
                </li>
              ))}
            </ul>
          </Card>

          {/* Demo link */}
          <div className="text-center">
            <p className="text-sm text-gray-400 dark:text-gray-500">
              没有报告文件？
              <button
                onClick={() => navigate('/results/demo')}
                className="ml-1 text-blue-600 dark:text-blue-400 hover:underline"
              >
                查看演示结果
              </button>
            </p>
          </div>
        </div>
      </div>
    </Layout>
  )
}
