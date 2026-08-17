import axios from 'axios'

const isLocalHost = () => {
  if (typeof window === 'undefined') return false
  const host = window.location.hostname
  const port = window.location.port
  return (
    host === 'localhost' ||
    host === '127.0.0.1' ||
    host === '0.0.0.0' ||
    host.startsWith('192.168.') ||
    host.startsWith('10.') ||
    host.startsWith('172.') ||
    host.endsWith('.local') ||
    port === '5173' ||
    port === '3000' ||
    port === '8080'
  )
}

const API_BASE = import.meta.env.VITE_API_URL || (
  isLocalHost()
    ? (window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1'
        ? 'http://localhost:8000'
        : `http://${window.location.hostname}:8000`)
    : 'https://jobshield-ai-4oev.onrender.com'
)

const client = axios.create({
  baseURL: API_BASE,
  timeout: 45000, // 45s timeout max
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
