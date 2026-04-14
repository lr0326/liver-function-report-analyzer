import { ALLOWED_FILE_TYPES, MAX_FILE_SIZE_MB } from '../constants/indicators'

export function validateFile(file, options = {}) {
  if (!file) return { valid: false, error: '未选择文件' }

  const typeResult = validateFileType(file, options.allowedTypes || ALLOWED_FILE_TYPES)
  if (!typeResult.valid) return typeResult

  const sizeResult = validateFileSize(file, options.maxMB || MAX_FILE_SIZE_MB)
  if (!sizeResult.valid) return sizeResult

  return { valid: true, error: null }
}

export function validateFileSize(file, maxMB) {
  const maxBytes = maxMB * 1024 * 1024
  if (file.size > maxBytes) {
    return {
      valid: false,
      error: `文件大小超过限制（最大 ${maxMB}MB，当前 ${(file.size / 1024 / 1024).toFixed(1)}MB）`,
    }
  }
  return { valid: true, error: null }
}

export function validateFileType(file, allowedTypes) {
  const allowed = allowedTypes || ALLOWED_FILE_TYPES
  if (!allowed.includes(file.type)) {
    const typeLabels = {
      'application/pdf': 'PDF',
      'image/jpeg': 'JPG',
      'image/png': 'PNG',
    }
    const allowedLabels = allowed.map((t) => typeLabels[t] || t).join('、')
    return {
      valid: false,
      error: `不支持的文件类型，请上传 ${allowedLabels} 格式的文件`,
    }
  }
  return { valid: true, error: null }
}
