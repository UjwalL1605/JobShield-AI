import { useState } from 'react'
import { Shield, Send, Loader2, RotateCcw } from 'lucide-react'
import FileUpload from '../components/FileUpload'
import ResultCard from '../components/ResultCard'
import RiskFactorTable from '../components/RiskFactorTable'
import HighlightedText from '../components/HighlightedText'
import WebIntelligenceCard from '../components/WebIntelligenceCard'
import { analyzeText, analyzeScreenshot } from '../api/client'
import './AnalyzePage.css'

const SOURCE_TYPES = [
  { value: 'job_posting', label: 'Job Posting' },
  { value: 'email', label: 'Email' },
  { value: 'whatsapp', label: 'WhatsApp' },
  { value: 'linkedin', label: 'LinkedIn' },
  { value: 'telegram', label: 'Telegram' },
  { value: 'sms', label: 'SMS' },
  { value: 'instagram', label: 'Instagram DM' },
  { value: 'other', label: 'Other' },
]

function AnalyzePage() {
  const [activeTab, setActiveTab] = useState('text')
  const [text, setText] = useState('')
  const [sourceType, setSourceType] = useState('job_posting')
  const [file, setFile] = useState(null)
  const [loading, setLoading] = useState(false)
  const [result, setResult] = useState(null)
  const [error, setError] = useState('')
  const [ocrText, setOcrText] = useState('')

  const handleAnalyze = async () => {
    setError('')
    setResult(null)
    setOcrText('')

    if (activeTab === 'text') {
      if (!text.trim() || text.trim().length < 10) {
        setError('Please enter at least 10 characters for meaningful analysis.')
        return
      }
      setLoading(true)
      try {
        const data = await analyzeText(text.trim(), sourceType)
        setResult(data)
      } catch (err) {
        setError(err.response?.data?.detail || 'Analysis failed. Make sure the backend server is running.')
      } finally {
        setLoading(false)
      }
    } else {
      if (!file) {
        setError('Please upload a screenshot first.')
        return
      }
      setLoading(true)
      try {
        const data = await analyzeScreenshot(file, sourceType)
        if (data.analysis) {
          setResult(data.analysis)
          setOcrText(data.ocr_result?.extracted_text || '')
        } else {
          setError(data.message || 'No text could be extracted from the image.')
        }
      } catch (err) {
        setError(err.response?.data?.detail || 'Screenshot analysis failed. Make sure the backend server is running.')
      } finally {
        setLoading(false)
      }
    }
  }

  const handleReset = () => {
    setText('')
    setFile(null)
    setResult(null)
    setError('')
    setOcrText('')
  }

  return (
    <div className="analyze-page">
      <div className="container">
        <div className="analyze-header animate-fade-in-up">
          <h1 className="analyze-title">
            <Shield size={28} className="text-gradient-icon" />
            Analyze for Scams
          </h1>
          <p className="analyze-subtitle">
            Paste a message or upload a screenshot to check for scam indicators
          </p>
        </div>

        <div className="analyze-layout">
          {/* ── Input Panel ─────────────────────────────────────────────────── */}
          <div className="analyze-input-panel animate-fade-in-up" style={{ animationDelay: '0.1s' }}>
            <div className="glass" style={{ padding: '24px' }}>
              {/* Tabs */}
              <div className="tabs">
                <button
                  className={`tab ${activeTab === 'text' ? 'active' : ''}`}
                  onClick={() => setActiveTab('text')}
                >
                  📝 Paste Text
                </button>
                <button
                  className={`tab ${activeTab === 'screenshot' ? 'active' : ''}`}
                  onClick={() => setActiveTab('screenshot')}
                >
                  📸 Upload Screenshot
                </button>
              </div>

              {/* Source Type */}
              <div className="mb-md">
                <label className="input-label">Source Type</label>
                <select
                  className="input-field"
                  value={sourceType}
                  onChange={(e) => setSourceType(e.target.value)}
                >
                  {SOURCE_TYPES.map((s) => (
                    <option key={s.value} value={s.value}>{s.label}</option>
                  ))}
                </select>
              </div>

              {/* Text Input */}
              {activeTab === 'text' && (
                <div className="mb-md">
                  <label className="input-label">
                    Message Content
                    <span className="char-count">{text.length} chars</span>
                  </label>
                  <textarea
                    className="input-field analyze-textarea"
                    placeholder="Paste the job description, email, WhatsApp message, or LinkedIn conversation here..."
                    value={text}
                    onChange={(e) => setText(e.target.value)}
                    rows={10}
                  />
                </div>
              )}

              {/* Screenshot Upload */}
              {activeTab === 'screenshot' && (
                <div className="mb-md">
                  <label className="input-label">Screenshot</label>
                  <FileUpload
                    onFileSelect={setFile}
                    disabled={loading}
                  />
                </div>
              )}

              {/* Error */}
              {error && (
                <div className="analyze-error animate-fade-in">
                  ⚠️ {error}
                </div>
              )}

              {/* Actions */}
              <div className="analyze-actions">
                <button
                  className="btn btn-primary btn-lg w-full"
                  onClick={handleAnalyze}
                  disabled={loading}
                >
                  {loading ? (
                    <>
                      <Loader2 size={20} className="spinning" />
                      Analyzing...
                    </>
                  ) : (
                    <>
                      <Send size={18} />
                      Analyze
                    </>
                  )}
                </button>
                {result && (
                  <button className="btn btn-ghost" onClick={handleReset}>
                    <RotateCcw size={16} />
                    Reset
                  </button>
                )}
              </div>
            </div>
          </div>

          {/* ── Results Panel ───────────────────────────────────────────────── */}
          <div className="analyze-results-panel">
            {loading && (
              <div className="analyze-loading glass">
                <div className="spinner"></div>
                <p>Running AI analysis pipeline...</p>
                <span className="text-muted" style={{ fontSize: '0.8125rem' }}>
                  ML Model → Rule Engine → Email Check → Salary Validation
                </span>
              </div>
            )}

            {result && !loading && (
              <div className="results-stack stagger">
                <ResultCard
                  scamProbability={result.scam_probability}
                  trustLevel={result.trust_level}
                />

                {/* ML + Rule Score Breakdown */}
                <div className="score-breakdown glass animate-fade-in-up" style={{ animationDelay: '0.1s' }}>
                  <h4 className="breakdown-title">Score Breakdown</h4>
                  <div className="breakdown-bars">
                    <div className="breakdown-item">
                      <span className="breakdown-label">ML Model</span>
                      <div className="breakdown-bar-track">
                        <div
                          className="breakdown-bar-fill breakdown-bar-ml"
                          style={{ width: `${result.ml_score}%` }}
                        ></div>
                      </div>
                      <span className="breakdown-value">{result.ml_score}%</span>
                    </div>
                    <div className="breakdown-item">
                      <span className="breakdown-label">Rule Engine</span>
                      <div className="breakdown-bar-track">
                        <div
                          className="breakdown-bar-fill breakdown-bar-rule"
                          style={{ width: `${result.rule_score}%` }}
                        ></div>
                      </div>
                      <span className="breakdown-value">{result.rule_score}%</span>
                    </div>
                  </div>
                </div>

                {/* Known scam warnings */}
                {result.known_scam_warnings && result.known_scam_warnings.length > 0 && (
                  <div className="known-warning glass animate-fade-in-up">
                    <h4>⚠️ Known Scam Alert</h4>
                    {result.known_scam_warnings.map((w, idx) => (
                      <p key={idx} className="known-warning-text">{w.message}</p>
                    ))}
                  </div>
                )}

                {/* Web & Entity Intelligence (Google Search Verification & Domain Checks) */}
                {result.web_intelligence && (
                  <WebIntelligenceCard webIntelligence={result.web_intelligence} />
                )}

                <RiskFactorTable
                  riskFactors={result.risk_factors}
                  emailAnalysis={result.email_analysis}
                  salaryAnalysis={result.salary_analysis}
                />

                <HighlightedText
                  text={ocrText || result.original_text}
                  keywords={result.scam_keywords}
                />

                {/* ML Feature Insights */}
                {result.ml_top_features && result.ml_top_features.length > 0 && (
                  <div className="ml-features glass animate-fade-in-up" style={{ animationDelay: '0.35s' }}>
                    <h3 className="ml-features-title">🧠 ML Model Insights</h3>
                    <p className="text-muted mb-md" style={{ fontSize: '0.8125rem' }}>
                      Top features the ML model used for its prediction
                    </p>
                    <div className="ml-features-list">
                      {result.ml_top_features.map((feat, idx) => (
                        <div key={idx} className="ml-feature-row">
                          <code className="ml-feature-name">{feat.feature}</code>
                          <span className={`badge ${feat.direction === 'scam' ? 'badge-very-high-risk' : 'badge-safe'}`}>
                            {feat.direction}
                          </span>
                          <span className="ml-feature-score">
                            {feat.contribution > 0 ? '+' : ''}{feat.contribution.toFixed(3)}
                          </span>
                        </div>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            )}

            {!result && !loading && (
              <div className="analyze-empty glass">
                <div className="analyze-empty-icon animate-float">
                  <Shield size={48} />
                </div>
                <h3>Ready to Analyze</h3>
                <p className="text-muted">
                  Paste a suspicious message or upload a screenshot to get started.
                </p>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  )
}

export default AnalyzePage
