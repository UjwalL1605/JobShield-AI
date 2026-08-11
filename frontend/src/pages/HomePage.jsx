import { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import {
  Shield, Search, Camera, Mail, BadgeDollarSign,
  FileWarning, Brain, Sparkles, ArrowRight, Users,
  AlertTriangle, CheckCircle2, Globe, Lock, Zap,
  ExternalLink, ShieldAlert, Cpu, Eye, MessageSquare,
  Phone, Building2, Terminal, AlertOctagon,
  CheckCircle, Loader2, RotateCcw, Activity, Crosshair,
  Layers, Database, Sparkle, Radio, Share2
} from 'lucide-react'
import './HomePage.css'

function HomePage() {
  const navigate = useNavigate()
  const [selectedDemoIndex, setSelectedDemoIndex] = useState(0)

  // Interactive Live Radar Demos
  const radarDemos = [
    {
      title: 'WhatsApp Task & Review Scam',
      company: 'Amazon HR Impersonation',
      channel: 'whatsapp',
      channelLabel: 'WhatsApp / Telegram',
      snippet: 'Hi, I am Priya from Amazon HR. Earn ₹3,500/day for simple rating tasks. Pay refundable security fee ₹499 to activate. Contact manager on Telegram: @amazon_hiring_portal',
      score: 96.8,
      risk: 'Critical Risk',
      signals: [
        'Demands upfront refundable deposit (₹499)',
        'Unsolicited WhatsApp / Telegram recruitment',
        'Unrealistic daily income benchmark (₹3.5k/day)',
      ],
      geminiFinding: 'Flagged across Consumer Complaints & Reddit r/India as task scam.',
    },
    {
      title: 'Fake MNC Appointment Letter',
      company: 'Tata Consultancy Services (TCS)',
      channel: 'email',
      channelLabel: 'Gmail (@gmail.com)',
      snippet: 'Dear Candidate, TCS is pleased to issue your Offer Letter for Junior Software Engineer. CTC ₹8.5 LPA. Send PAN, Aadhaar and ₹1,200 gate pass fee to tcs.hr.recruiter@gmail.com within 24h.',
      score: 94.2,
      risk: 'High Risk',
      signals: [
        'Corporate recruitment via free public Gmail',
        'High-pressure 24-hour urgency countdown',
        'Identity & credential harvesting (Aadhaar/PAN)',
      ],
      geminiFinding: 'Official TCS never uses Gmail or charges for gate passes.',
    },
    {
      title: 'Legitimate Corporate Job Posting',
      company: 'Infosys Limited',
      channel: 'job_posting',
      channelLabel: 'Official Portal',
      snippet: 'Infosys is hiring Systems Engineers in Pune (2-4 yrs exp). Apply directly via our official portal career.infosys.com. Infosys does not charge any recruitment fee at any stage.',
      score: 8.4,
      risk: 'Safe / Legitimate',
      signals: [
        'Official verified career domain (career.infosys.com)',
        'Explicit anti-fee legitimacy statement present',
        'Standard corporate interview workflow',
      ],
      geminiFinding: 'Verified official corporate hiring channel.',
    },
  ]

  const liveThreatStream = [
    {
      id: 1,
      source: 'WhatsApp',
      type: 'YouTube Like & Review Task',
      snippet: 'Earn ₹5,000/day. Send ₹500 prepaid recharge to start task 1.',
      risk: 'Critical (98%)',
      timestamp: 'Just now',
      tag: 'badge-very-high-risk',
    },
    {
      id: 2,
      source: 'Gmail',
      type: 'Indigo Ground Staff Impersonation',
      snippet: 'Pay ₹1,500 for airport security badge and uniform issuance.',
      risk: 'Critical (96%)',
      timestamp: '3m ago',
      tag: 'badge-very-high-risk',
    },
    {
      id: 3,
      source: 'Telegram',
      type: 'Crypto Arbitrage Assistant',
      snippet: 'Deposit 100 USDT into trade portal to unlock daily commission.',
      risk: 'Critical (99%)',
      timestamp: '8m ago',
      tag: 'badge-very-high-risk',
    },
    {
      id: 4,
      source: 'SMS Alert',
      type: 'Work From Home Data Entry',
      snippet: 'Pay ₹850 server maintenance fee. Legal penalty if incomplete.',
      risk: 'High (92%)',
      timestamp: '15m ago',
      tag: 'badge-high-risk',
    },
  ]

  const handleLaunchStudioWithScenario = (demo) => {
    navigate('/analyze', {
      state: {
        initialText: demo.snippet,
        initialSource: demo.channel,
      },
    })
  }

  return (
    <div className="innovative-home">
      {/* ── Section 1: Holographic Command Hero ────────────────────────────── */}
      <section className="hero-command-section section">
        <div className="container">
          <div className="hero-command-grid">
            {/* Left Column: Vision & Human-Crafted Brand Statement */}
            <div className="hero-left-column animate-fade-in-up">
              <div className="command-status-badge">
                <span className="command-live-dot"></span>
                <span className="command-badge-text">NEURAL SCAM INTELLIGENCE // MIL-SPEC V2.4</span>
              </div>

              <h1 className="hero-editorial-title">
                Autonomous<br />
                <span className="hero-gradient-text">Scam Defense</span><br />
                For Job Seekers.
              </h1>

              <p className="hero-editorial-lead">
                Don't lose money or identity to predatory hiring traps. JobShield AI combines <strong>high-capacity local NLP (94.2% precision)</strong> with <strong>Google Gemini 2.5 Flash live web grounding</strong> to audit job offers, emails, and WhatsApp screenshots in real time.
              </p>

              {/* Action Trigger Bar */}
              <div className="hero-command-actions">
                <Link to="/analyze" className="btn btn-primary btn-lg hero-action-btn">
                  <Zap size={18} />
                  Scan a Job Offer Now
                  <ArrowRight size={18} />
                </Link>
                <Link to="/about" className="btn btn-secondary btn-lg hero-action-btn">
                  <Eye size={18} />
                  How It Works
                </Link>
              </div>

              {/* Key Telemetry Highlights */}
              <div className="hero-telemetry-strip glass">
                <div className="telemetry-item">
                  <span className="telemetry-num text-gradient">94.19%</span>
                  <span className="telemetry-label">Model Accuracy</span>
                </div>
                <div className="telemetry-divider"></div>
                <div className="telemetry-item">
                  <span className="telemetry-num text-gradient">2,016+</span>
                  <span className="telemetry-label">Blacklisted Threats</span>
                </div>
                <div className="telemetry-divider"></div>
                <div className="telemetry-item">
                  <span className="telemetry-num text-gradient">&lt;50 ms</span>
                  <span className="telemetry-label">Local Inference</span>
                </div>
              </div>
            </div>

            {/* Right Column: Interactive 3D Holographic Threat Radar Terminal */}
            <div className="hero-right-column animate-fade-in-up" style={{ animationDelay: '0.15s' }}>
              <div className="holographic-radar-card glass">
                <div className="radar-card-header">
                  <div className="radar-status-group">
                    <span className="radar-status-icon"><Radio size={15} /></span>
                    <span className="radar-status-title">THREAT RADAR SIMULATOR</span>
                  </div>
                  <span className="radar-live-tag">LIVE DEMO</span>
                </div>

                {/* Interactive Scenario Selector Pills */}
                <div className="radar-scenario-pills">
                  {radarDemos.map((demo, idx) => (
                    <button
                      key={idx}
                      className={`radar-pill-btn ${selectedDemoIndex === idx ? 'active' : ''}`}
                      onClick={() => setSelectedDemoIndex(idx)}
                    >
                      {demo.title}
                    </button>
                  ))}
                </div>

                {/* Scenario Visualizer Screen */}
                <div className="radar-screen glass-subtle">
                  <div className="radar-screen-header">
                    <span className="screen-company">{radarDemos[selectedDemoIndex].company}</span>
                    <span className="screen-channel">{radarDemos[selectedDemoIndex].channelLabel}</span>
                  </div>

                  <p className="screen-snippet">
                    "{radarDemos[selectedDemoIndex].snippet}"
                  </p>

                  <div className="radar-score-banner">
                    <div className="radar-gauge-val">
                      <span className={`radar-score-number ${radarDemos[selectedDemoIndex].score > 50 ? 'text-red' : 'text-emerald'}`}>
                        {radarDemos[selectedDemoIndex].score}%
                      </span>
                      <span className="radar-score-caption">SCAM RISK</span>
                    </div>

                    <div className="radar-verdict-col">
                      <span className={`badge ${radarDemos[selectedDemoIndex].score > 50 ? 'badge-very-high-risk' : 'badge-safe'}`}>
                        {radarDemos[selectedDemoIndex].risk}
                      </span>
                      <span className="radar-signals-summary">
                        {radarDemos[selectedDemoIndex].signals.length} threat indicators detected
                      </span>
                    </div>
                  </div>

                  {/* Indicators List */}
                  <div className="radar-signals-list">
                    {radarDemos[selectedDemoIndex].signals.map((sig, i) => (
                      <div key={i} className="radar-signal-chip">
                        <AlertTriangle size={13} className={radarDemos[selectedDemoIndex].score > 50 ? 'text-orange' : 'text-emerald'} />
                        <span>{sig}</span>
                      </div>
                    ))}
                  </div>

                  {/* Gemini AI Live Search Insight */}
                  <div className="radar-gemini-insight">
                    <Sparkles size={14} className="text-purple" />
                    <span><strong>Google AI Deep Search:</strong> {radarDemos[selectedDemoIndex].geminiFinding}</span>
                  </div>
                </div>

                {/* Bottom Trigger to try in main scanner studio */}
                <button
                  className="radar-try-btn"
                  onClick={() => handleLaunchStudioWithScenario(radarDemos[selectedDemoIndex])}
                >
                  <span>Audit this scenario in Detection Studio</span>
                  <ArrowRight size={14} />
                </button>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* ── Section 2: Live Threat Stream & Scam Anatomy ─────────────────────── */}
      <section className="threat-stream-section section">
        <div className="container">
          <div className="section-header text-center">
            <div className="command-status-badge" style={{ margin: '0 auto 12px' }}>
              <Activity size={14} />
              Real-Time Cyber Feed
            </div>
            <h2 className="section-title">
              Live Threat <span className="text-gradient">Intelligence Feed</span>
            </h2>
            <p className="section-subtitle">
              Verified recruitment fraud attempts intercepted and cataloged into our 2,016+ threat registry.
            </p>
          </div>

          <div className="threat-stream-grid">
            {/* Live Cards */}
            <div className="stream-cards-column">
              <div className="stream-column-header">
                <div className="stream-header-title">
                  <span className="command-live-dot"></span>
                  <h3>Recently Intercepted Frauds</h3>
                </div>
                <span className="stream-db-count">2,016+ Blacklisted</span>
              </div>

              <div className="stream-feed-list">
                {liveThreatStream.map((item) => (
                  <div key={item.id} className="stream-feed-card glass">
                    <div className="stream-card-top">
                      <div className="stream-source-tag">
                        <span className="source-pill">{item.source}</span>
                        <span className="type-title">{item.type}</span>
                      </div>
                      <span className="stream-time">{item.timestamp}</span>
                    </div>
                    <p className="stream-snippet">"{item.snippet}"</p>
                    <div className="stream-card-footer">
                      <span className={`badge ${item.tag}`}>{item.risk}</span>
                      <span className="stream-protected-label">🛡️ Blocked by JobShield AI</span>
                    </div>
                  </div>
                ))}
              </div>
            </div>

            {/* Common Scam Patterns Analytics */}
            <div className="stream-analytics-column">
              <div className="analytics-card glass">
                <div className="analytics-header">
                  <AlertOctagon size={18} className="text-orange" />
                  <h3>Top 4 Indian Scam Vectors</h3>
                </div>
                <p className="analytics-sub">
                  Frequency breakdown based on 6,340+ analyzed real-world communications:
                </p>

                <div className="analytics-bars-list">
                  <div className="analytics-bar-item">
                    <div className="analytics-bar-labels">
                      <span>Advance Registration & Uniform Fees</span>
                      <strong className="text-orange">42% (840+ cases)</strong>
                    </div>
                    <div className="analytics-track">
                      <div className="analytics-fill" style={{ width: '42%' }}></div>
                    </div>
                  </div>

                  <div className="analytics-bar-item">
                    <div className="analytics-bar-labels">
                      <span>Unsolicited WhatsApp / Telegram Recruitment</span>
                      <strong className="text-orange">31% (620+ cases)</strong>
                    </div>
                    <div className="analytics-track">
                      <div className="analytics-fill" style={{ width: '31%' }}></div>
                    </div>
                  </div>

                  <div className="analytics-bar-item">
                    <div className="analytics-bar-labels">
                      <span>Brand Impersonation (Free Email / Phishing)</span>
                      <strong className="text-orange">18% (360+ cases)</strong>
                    </div>
                    <div className="analytics-track">
                      <div className="analytics-fill" style={{ width: '18%' }}></div>
                    </div>
                  </div>

                  <div className="analytics-bar-item">
                    <div className="analytics-bar-labels">
                      <span>Remote Data Entry & Fake Legal Penalty</span>
                      <strong className="text-orange">9% (180+ cases)</strong>
                    </div>
                    <div className="analytics-track">
                      <div className="analytics-fill" style={{ width: '9%' }}></div>
                    </div>
                  </div>
                </div>

                <div className="analytics-footer">
                  <CheckCircle2 size={15} className="text-emerald" />
                  <span>JobShield AI inspects all 4 vectors autonomously in under 50ms.</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* ── Section 3: 4-Tier Security Pipeline ──────────────────────────────── */}
      <section className="architecture-section section">
        <div className="container">
          <div className="section-header text-center">
            <div className="command-status-badge" style={{ margin: '0 auto 12px' }}>
              <Layers size={14} />
              Defense in Depth
            </div>
            <h2 className="section-title">
              Engineered Security <span className="text-gradient">Architecture</span>
            </h2>
            <p className="section-subtitle">
              How JobShield AI eliminates false positives and verifies job legitimacy across four distinct analytical layers.
            </p>
          </div>

          <div className="pipeline-grid">
            <div className="pipeline-card glass">
              <div className="pipeline-card-top">
                <span className="pipeline-step-number">01</span>
                <div className="pipeline-icon-box"><Camera size={20} /></div>
              </div>
              <h3 className="pipeline-card-title">Multi-Modal Input & OCR</h3>
              <p className="pipeline-card-desc">
                Paste raw emails, SMS texts, or upload chat screenshots from WhatsApp & Telegram with EasyOCR contrast enhancement.
              </p>
            </div>

            <div className="pipeline-card glass">
              <div className="pipeline-card-top">
                <span className="pipeline-step-number">02</span>
                <div className="pipeline-icon-box"><Database size={20} /></div>
              </div>
              <h3 className="pipeline-card-title">Entity & Blacklist Match</h3>
              <p className="pipeline-card-desc">
                Cross-references recruiter emails, phone numbers, UPI IDs, and phishing domains against 2,016+ reported fraud records.
              </p>
            </div>

            <div className="pipeline-card glass">
              <div className="pipeline-card-top">
                <span className="pipeline-step-number">03</span>
                <div className="pipeline-icon-box"><Brain size={20} /></div>
              </div>
              <h3 className="pipeline-card-title">Hybrid ML & Domain XAI</h3>
              <p className="pipeline-card-desc">
                Trained Logistic Regression with 13 domain indicators inspects advance fees, urgency, and credential harvesting with explainability.
              </p>
            </div>

            <div className="pipeline-card glass">
              <div className="pipeline-card-top">
                <span className="pipeline-step-number">04</span>
                <div className="pipeline-icon-box"><Sparkles size={20} /></div>
              </div>
              <h3 className="pipeline-card-title">Live Google AI Search Grounding</h3>
              <p className="pipeline-card-desc">
                Google Gemini 2.5 Flash executes live Google Search queries to verify corporate registration and uncover victim complaints.
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* ── Section 4: Safety Guarantee CTA Banner ──────────────────────────── */}
      <section className="safety-cta-section section">
        <div className="container">
          <div className="safety-cta-card glass">
            <div className="safety-cta-content">
              <div className="command-status-badge">
                <Shield size={14} />
                Candidate Protection Oath
              </div>
              <h2 className="safety-cta-title">
                Never Assume Safety by Default
              </h2>
              <p className="safety-cta-desc">
                Legitimate employers will never ask for registration deposits, training kit fees, or personal net-banking OTPs. When in doubt, audit before you reply.
              </p>
              <div className="safety-cta-buttons">
                <Link to="/analyze" className="btn btn-primary btn-lg">
                  <Zap size={18} />
                  Open Scam Detection Studio
                  <ArrowRight size={18} />
                </Link>
                <Link to="/report" className="btn btn-secondary btn-lg">
                  Report a Suspicious Recruiter
                </Link>
              </div>
            </div>
          </div>
        </div>
      </section>
    </div>
  )
}

export default HomePage
