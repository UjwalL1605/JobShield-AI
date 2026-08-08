import {
  Shield, Upload, Brain, FileSearch, Mail, DollarSign,
  BarChart3, Eye, ChevronRight, HelpCircle
} from 'lucide-react'
import { Link } from 'react-router-dom'
import './AboutPage.css'

function AboutPage() {
  const pipelineSteps = [
    {
      icon: <Upload size={22} />,
      title: 'Input',
      desc: 'Paste text or upload a screenshot',
      color: '#818cf8',
    },
    {
      icon: <Eye size={22} />,
      title: 'OCR Extraction',
      desc: 'EasyOCR converts images to text',
      color: '#22d3ee',
    },
    {
      icon: <FileSearch size={22} />,
      title: 'Text Preprocessing',
      desc: 'Clean, normalize, and tokenize',
      color: '#10b981',
    },
    {
      icon: <Brain size={22} />,
      title: 'ML Classification',
      desc: 'TF-IDF + Logistic Regression',
      color: '#f59e0b',
    },
    {
      icon: <Shield size={22} />,
      title: 'Rule Engine',
      desc: '50+ scam patterns checked',
      color: '#f97316',
    },
    {
      icon: <Mail size={22} />,
      title: 'Email & URL Check',
      desc: 'Domain & impersonation detection',
      color: '#ef4444',
    },
    {
      icon: <DollarSign size={22} />,
      title: 'Salary Validation',
      desc: 'Benchmark comparison',
      color: '#8b5cf6',
    },
    {
      icon: <BarChart3 size={22} />,
      title: 'Risk Report',
      desc: 'Score + explainable factors',
      color: '#06b6d4',
    },
  ]

  const faqs = [
    {
      q: 'How accurate is JobShield AI?',
      a: 'Our ML model combined with rule-based analysis achieves high accuracy on known scam patterns. However, no system is 100% foolproof. Always exercise caution with job offers.',
    },
    {
      q: 'Is my data stored?',
      a: 'No. Text you submit for analysis is processed in real-time and not stored. Only scam reports you explicitly submit are saved to help the community.',
    },
    {
      q: 'What languages are supported?',
      a: 'Currently, English text analysis is fully supported. OCR can extract text from images with mixed English/Hindi content. More languages coming soon.',
    },
    {
      q: 'Is this service free?',
      a: 'Yes, JobShield AI is completely free. Our goal is to protect students and job seekers from scams.',
    },
    {
      q: 'Can I report a scam?',
      a: 'Absolutely! Use the Report Scam page to submit email addresses, phone numbers, websites, or UPI IDs associated with scams. Your reports help protect others.',
    },
    {
      q: 'What should I do if I\'ve been scammed?',
      a: 'Report the incident to the Cyber Crime Portal (cybercrime.gov.in), contact your bank to block transactions, and file a police complaint. Do NOT make further payments.',
    },
  ]

  return (
    <div className="about-page">
      <div className="container">
        {/* ── Header ────────────────────────────────────────────────────────── */}
        <div className="about-header animate-fade-in-up">
          <h1 className="about-title">
            How <span className="text-gradient">JobShield AI</span> Works
          </h1>
          <p className="about-subtitle">
            A multi-layered AI analysis pipeline that catches scams from every angle
          </p>
        </div>

        {/* ── Pipeline ──────────────────────────────────────────────────────── */}
        <section className="pipeline-section animate-fade-in-up" style={{ animationDelay: '0.1s' }}>
          <div className="pipeline-grid stagger">
            {pipelineSteps.map((step, idx) => (
              <div key={idx} className="pipeline-step glass-subtle">
                <div className="pipeline-step-number">{idx + 1}</div>
                <div
                  className="pipeline-step-icon"
                  style={{ color: step.color, backgroundColor: `${step.color}15` }}
                >
                  {step.icon}
                </div>
                <h3 className="pipeline-step-title">{step.title}</h3>
                <p className="pipeline-step-desc">{step.desc}</p>
                {idx < pipelineSteps.length - 1 && (
                  <div className="pipeline-arrow">
                    <ChevronRight size={16} />
                  </div>
                )}
              </div>
            ))}
          </div>
        </section>

        {/* ── Tech Stack ────────────────────────────────────────────────────── */}
        <section className="tech-section section">
          <h2 className="section-title text-center">Technology Stack</h2>
          <div className="tech-grid stagger">
            <div className="tech-card glass-subtle">
              <h4>Frontend</h4>
              <ul>
                <li>React 19 + Vite</li>
                <li>React Router</li>
                <li>Framer Motion</li>
                <li>Lucide Icons</li>
              </ul>
            </div>
            <div className="tech-card glass-subtle">
              <h4>Backend</h4>
              <ul>
                <li>FastAPI (Python)</li>
                <li>Pydantic</li>
                <li>SQLite</li>
                <li>Uvicorn</li>
              </ul>
            </div>
            <div className="tech-card glass-subtle">
              <h4>AI / ML</h4>
              <ul>
                <li>Scikit-learn</li>
                <li>TF-IDF Vectorizer</li>
                <li>Logistic Regression</li>
                <li>Rule-Based NLP</li>
              </ul>
            </div>
            <div className="tech-card glass-subtle">
              <h4>OCR</h4>
              <ul>
                <li>EasyOCR</li>
                <li>Pillow (PIL)</li>
                <li>Image Preprocessing</li>
                <li>Multi-language Support</li>
              </ul>
            </div>
          </div>
        </section>

        {/* ── FAQ ───────────────────────────────────────────────────────────── */}
        <section className="faq-section section">
          <h2 className="section-title text-center">
            <HelpCircle size={28} style={{ display: 'inline', verticalAlign: 'middle' }} />{' '}
            Frequently Asked Questions
          </h2>
          <div className="faq-grid stagger">
            {faqs.map((faq, idx) => (
              <div key={idx} className="faq-card glass-subtle">
                <h4 className="faq-question">{faq.q}</h4>
                <p className="faq-answer">{faq.a}</p>
              </div>
            ))}
          </div>
        </section>

        {/* ── CTA ───────────────────────────────────────────────────────────── */}
        <section className="about-cta">
          <div className="glass" style={{ padding: '40px', textAlign: 'center' }}>
            <h3 style={{ fontSize: '1.5rem', fontWeight: 800, marginBottom: '12px' }}>
              Ready to verify a job offer?
            </h3>
            <p className="text-muted mb-lg">
              Paste the message and get instant AI-powered analysis.
            </p>
            <Link to="/analyze" className="btn btn-primary btn-lg">
              <Shield size={20} />
              Start Analysis
            </Link>
          </div>
        </section>
      </div>
    </div>
  )
}

export default AboutPage
