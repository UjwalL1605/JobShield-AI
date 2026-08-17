import { useState, useEffect } from 'react'
import { useLocation, Link } from 'react-router-dom'
import {
  AlertTriangle, Send, Search, Loader2,
  Mail, Phone, Globe, CreditCard, Building2, Clock,
  CheckCircle2, ArrowLeft, ShieldAlert, Sparkles
} from 'lucide-react'
import { submitReport, checkIdentifier, getRecentReports } from '../api/client'
import './ReportPage.css'

const REPORT_TYPES = [
  { value: 'email', label: 'Email Address', icon: <Mail size={16} /> },
  { value: 'phone', label: 'Phone Number', icon: <Phone size={16} /> },
  { value: 'website', label: 'Website URL', icon: <Globe size={16} /> },
  { value: 'upi', label: 'UPI ID', icon: <CreditCard size={16} /> },
  { value: 'company', label: 'Company Name', icon: <Building2 size={16} /> },
]

const SOURCE_PLATFORMS = [
  'WhatsApp', 'Telegram', 'LinkedIn', 'Email', 'SMS',
  'Instagram', 'Job Portal', 'Other',
]

function ReportPage() {
  const location = useLocation()
  const [activeTab, setActiveTab] = useState('report')

  // Report form
  const [reportType, setReportType] = useState('email')
  const [identifier, setIdentifier] = useState('')
  const [companyName, setCompanyName] = useState('')
  const [description, setDescription] = useState('')
  const [sourcePlatform, setSourcePlatform] = useState('')
  const [submitting, setSubmitting] = useState(false)
  const [submitResult, setSubmitResult] = useState(null)
  const [prefillNotice, setPrefillNotice] = useState(false)

  // Check form
  const [checkQuery, setCheckQuery] = useState('')
  const [checking, setChecking] = useState(false)
  const [checkResult, setCheckResult] = useState(null)

  // Recent reports
  const [recentReports, setRecentReports] = useState([])
  const [loadingRecent, setLoadingRecent] = useState(false)

  useEffect(() => {
    loadRecentReports()

    // Handle prefill from AnalyzePage
    if (location.state) {
      if (location.state.prefillType) setReportType(location.state.prefillType)
      if (location.state.prefillIdentifier) setIdentifier(location.state.prefillIdentifier)
      if (location.state.prefillCompany) setCompanyName(location.state.prefillCompany)
      if (location.state.prefillDescription) setDescription(location.state.prefillDescription)
      if (location.state.prefillSource) {
        const sourceMap = {
          'whatsapp': 'WhatsApp',
          'telegram': 'Telegram',
          'email': 'Email',
          'linkedin': 'LinkedIn',
          'sms': 'SMS',
          'instagram': 'Instagram',
          'job_posting': 'Job Portal',
        }
        setSourcePlatform(sourceMap[location.state.prefillSource] || 'Other')
      }
      setPrefillNotice(true)
    }
  }, [location.state])

  const loadRecentReports = async () => {
    setLoadingRecent(true)
    try {
      const data = await getRecentReports(15)
      setRecentReports(data)
    } catch {
      // silently fail — not critical
    } finally {
      setLoadingRecent(false)
    }
  }

  const handleSubmitReport = async (e) => {
    e.preventDefault()
    if (!identifier.trim()) return

    setSubmitting(true)
    setSubmitResult(null)
    try {
      const result = await submitReport({
        report_type: reportType,
        identifier: identifier.trim(),
        company_name: companyName.trim() || null,
        description: description.trim() || null,
        source_platform: sourcePlatform || null,
      })
      setSubmitResult(result)
      // Reset form on success
      setIdentifier('')
      setCompanyName('')
      setDescription('')
      setSourcePlatform('')
      loadRecentReports()
    } catch (err) {
      setSubmitResult({
        status: 'error',
        message: err.response?.data?.detail || 'Failed to submit report. Is the backend running?',
      })
    } finally {
      setSubmitting(false)
    }
  }

  const handleCheck = async (e) => {
    e.preventDefault()
    if (!checkQuery.trim()) return

    setChecking(true)
    setCheckResult(null)
    try {
      const result = await checkIdentifier(checkQuery.trim())
      setCheckResult(result)
    } catch (err) {
      setCheckResult({
        found: false,
        message: err.response?.data?.detail || 'Check failed. Is the backend running?',
      })
    } finally {
      setChecking(false)
    }
  }

  const typeIcon = {
    email: <Mail size={14} />,
    phone: <Phone size={14} />,
    website: <Globe size={14} />,
    upi: <CreditCard size={14} />,
    company: <Building2 size={14} />,
  }

  return (
    <div className="report-page">
      <div className="container">
        <div className="report-header animate-fade-in-up">
          <h1 className="report-title">
            <AlertTriangle size={28} />
            Scam Report Center
          </h1>
          <p className="report-subtitle">
            Report scam identifiers to protect the community, or check if something has already been reported
          </p>
        </div>

        <div className="tabs" style={{ maxWidth: '500px', margin: '0 auto 32px' }}>
          <button
            className={`tab ${activeTab === 'report' ? 'active' : ''}`}
            onClick={() => setActiveTab('report')}
          >
            📝 Report a Scam
          </button>
          <button
            className={`tab ${activeTab === 'check' ? 'active' : ''}`}
            onClick={() => setActiveTab('check')}
          >
            🔍 Check Identifier
          </button>
        </div>

        <div className="report-layout">
          {/* ── Report / Check Panel ──────────────────────────────────────── */}
          <div className="report-form-panel animate-fade-in-up" style={{ animationDelay: '0.1s' }}>
            {activeTab === 'report' ? (
              <form className="glass report-form" onSubmit={handleSubmitReport}>
                <div className="report-form-header-row">
                  <h3 className="form-title">Report a Scam</h3>
                  <Link to="/analyze" className="btn-link-back">
                    <ArrowLeft size={14} /> Back to Scanner
                  </Link>
                </div>

                {prefillNotice && (
                  <div className="prefill-alert animate-fade-in">
                    <Sparkles size={16} className="text-purple flex-shrink-0" />
                    <div className="prefill-text">
                      <strong>Auto-filled from your scan audit.</strong> Review the details below and submit to protect the job seeker community.
                    </div>
                  </div>
                )}

                <div className="report-type-grid">
                  {REPORT_TYPES.map((rt) => (
                    <button
                      key={rt.value}
                      type="button"
                      className={`report-type-btn ${reportType === rt.value ? 'active' : ''}`}
                      onClick={() => setReportType(rt.value)}
                    >
                      {rt.icon}
                      {rt.label}
                    </button>
                  ))}
                </div>

                <div className="form-group">
                  <label className="input-label">
                    {REPORT_TYPES.find(r => r.value === reportType)?.label} *
                  </label>
                  <input
                    className="input-field"
                    type="text"
                    placeholder={`Enter the ${reportType}...`}
                    value={identifier}
                    onChange={(e) => setIdentifier(e.target.value)}
                    required
                  />
                </div>

                <div className="form-group">
                  <label className="input-label">Company Name (optional)</label>
                  <input
                    className="input-field"
                    type="text"
                    placeholder="e.g. TechVision Solutions"
                    value={companyName}
                    onChange={(e) => setCompanyName(e.target.value)}
                  />
                </div>

                <div className="form-group">
                  <label className="input-label">Source Platform</label>
                  <select
                    className="input-field"
                    value={sourcePlatform}
                    onChange={(e) => setSourcePlatform(e.target.value)}
                  >
                    <option value="">Select platform...</option>
                    {SOURCE_PLATFORMS.map((p) => (
                      <option key={p} value={p}>{p}</option>
                    ))}
                  </select>
                </div>

                <div className="form-group">
                  <label className="input-label">Description (optional)</label>
                  <textarea
                    className="input-field"
                    placeholder="Describe the scam briefly..."
                    value={description}
                    onChange={(e) => setDescription(e.target.value)}
                    rows={3}
                  />
                </div>

                <button className="btn btn-danger w-full" type="submit" disabled={submitting}>
                  {submitting ? (
                    <><Loader2 size={18} className="spinning" /> Submitting...</>
                  ) : (
                    <><Send size={18} /> Submit Report</>
                  )}
                </button>

                {submitResult && (
                  <div className={`report-result ${submitResult.status === 'error' ? 'report-result-error' : 'report-result-success'}`}>
                    {submitResult.message}
                  </div>
                )}
              </form>
            ) : (
              <form className="glass report-form" onSubmit={handleCheck}>
                <h3 className="form-title">Check an Identifier</h3>
                <p className="text-muted mb-md" style={{ fontSize: '0.875rem' }}>
                  Enter an email, phone number, website, or UPI ID to check our database.
                </p>

                <div className="form-group">
                  <label className="input-label">Identifier</label>
                  <input
                    className="input-field"
                    type="text"
                    placeholder="e.g. hr.microsoft@gmail.com"
                    value={checkQuery}
                    onChange={(e) => setCheckQuery(e.target.value)}
                    required
                  />
                </div>

                <button className="btn btn-primary w-full" type="submit" disabled={checking}>
                  {checking ? (
                    <><Loader2 size={18} className="spinning" /> Checking...</>
                  ) : (
                    <><Search size={18} /> Check Database</>
                  )}
                </button>

                {checkResult && (
                  <div className={`report-result ${checkResult.found ? 'report-result-warning' : 'report-result-safe'}`}>
                    {checkResult.found ? (
                      <>
                        <strong>⚠️ Found in scam database!</strong>
                        <p>{checkResult.message}</p>
                        <p style={{ fontSize: '0.8125rem', marginTop: '4px' }}>
                          Reported {checkResult.total_reports} time(s)
                        </p>
                      </>
                    ) : (
                      <>
                        <strong>✅ Not found</strong>
                        <p>{checkResult.message}</p>
                      </>
                    )}
                  </div>
                )}
              </form>
            )}
          </div>

          {/* ── Recent Reports Feed ──────────────────────────────────────── */}
          <div className="recent-panel animate-fade-in-up" style={{ animationDelay: '0.2s' }}>
            <div className="glass" style={{ padding: '24px' }}>
              <h3 className="recent-title">
                <Clock size={18} />
                Recent Reports
              </h3>

              {loadingRecent ? (
                <div className="flex items-center justify-center" style={{ padding: '32px' }}>
                  <div className="spinner spinner-sm"></div>
                </div>
              ) : recentReports.length === 0 ? (
                <p className="text-muted" style={{ padding: '24px', textAlign: 'center', fontSize: '0.875rem' }}>
                  No reports yet. Be the first to report a scam!
                </p>
              ) : (
                <div className="recent-list">
                  {recentReports.map((report, idx) => (
                    <div key={idx} className="recent-item">
                      <div className="recent-item-icon">
                        {typeIcon[report.report_type] || <AlertTriangle size={14} />}
                      </div>
                      <div className="recent-item-content">
                        <span className="recent-item-id">{report.identifier}</span>
                        {report.company_name && (
                          <span className="recent-item-company">{report.company_name}</span>
                        )}
                      </div>
                      <span className={`badge badge-severity-${report.report_count > 3 ? 'high' : report.report_count > 1 ? 'medium' : 'low'}`}>
                        {report.report_count}x
                      </span>
                    </div>
                  ))}
                </div>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}

export default ReportPage
