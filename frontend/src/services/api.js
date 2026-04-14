import axios from 'axios'

const apiClient = axios.create({
  baseURL: '/api',
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
})

// Request interceptor
apiClient.interceptors.request.use(
  (config) => config,
  (error) => Promise.reject(error)
)

// Response interceptor
apiClient.interceptors.response.use(
  (response) => response.data,
  (error) => {
    const message =
      error.response?.data?.message ||
      error.response?.data?.error ||
      error.message ||
      '请求失败，请稍后重试'
    return Promise.reject(new Error(message))
  }
)

export const uploadReport = (file, onProgress) => {
  const formData = new FormData()
  formData.append('file', file)

  return apiClient.post('/reports/upload', formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
    onUploadProgress: (progressEvent) => {
      if (onProgress && progressEvent.total) {
        const percent = Math.round((progressEvent.loaded * 100) / progressEvent.total)
        onProgress(percent)
      }
    },
  })
}

export const getAnalysisResult = (reportId) =>
  apiClient.get(`/reports/analysis/${reportId}`)

export const getUserReports = (userId) =>
  apiClient.get(`/reports/user/${userId}`)

export const getHealthRecords = (userId) =>
  apiClient.get(`/health-records/${userId}`)

export const checkHealth = () =>
  apiClient.get('/health')

export default apiClient
