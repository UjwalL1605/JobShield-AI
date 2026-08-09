import {
  Shield, Upload, Brain, FileSearch, Mail, DollarSign,
  BarChart3, Eye, ChevronRight, HelpCircle, Sparkles,
  Globe, Cpu, Database, CheckCircle2, AlertTriangle
} from 'lucide-react'
import { Link } from 'react-router-dom'
import './AboutPage.css'

function AboutPage() {
  const pipelineSteps = [
    {
      icon: <Upload size={22} />,
      title: '1. Multi-Modal Input',
      desc: 'Raw text, email, or chat screenshots',
      color: '#818cf8',
    },
    {
      icon: <Eye size={22} />,
      title: '2. EasyOCR Engine',
      desc: 'Image upscaling & text detection',
      color: '#22d3ee',
    },
    {
      icon: <FileSearch size={22} />,
      title: '3. Domain Signals',
      desc: '13 domain feature indicators',
      color: '#10b981',
    },
    {
      icon: <Brain size={22} />,
      title: '4. Hybrid ML (94%)',
      desc: 'TF-IDF + Logistic Regression',
      color: '#f59e0b',
    },
    {
      icon: <Globe size={22} />,
      title: '5. Impersonation Check',
      desc: 'MNC & free email authentication',
      color: '#ec4899',
    },
    {
      icon: <Database size={22} />,
      title: '6. Threat Registry',
      desc: '2,000+ blacklisted contacts',
      color: '#ef4444',
    },
    {
      icon: <Sparkles size={22} />,
      title: '7. Google AI Search',
      desc: 'Live Gemini search grounding',
      color: '#a855f7',
    },
    {
      icon: <BarChart3 size={22} />,
      title: '8. Explainable Verdict',
      desc: 'XAI feature weights & advice',
      color: '#06b6d4',
    },
  ]

  const techStack = [
    {
      category: 'Machine Learning',
      tech: 'Scikit-Learn, FeatureUnion, TF-IDF, Logistic Regression (Balanced)',
      detail: 'Trained on 6,340 deduplicated Indian job scams with 94.19% accuracy and 0.9592 5-fold CV score.',
    },
    {
      category: 'Computer Vision & OCR',
      tech: 'EasyOCR, PyTorch, PIL Image Processing',
      detail: 'Automatic image enhancement (sharpening, contrast) and optical character recognition for chat screenshots.',
    },
    {
      category: 'Real-Time Web Intelligence',
      tech: 'Google GenAI SDK, Gemini 2.5 Flash, Google Search Grounding',
      detail: 'Autonomous real-time search queries to cross-reference Reddit, Glassdoor, Quora, and official corporate registries.',
    },
    {
      category: 'Threat Registry & Backend',
      tech: 'FastAPI, SQLite (WAL mode), Pydantic, Python 3.13',
      detail: 'Ultra-fast sub-millisecond local endpoint processing with pre-seeded 2,016+ threat database.',
    },
  ]

  const faqs = [
    {
      q: 'How does JobShield AI catch scams that have clean grammar?',
      a: 'Pure text models can miss polite scams. JobShield AI inspects brand impersonation (e.g. Amazon HR using @gmail.com or WhatsApp) and uses Google Gemini with live Google Search Grounding to check if the company domain or phone number has been reported by victims.',
    },
    {
      q: 'How accurate is the machine learning model?',
      a: 'Our hybrid pipeline achieves 94.19% test accuracy, 0.9497 F1 score, and 95.92% 5-fold cross-validation on rigorous group-based splits that prevent template leakage.',
    },
    {
      q: 'Is my data private?',
      a: 'Yes. Messages and screenshots analyzed on the platform are processed on-the-fly and never stored on our servers. Only explicitly submitted community reports are added to the threat registry.',
    },
    {
      q: 'Do I need an API key to use JobShield AI?',
      a: 'No! The local ML model, heuristic rule engine, OCR scanner, brand verifier, and 1-click Google search buttons work 100% free with zero configuration. Adding a free Gemini API key simply unlocks real-time Google search grounding.',
    },
    {
      q: 'What should I do if I suspect a job offer is a scam?',
      a: 'Never pay any upfront registration fee, uniform deposit, or training kit charge. Legitimate employers never charge candidates. Report fraudulent numbers to cybercrime.gov.in and add them to our scam registry.',
    },
  ]

  return (
    <div className="about-page">
      <div className="container">
        {/* ── Header ────────────────────────────────────────────────────────── */}
        <div className="about-header animate-fade-in-up">
          <div className="analyze-badge">
            <Shield size={14} />
            System Architecture & Methodology
          </div>
          <h1 className="about-title">
            How <span className="text-gradient">JobShield AI</span> Protects You
          </h1>
          <p className="about-subtitle">
            An 8-stage hybrid defense pipeline combining local machine learning with real-time Google AI search intelligence.
          </p>
        </div>

        {/* ── Pipeline ──────────────────────────────────────────────────────── */}
        <section className="pipeline-section animate-fade-in-up" style={{ animationDelay: '0.1s' }}>
          <div className="pipeline-grid-about">
            {pipelineSteps.map((step, idx) => (
              <div key={idx} className="pipeline-step-card glass">
                <div
                  className="pipeline-step-icon"
                  style={{ background: `${step.color}15`, color: step.color, border: `1px solid ${step.color}35` }}
                >
                  {step.icon}
                </div>
                <h3 className="pipeline-step-title">{step.title}</h3>
                <p className="pipeline-step-desc">{step.desc}</p>
              </div>
            ))}
          </div>
        </section>

        {/* ── Tech Stack ────────────────────────────────────────────────────── */}
        <section className="tech-section section">
          <div className="section-header text-center">
            <h2 className="section-title">
              Core <span className="text-gradient">Technology Stack</span>
            </h2>
            <p className="section-subtitle">
              Built with state-of-the-art machine learning, computer vision, and cloud intelligence libraries.
            </p>
          </div>

          <div className="tech-grid">
            {techStack.map((item, idx) => (
              <div key={idx} className="tech-card glass">
                <span className="tech-category text-gradient">{item.category}</span>
                <h3 className="tech-name">{item.tech}</h3>
                <p className="tech-detail">{item.detail}</p>
              </div>
            ))}
          </div>
        </section>

        {/* ── FAQs ──────────────────────────────────────────────────────────── */}
        <section className="faq-section section">
          <div className="section-header text-center">
            <h2 className="section-title">
              Frequently Asked <span className="text-gradient">Questions</span>
            </h2>
            <p className="section-subtitle">
              Common questions about recruitment scams, data privacy, and verification.
            </p>
          </div>

          <div className="faq-grid">
            {faqs.map((faq, idx) => (
              <div key={idx} className="faq-card glass">
                <div className="faq-q-group">
                  <HelpCircle size={18} className="faq-icon" />
                  <h3 className="faq-q">{faq.q}</h3>
                </div>
                <p className="faq-a">{faq.a}</p>
              </div>
            ))}
          </div>
        </section>

        {/* ── CTA ───────────────────────────────────────────────────────────── */}
        <section className="cta-section section">
          <div className="cta-card glass">
            <div className="cta-content text-center">
              <h2 className="cta-title">Ready to Test a Job Offer?</h2>
              <p className="cta-subtitle">
                Paste any message or upload a screenshot to get an instant multi-layer risk assessment.
              </p>
              <div className="cta-actions">
                <Link to="/analyze" className="btn btn-primary btn-lg">
                  <Shield size={20} />
                  Launch Detection Studio
                </Link>
              </div>
            </div>
          </div>
        </section>
      </div>
    </div>
  )
}

export default AboutPage
