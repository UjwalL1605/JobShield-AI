import { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import {
  Shield, Search, Camera, Mail, BadgeDollarSign,
  FileWarning, Brain, Sparkles, ArrowRight, Users,
  AlertTriangle, CheckCircle2, Globe, Lock, Zap,
  ExternalLink, ShieldAlert, Cpu, Eye
} from 'lucide-react'
import './HomePage.css'

function HomePage() {
  const navigate = useNavigate()

  const sampleScam = "Hi, I am Priya from Amazon HR. You have been shortlisted for our Remote Product Review role. Earn ₹3,500/day. Pay refundable verification fee of ₹499 to start. Contact on Telegram: @amazon_hiring"
  const sampleLegit = "TCS is hiring React Developers for Bengaluru location (2-4 yrs exp). Apply via official portal careers.tcs.com. No registration fee required."

  const handleTrySample = (sampleText, sourceType = 'whatsapp') => {
    navigate('/analyze', { state: { initialText: sampleText, initialSource: sourceType } })
  }

  const features = [
    {
      icon: <Sparkles size={24} />,
      title: 'Google AI Deep Search',
      desc: 'Real-time Google search grounding cross-references Reddit, Glassdoor, and company databases to uncover live fraud reports.',
      color: '#a855f7',
      tag: 'New ✨',
    },
    {
      icon: <Brain size={24} />,
      title: 'Hybrid ML Classifier (94%)',
      desc: 'Trained on 6,300+ Indian job scams combining n-gram TF-IDF with 13 domain risk indicators (advance fees, KYC harvesting, urgency).',
      color: '#6366f1',
      tag: 'Local AI',
    },
    {
      icon: <Camera size={24} />,
      title: 'Screenshot OCR Engine',
      desc: 'Upload WhatsApp, Telegram, or LinkedIn chats — EasyOCR with image enhancement automatically extracts and audits text.',
      color: '#06b6d4',
      tag: 'Multi-Modal',
    },
    {
      icon: <Globe size={24} />,
      title: 'Brand Impersonation Check',
      desc: 'Instantly catches scammers posing as Amazon, Google, TCS, or Infosys while using personal WhatsApp numbers or free @gmail.com.',
      color: '#ec4899',
      tag: 'Threat Intel',
    },
    {
      icon: <BadgeDollarSign size={24} />,
      title: 'Salary Anomaly Detection',
      desc: 'Evaluates stated compensation against realistic industry benchmarks for fresher, internship, and remote data entry roles.',
      color: '#10b981',
      tag: 'Heuristics',
    },
    {
      icon: <FileWarning size={24} />,
      title: '2,000+ Threat Registry',
      desc: 'Pre-seeded and community-driven registry of verified scam recruiters, fraudulent phone numbers, UPI IDs, and phishing links.',
      color: '#f59e0b',
      tag: 'Database',
    },
  ]

  const pipelineStages = [
    {
      step: '01',
      title: 'Multi-Modal Input',
      desc: 'Paste raw job texts, email headers, or upload screenshots from WhatsApp & Telegram with EasyOCR.',
      icon: <Camera size={20} />,
    },
    {
      step: '02',
      title: 'Domain & Entity Extraction',
      desc: 'Extracts companies, recruiter contacts, domains, UPI IDs, and cross-references 2,000+ blacklist records.',
      icon: <Cpu size={20} />,
    },
    {
      step: '03',
      title: 'Hybrid ML & XAI Engine',
      desc: 'Logistic Regression with 13 domain indicators inspects advance fees, urgency, and KYC demands with explainability.',
      icon: <Brain size={20} />,
    },
    {
      step: '04',
      title: 'Live Google Search Grounding',
      desc: 'Google Gemini 2.5 Flash queries Google Search in real-time to check live victim reports and registry proof.',
      icon: <Sparkles size={20} />,
    },
  ]

  const threatVectors = [
    {
      type: 'WhatsApp Part-Time Task Scams',
      badge: 'Critical Risk',
      desc: 'Promises ₹3,000–₹8,000/day for liking YouTube videos or reviewing products, demanding small prepaid task deposits.',
      risk: '98% Scam Probability',
    },
    {
      type: 'MNC Impersonation Letters',
      badge: 'High Risk',
      desc: 'Fake TCS, Google, or Amazon appointment letters sent from @gmail.com or newly registered .site / .online phishing domains.',
      risk: '92% Scam Probability',
    },
    {
      type: 'Remote Data Entry & Typing Fraud',
      badge: 'High Risk',
      desc: 'Demands upfront registration fees, security deposits, or legal penalty threats for unfinished arbitrary typing tasks.',
      risk: '96% Scam Probability',
    },
    {
      type: 'Crypto & Forex Trading Tasks',
      badge: 'Critical Risk',
      desc: 'Lures candidates into Telegram groups claiming trading assistant roles, asking users to deposit USDT/crypto into fake portals.',
      risk: '99% Scam Probability',
    },
  ]

  return (
    <div className="home-page">
      {/* ── Hero Section ────────────────────────────────────────────────────── */}
      <section className="hero section">
        <div className="container">
          <div className="hero-grid">
            <div className="hero-content animate-fade-in-up">
              <div className="hero-badge">
                <Sparkles size={14} className="hero-badge-sparkle" />
                <span>Next-Gen Multi-Layer Fraud Defense</span>
              </div>

              <h1 className="hero-title">
                Don't Let Fake Jobs<br />
                <span className="text-gradient">Steal Your Future</span>
              </h1>

              <p className="hero-subtitle">
                JobShield AI pairs high-speed <strong>local machine learning (94% accuracy)</strong> with <strong>real-time Google AI Search Grounding</strong> to inspect job offers, emails, and chat screenshots before you respond or pay.
              </p>

              <div className="hero-actions">
                <Link to="/analyze" className="btn btn-primary btn-lg">
                  <Shield size={20} />
                  Scan a Job Offer Now
                  <ArrowRight size={18} />
                </Link>
                <Link to="/about" className="btn btn-secondary btn-lg">
                  <Eye size={18} />
                  How It Works
                </Link>
              </div>

              {/* 1-Click Sample Previews */}
              <div className="hero-sample-pills">
                <span className="sample-pill-label">⚡ Try 1-Click Demo:</span>
                <button
                  className="sample-pill sample-pill-scam"
                  onClick={() => handleTrySample(sampleScam, 'whatsapp')}
                >
                  <AlertTriangle size={13} /> Test Scam Offer
                </button>
                <button
                  className="sample-pill sample-pill-legit"
                  onClick={() => handleTrySample(sampleLegit, 'job_posting')}
                >
                  <CheckCircle2 size={13} /> Test Legit Offer
                </button>
              </div>
            </div>

            {/* Interactive Threat Terminal Mockup */}
            <div className="hero-visual animate-fade-in-up" style={{ animationDelay: '0.2s' }}>
              <div className="terminal-card glass">
                <div className="terminal-header">
                  <div className="terminal-dots">
                    <span className="dot dot-red"></span>
                    <span className="dot dot-yellow"></span>
                    <span className="dot dot-green"></span>
                  </div>
                  <div className="terminal-title">
                    <Shield size={14} /> JobShield Threat Radar Live
                  </div>
                  <span className="badge badge-very-high-risk">LIVE SCAN</span>
                </div>

                <div className="terminal-body">
                  <div className="terminal-snippet">
                    <span className="terminal-prompt">&gt;</span>
                    <p className="terminal-text">
                      "Hi, I am Priya from Amazon HR. Earn ₹5,000/day remote. Pay ₹499 verification fee..."
                    </p>
                  </div>

                  <div className="terminal-verdict-box">
                    <div className="terminal-score-group">
                      <span className="terminal-score-num">96.8%</span>
                      <span className="terminal-score-label">SCAM RISK</span>
                    </div>
                    <div className="terminal-verdict-info">
                      <span className="badge badge-very-high-risk">Very High Risk</span>
                      <span className="terminal-verdict-sub">MNC Brand Impersonation + Advance Fee</span>
                    </div>
                  </div>

                  <div className="terminal-signals">
                    <div className="terminal-signal-item signal-red">
                      <ShieldAlert size={14} />
                      <span>Telegram / WhatsApp Recruitment Channel</span>
                    </div>
                    <div className="terminal-signal-item signal-amber">
                      <AlertTriangle size={14} />
                      <span>Registration Deposit Demanded (₹499)</span>
                    </div>
                    <div className="terminal-signal-item signal-purple">
                      <Sparkles size={14} />
                      <span>Google AI Search Grounding: Flagged on Reddit & Consumer Forums</span>
                    </div>
                  </div>
                </div>

                {/* Floating Badges */}
                <div className="terminal-floating-badge badge-top-right animate-float">
                  <Sparkles size={14} className="text-purple" />
                  <span>Gemini 2.5 Flash Grounded</span>
                </div>
                <div className="terminal-floating-badge badge-bottom-left animate-float" style={{ animationDelay: '1.5s' }}>
                  <Brain size={14} className="text-indigo" />
                  <span>94.2% ML Precision</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* ── Stats Bar ───────────────────────────────────────────────────────── */}
      <section className="stats-section">
        <div className="container">
          <div className="stats-grid glass">
            <div className="stat-card">
              <span className="stat-num text-gradient">94.19%</span>
              <span className="stat-label">Model Accuracy</span>
            </div>
            <div className="stat-card">
              <span className="stat-num text-gradient">2,016+</span>
              <span className="stat-label">Blacklisted Threats</span>
            </div>
            <div className="stat-card">
              <span className="stat-num text-gradient">0 ms</span>
              <span className="stat-label">Local Latency</span>
            </div>
            <div className="stat-card">
              <span className="stat-num text-gradient">100%</span>
              <span className="stat-label">Private & Free</span>
            </div>
          </div>
        </div>
      </section>

      {/* ── 4-Stage Security Architecture ───────────────────────────────────── */}
      <section className="architecture-section section">
        <div className="container">
          <div className="section-header text-center">
            <div className="hero-badge" style={{ margin: '0 auto 12px' }}>
              <Cpu size={14} />
              Defense in Depth
            </div>
            <h2 className="section-title">
              How JobShield AI <span className="text-gradient">Protects You</span>
            </h2>
            <p className="section-subtitle">
              A 4-tier security pipeline that combines local machine learning with real-time web intelligence.
            </p>
          </div>

          <div className="pipeline-grid">
            {pipelineStages.map((stage, idx) => (
              <div key={idx} className="pipeline-card glass">
                <div className="pipeline-step-header">
                  <span className="pipeline-step-num">{stage.step}</span>
                  <div className="pipeline-icon-circle">{stage.icon}</div>
                </div>
                <h3 className="pipeline-title">{stage.title}</h3>
                <p className="pipeline-desc">{stage.desc}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* ── Features Grid ───────────────────────────────────────────────────── */}
      <section className="features-section section">
        <div className="container">
          <div className="section-header text-center">
            <div className="hero-badge" style={{ margin: '0 auto 12px' }}>
              <Sparkles size={14} />
              Comprehensive Security
            </div>
            <h2 className="section-title">
              Engineered for <span className="text-gradient">Real-World Scams</span>
            </h2>
            <p className="section-subtitle">
              Every tool and heuristic you need to detect fraudulent job offers before losing money or personal data.
            </p>
          </div>

          <div className="features-grid">
            {features.map((feat, idx) => (
              <div key={idx} className="feature-card glass">
                <div className="feature-card-header">
                  <div
                    className="feature-icon"
                    style={{ background: `${feat.color}15`, color: feat.color, borderColor: `${feat.color}30` }}
                  >
                    {feat.icon}
                  </div>
                  <span className="feature-tag">{feat.tag}</span>
                </div>
                <h3 className="feature-title">{feat.title}</h3>
                <p className="feature-desc">{feat.desc}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* ── Modern Scam Threats Matrix ──────────────────────────────────────── */}
      <section className="threats-section section">
        <div className="container">
          <div className="section-header text-center">
            <div className="hero-badge" style={{ margin: '0 auto 12px' }}>
              <AlertTriangle size={14} />
              Threat Radar
            </div>
            <h2 className="section-title">
              Common Indian Job Scams <span className="text-gradient">We Block</span>
            </h2>
            <p className="section-subtitle">
              Scammers use sophisticated psychological tactics. Here are the top 4 vectors our engine detects instantly.
            </p>
          </div>

          <div className="threats-grid">
            {threatVectors.map((threat, idx) => (
              <div key={idx} className="threat-card glass">
                <div className="threat-header">
                  <span className={`badge ${threat.badge === 'Critical Risk' ? 'badge-very-high-risk' : 'badge-high-risk'}`}>
                    {threat.badge}
                  </span>
                  <span className="threat-risk-score">{threat.risk}</span>
                </div>
                <h3 className="threat-title">{threat.type}</h3>
                <p className="threat-desc">{threat.desc}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* ── CTA Banner ──────────────────────────────────────────────────────── */}
      <section className="cta-section section">
        <div className="container">
          <div className="cta-card glass">
            <div className="cta-content">
              <h2 className="cta-title">
                Received a Suspicious Job Offer?
              </h2>
              <p className="cta-subtitle">
                Paste the message or upload a screenshot to get an instant AI risk score, live web verification, and evidence report.
              </p>
              <div className="cta-actions">
                <Link to="/analyze" className="btn btn-primary btn-lg">
                  <Shield size={20} />
                  Analyze Suspicious Offer
                  <ArrowRight size={18} />
                </Link>
                <Link to="/report" className="btn btn-secondary btn-lg">
                  Report a Scam
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
