import { useState, useEffect } from 'react'
import { useLocation } from 'react-router-dom'
import {
  Shield, Send, Loader2, RotateCcw, Clipboard,
  Sparkles, AlertTriangle, CheckCircle2, FileText,
  Camera, Zap, ArrowRight, Building2, HelpCircle
} from 'lucide-react'
import FileUpload from '../components/FileUpload'
import ResultCard from '../components/ResultCard'
import RiskFactorTable from '../components/RiskFactorTable'
import HighlightedText from '../components/HighlightedText'
import WebIntelligenceCard from '../components/WebIntelligenceCard'
import GeminiSearchCard from '../components/GeminiSearchCard'
import { analyzeText, analyzeScreenshot } from '../api/client'
import './AnalyzePage.css'

const SOURCE_TYPES = [
  { value: 'job_posting', label: '📄 Job Portal / Website' },
  { value: 'email', label: '✉️ Email Offer Letter' },
  { value: 'whatsapp', label: '💬 WhatsApp Message' },
  { value: 'telegram', label: '✈️ Telegram Group / Channel' },
  { value: 'linkedin', label: '💼 LinkedIn Recruiter Message' },
  { value: 'sms', label: '📱 SMS Alert' },
  { value: 'instagram', label: '📸 Instagram DM' },
  { value: 'other', label: '🌐 Other Platform' },
]

const SAMPLE_PRESETS = [
  {
    label: '⚡ WhatsApp Task Scam',
    type: 'whatsapp',
    text: 'Hi, I am Priya from Amazon HR. You have been shortlisted for our Remote Product Review & Data Entry role. Work 1-2 hrs daily and earn ₹3,500 to ₹8,000/day. No experience required. To activate your employee portal, pay a refundable registration deposit of ₹499. Contact hiring manager on Telegram: @amazon_hiring_official',
  },
  {
    label: '🏢 Fake Google Offer Letter',
    type: 'email',
    text: 'Dear Candidate, Google India is pleased to offer you the position of Junior Cloud Support Associate. Monthly CTC is ₹65,000. Review your offer at http://google-careers-portal.site and reply with your Aadhaar, PAN card, and bank account details to google.recruitment.hr@gmail.com within 24 hours.',
  },
  {
    label: '🟢 Genuine TCS Posting',
    type: 'job_posting',
    text: 'Tata Consultancy Services (TCS) is hiring React and Node.js Developers for Bengaluru location. 2-4 years experience required. Apply directly through official portal at https://careers.tcs.com. TCS is an equal opportunity employer and never requests any registration fee, caution deposit, or monetary payment at any stage of recruitment.',
  },
]

function AnalyzePage() {
  const location = useLocation()
  const [activeTab, setActiveTab] = useState('text')
  const [text, setText] = useState('')
  const [sourceType, setSourceType] = useState('job_posting')
  const [file, setFile] = useState(null)
  const [loading, setLoading] = useState(false)
  const [result, setResult] = useState(null)
  const [error, setError] = useState('')
  const [ocrText, setOcrText] = useState('')

  // Handle incoming sample text from HomePage navigation
  useEffect(() => {
    if (location.state?.initialText) {
      setText(location.state.initialText)
      if (location.state?.initialSource) {
        setSourceType(location.state.initialSource)
      }
      // Automatically trigger analysis for seamless demo
      executeAnalysis(location.state.initialText, location.state?.initialSource || 'whatsapp')
    }
  }, [location.state])

  const executeAnalysis = async (contentToAnalyze, source) => {
    setError('')
    setResult(null)
    setOcrText('')
    setLoading(true)

    try {
      const data = await analyzeText(contentToAnalyze.trim(), source)
      setResult(data)
    } catch (err) {
      setError(err.response?.data?.detail || 'Analysis failed. Make sure the backend server is running.')
    } finally {
      setLoading(false)
    }
  }

  const handleAnalyze = async () => {
    setError('')
    setResult(null)
    setOcrText('')

    if (activeTab === 'text') {
      if (!text.trim() || text.trim().length < 10) {
        setError('Please enter at least 10 characters for meaningful analysis.')
        return
      }
      executeAnalysis(text, sourceType)
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

  const handlePasteClipboard = async () => {
    try {
      const clipText = await navigator.clipboard.readText()
      if (clipText) {
        setText(clipText)
        setError('')
      }
    } catch (err) {
      setError('Clipboard access denied. Please paste directly into the box.')
    }
  }

  const handleLoadPreset = (preset) => {
    setText(preset.text)
    setSourceType(preset.type)
    setError('')
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
        {/* ── Header ───────────────────────────────────────────────────────── */}
        <div className="analyze-header animate-fade-in-up">
          <div className="analyze-badge">
            <Sparkles size={14} />
            Multi-Layer Fraud Detection
          </div>
          <h1 className="analyze-title">
            <Shield size={32} className="text-gradient-icon" />
            Scam Detection Studio
          </h1>
          <p className="analyze-subtitle">
            Paste a suspicious recruitment message or upload a chat screenshot to run our hybrid ML classifier, domain authenticator, and live Google AI Deep Search.
          </p>
        </div>

        <div className="analyze-layout">
          {/* ── Left Input Panel ────────────────────────────────────────────── */}
          <div className="analyze-input-panel animate-fade-in-up" style={{ animationDelay: '0.1s' }}>
            <div className="glass input-glass-card">
              {/* Tab Selector */}
              <div className="tabs">
                <button
                  className={`tab ${activeTab === 'text' ? 'active' : ''}`}
                  onClick={() => setActiveTab('text')}
                >
                  <FileText size={16} /> Paste Message / JD
                </button>
                <button
                  className={`tab ${activeTab === 'screenshot' ? 'active' : ''}`}
                  onClick={() => setActiveTab('screenshot')}
                >
                  <Camera size={16} /> Upload Screenshot
                </button>
              </div>

              {/* Source Type Selector */}
              <div className="mb-md">
                <label className="input-label">Recruitment Channel</label>
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

              {/* Text Input Tab */}
              {activeTab === 'text' && (
                <div className="mb-md">
                  <div className="textarea-header">
                    <label className="input-label" style={{ margin: 0 }}>Message Content</label>
                    <div className="textarea-actions">
                      <button
                        type="button"
                        className="btn-text-action"
                        onClick={handlePasteClipboard}
                        title="Paste from clipboard"
                      >
                        <Clipboard size={13} /> Paste
                      </button>
                      <span className="char-count">{text.length} chars</span>
                    </div>
                  </div>

                  <textarea
                    className="input-field analyze-textarea"
                    placeholder="Paste the job description, WhatsApp message, email, or Telegram chat here..."
                    value={text}
                    onChange={(e) => setText(e.target.value)}
                    rows={9}
                  />

                  {/* 1-Click Preset Loaders */}
                  <div className="preset-container">
                    <span className="preset-label">⚡ Quick Presets:</span>
                    <div className="preset-buttons">
                      {SAMPLE_PRESETS.map((preset, idx) => (
                        <button
                          key={idx}
                          type="button"
                          className="preset-chip"
                          onClick={() => handleLoadPreset(preset)}
                        >
                          {preset.label}
                        </button>
                      ))}
                    </div>
                  </div>
                </div>
              )}

              {/* Screenshot Upload Tab */}
              {activeTab === 'screenshot' && (
                <div className="mb-md">
                  <label className="input-label">Chat / Offer Screenshot</label>
                  <FileUpload
                    onFileSelect={setFile}
                    disabled={loading}
                  />
                </div>
              )}

              {/* Error Message */}
              {error && (
                <div className="analyze-error animate-fade-in">
                  <AlertTriangle size={18} />
                  <span>{error}</span>
                </div>
              )}

              {/* Action Buttons */}
              <div className="analyze-actions">
                <button
                  className="btn btn-primary btn-lg w-full"
                  onClick={handleAnalyze}
                  disabled={loading}
                >
                  {loading ? (
                    <>
                      <Loader2 size={20} className="spinning" />
                      Analyzing with AI...
                    </>
                  ) : (
                    <>
                      <Send size={18} />
                      Run Scam Investigation
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

          {/* ── Right Results Panel ─────────────────────────────────────────── */}
          <div className="analyze-results-panel">
            {loading && (
              <div className="analyze-loading glass animate-fade-in">
                <div className="spinner-container">
                  <div className="spinner"></div>
                  <div className="spinner-core">
                    <Shield size={22} className="text-gradient-icon" />
                  </div>
                </div>
                <h3 className="loading-title">Running Multi-Layer Scam Investigation...</h3>
                <div className="loading-stages">
                  <div className="loading-stage-item">
                    <span className="stage-dot dot-active"></span>
                    <span>1. Local Hybrid ML Model (94.2% Accuracy)</span>
                  </div>
                  <div className="loading-stage-item">
                    <span className="stage-dot dot-active"></span>
                    <span>2. Heuristic Rules & Advance Fee Detection</span>
                  </div>
                  <div className="loading-stage-item">
                    <span className="stage-dot dot-active"></span>
                    <span>3. Brand Impersonation & 2,000+ Threat Registry Check</span>
                  </div>
                  <div className="loading-stage-item">
                    <span className="stage-dot dot-pulse"></span>
                    <span>4. ✨ Live Google AI Search Grounding (Gemini 2.5)</span>
                  </div>
                </div>
              </div>
            )}

            {result && !loading && (
              <div className="results-stack stagger">
                {/* 1. Main Risk Verdict Gauge */}
                <ResultCard
                  scamProbability={result.scam_probability}
                  trustLevel={result.trust_level}
                />

                {/* 2. Score Breakdown Bar */}
                <div className="score-breakdown glass animate-fade-in-up" style={{ animationDelay: '0.1s' }}>
                  <h4 className="breakdown-title">Engine Score Distribution</h4>
                  <div className="breakdown-bars">
                    <div className="breakdown-item">
                      <span className="breakdown-label">ML Model (Trained on 6.3k dataset)</span>
                      <div className="breakdown-bar-track">
                        <div
                          className="breakdown-bar-fill breakdown-bar-ml"
                          style={{ width: `${result.ml_score}%` }}
                        ></div>
                      </div>
                      <span className="breakdown-value">{result.ml_score}%</span>
                    </div>
                    <div className="breakdown-item">
                      <span className="breakdown-label">Rule Engine (Domain heuristics)</span>
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

                {/* 3. Known Scam Warning from Threat Database */}
                {result.known_scam_warnings && result.known_scam_warnings.length > 0 && (
                  <div className="known-warning glass animate-fade-in-up">
                    <div className="known-warning-header">
                      <ShieldAlert size={20} className="known-warning-icon" />
                      <h4>Verified Blacklist Match in Threat Registry</h4>
                    </div>
                    {result.known_scam_warnings.map((w, idx) => (
                      <p key={idx} className="known-warning-text">{w.message}</p>
                    ))}
                  </div>
                )}

                {/* 4. Google AI Deep Search Grounding Card */}
                {result.gemini_analysis && (
                  <GeminiSearchCard geminiAnalysis={result.gemini_analysis} />
                )}

                {/* 5. Web & Entity Intelligence Card */}
                {result.web_intelligence && (
                  <WebIntelligenceCard webIntelligence={result.web_intelligence} />
                )}

                {/* 6. Itemized Risk Factors & Evidence Table */}
                <RiskFactorTable
                  riskFactors={result.risk_factors}
                  emailAnalysis={result.email_analysis}
                  salaryAnalysis={result.salary_analysis}
                />

                {/* 7. Highlighted Text with Annotated Keyword Pills */}
                <HighlightedText
                  text={ocrText || result.original_text}
                  keywords={result.scam_keywords}
                />

                {/* 8. ML Feature Insights (XAI) */}
                {result.ml_top_features && result.ml_top_features.length > 0 && (
                  <div className="ml-features glass animate-fade-in-up" style={{ animationDelay: '0.35s' }}>
                    <div className="ml-features-header">
                      <Brain size={18} className="text-indigo" />
                      <h3 className="ml-features-title">Explainable AI (XAI) Feature Weights</h3>
                    </div>
                    <p className="text-muted mb-md" style={{ fontSize: '0.8125rem' }}>
                      Exact linguistic n-grams and domain indicators that influenced the machine learning prediction:
                    </p>
                    <div className="ml-features-list">
                      {result.ml_top_features.map((feat, idx) => (
                        <div key={idx} className="ml-feature-row">
                          <code className="ml-feature-name">{feat.feature}</code>
                          <span className={`badge ${feat.direction === 'scam' ? 'badge-very-high-risk' : 'badge-safe'}`}>
                            {feat.direction}
                          </span>
                          <span className="ml-feature-score">
                            {typeof feat.contribution === 'number'
                              ? `${feat.contribution > 0 ? '+' : ''}${feat.contribution.toFixed(3)}`
                              : (feat.contribution || '')}
                          </span>
                        </div>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            )}

            {!result && !loading && (
              <div className="analyze-empty glass animate-fade-in">
                <div className="analyze-empty-icon animate-float">
                  <Shield size={56} />
                </div>
                <h3>Ready to Investigate</h3>
                <p className="text-muted" style={{ maxWidth: '420px', margin: '8px auto 20px' }}>
                  Paste any job description, WhatsApp message, email, or upload a screenshot to inspect for fraud signals.
                </p>
                <div className="empty-quick-steps">
                  <div className="empty-step">
                    <span className="empty-step-num">1</span>
                    <span>Paste text or image</span>
                  </div>
                  <ArrowRight size={14} className="empty-arrow" />
                  <div className="empty-step">
                    <span className="empty-step-num">2</span>
                    <span>AI audits red flags</span>
                  </div>
                  <ArrowRight size={14} className="empty-arrow" />
                  <div className="empty-step">
                    <span className="empty-step-num">3</span>
                    <span>Instant verdict & proof</span>
                  </div>
                </div>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  )
}

export default AnalyzePage
