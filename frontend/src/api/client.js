import axios from 'axios'

const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:8000'

const client = axios.create({
  baseURL: API_BASE,
  timeout: 60000, // 60s timeout for OCR requests
  headers: {
    'Content-Type': 'application/json',
  },
})

// ── API Methods ──────────────────────────────────────────────────────────────

export async function analyzeText(text, sourceType = 'job_posting') {
  const response = await client.post('/api/analyze/text', {
    text,
    source_type: sourceType,
  })
  return response.data
}

export async function analyzeScreenshot(file, sourceType = 'whatsapp') {
  const formData = new FormData()
  formData.append('file', file)
  formData.append('source_type', sourceType)

  const response = await client.post('/api/analyze/screenshot', formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
  })
  return response.data
}

export async function submitReport(report) {
  const response = await client.post('/api/report/submit', report)
  return response.data
}

export async function checkIdentifier(identifier) {
  const response = await client.post('/api/report/check', { identifier })
  return response.data
}

export async function getRecentReports(limit = 20) {
  const response = await client.get('/api/report/recent', { params: { limit } })
  return response.data
}

export async function getReportStats() {
  const response = await client.get('/api/report/stats')
  return response.data
}

export async function healthCheck() {
  const response = await client.get('/api/health')
  return response.data
}

export default client
