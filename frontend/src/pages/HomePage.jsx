import { Link } from 'react-router-dom'
import {
  Shield, Search, Camera, Mail, BadgeDollarSign,
  FileWarning, Brain, Sparkles, ArrowRight, Users,
  AlertTriangle, CheckCircle
} from 'lucide-react'
import './HomePage.css'

function HomePage() {
  const features = [
    {
      icon: <Search size={24} />,
      title: 'Text Analyzer',
      desc: 'Paste any job description, email, or recruitment message for instant scam detection.',
      color: '#818cf8',
    },
    {
      icon: <Camera size={24} />,
      title: 'Screenshot Scanner',
      desc: 'Upload WhatsApp, Telegram, or LinkedIn screenshots — OCR extracts and analyzes text automatically.',
      color: '#22d3ee',
    },
    {
      icon: <Mail size={24} />,
      title: 'Email Verification',
      desc: 'Detects unofficial email domains and corporate impersonation attempts.',
      color: '#f59e0b',
    },
    {
      icon: <BadgeDollarSign size={24} />,
      title: 'Salary Validation',
      desc: 'Flags unrealistically high salary claims for entry-level or no-experience roles.',
      color: '#10b981',
    },
    {
      icon: <Brain size={24} />,
      title: 'Explainable AI',
      desc: 'Not just a score — see exactly why a message is flagged with detailed risk factors.',
      color: '#f97316',
    },
    {
      icon: <FileWarning size={24} />,
      title: 'Scam Database',
      desc: 'Community-powered database of reported scam emails, phones, UPIs, and websites.',
      color: '#ef4444',
    },
  ]

  const stats = [
    { value: '50+', label: 'Scam Patterns', icon: <AlertTriangle size={20} /> },
    { value: 'AI', label: 'ML + NLP Powered', icon: <Brain size={20} /> },
    { value: '6+', label: 'Platform Support', icon: <Users size={20} /> },
    { value: '100%', label: 'Free & Private', icon: <CheckCircle size={20} /> },
  ]

  return (
    <div className="home-page">
      {/* ── Hero ─────────────────────────────────────────────────────────────── */}
      <section className="hero section">
        <div className="container">
          <div className="hero-content animate-fade-in-up">
            <div className="hero-badge">
              <Sparkles size={14} />
              AI-Powered Scam Detection
            </div>

            <h1 className="hero-title">
              Don't Let Fake Jobs<br />
              <span className="text-gradient">Steal Your Future</span>
            </h1>

            <p className="hero-subtitle">
              JobShield AI uses machine learning, NLP, and OCR to analyze job offers,
              emails, and chat screenshots — protecting you from recruitment scams
              before you respond or pay.
            </p>

            <div className="hero-actions">
              <Link to="/analyze" className="btn btn-primary btn-lg">
                <Shield size={20} />
                Analyze a Message
                <ArrowRight size={18} />
              </Link>
              <Link to="/about" className="btn btn-secondary btn-lg">
                How It Works
              </Link>
            </div>
          </div>

          <div className="hero-visual animate-fade-in-up" style={{ animationDelay: '0.2s' }}>
            <div className="hero-shield-container animate-float">
              <div className="hero-shield">
                <Shield size={64} />
              </div>
              <div className="hero-shield-ring"></div>
              <div className="hero-shield-ring hero-shield-ring-2"></div>
            </div>
          </div>
        </div>
      </section>

      {/* ── Stats ────────────────────────────────────────────────────────────── */}
      <section className="stats-section">
        <div className="container">
          <div className="stats-grid stagger">
            {stats.map((stat, idx) => (
              <div key={idx} className="stat-card glass-subtle">
                <div className="stat-icon">{stat.icon}</div>
                <span className="stat-value">{stat.value}</span>
                <span className="stat-label">{stat.label}</span>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* ── Features ─────────────────────────────────────────────────────────── */}
      <section className="features section">
        <div className="container">
          <div className="section-header animate-fade-in-up">
            <h2 className="section-title">
              Comprehensive <span className="text-gradient">Protection</span>
            </h2>
            <p className="section-subtitle">
              Multiple layers of AI-powered analysis to catch every type of recruitment scam
            </p>
          </div>

          <div className="features-grid stagger">
            {features.map((feat, idx) => (
              <div key={idx} className="feature-card glass-subtle">
                <div className="feature-icon" style={{ color: feat.color, backgroundColor: `${feat.color}15` }}>
                  {feat.icon}
                </div>
                <h3 className="feature-title">{feat.title}</h3>
                <p className="feature-desc">{feat.desc}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* ── CTA ──────────────────────────────────────────────────────────────── */}
      <section className="cta section">
        <div className="container">
          <div className="cta-card glass animate-fade-in-up">
            <div className="cta-glow"></div>
            <h2 className="cta-title">
              Received a suspicious job offer?
            </h2>
            <p className="cta-text">
              Don't risk your money or personal information. Let our AI analyze it in seconds.
            </p>
            <Link to="/analyze" className="btn btn-primary btn-lg">
              <Shield size={20} />
              Start Free Analysis
              <ArrowRight size={18} />
            </Link>
          </div>
        </div>
      </section>
    </div>
  )
}

export default HomePage
