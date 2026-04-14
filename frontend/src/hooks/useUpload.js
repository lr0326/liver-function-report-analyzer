import { useState, useCallback } from 'react'
import { uploadReport } from '../services/api'
import { validateFile } from '../utils/validators'

export function useUpload() {
  const [file, setFile] = useState(null)
  const [progress, setProgress] = useState(0)
  const [uploading, setUploading] = useState(false)
  const [error, setError] = useState(null)
  const [result, setResult] = useState(null)

  const selectFile = useCallback((selectedFile) => {
    const validation = validateFile(selectedFile)
    if (!validation.valid) {
      setError(validation.error)
      return false
    }
    setFile(selectedFile)
    setError(null)
    setResult(null)
    setProgress(0)
    return true
  }, [])

  const upload = useCallback(async () => {
    if (!file) {
      setError('请先选择文件')
      return null
    }

    setUploading(true)
    setError(null)
    setProgress(0)

    try {
      const data = await uploadReport(file, setProgress)
      setResult(data)
      setProgress(100)
      return data
    } catch (err) {
      setError(err.message || '上传失败，请重试')
      return null
    } finally {
      setUploading(false)
    }
  }, [file])

  const reset = useCallback(() => {
    setFile(null)
    setProgress(0)
    setUploading(false)
    setError(null)
    setResult(null)
  }, [])

  return { file, progress, uploading, error, result, selectFile, upload, reset }
}
