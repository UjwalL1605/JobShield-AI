import { useEffect, useState } from 'react'
import { ShieldCheck, ShieldAlert, ShieldX, AlertTriangle, CircleAlert } from 'lucide-react'
import './ResultCard.css'

const trustConfig = {
  'Safe': {
    icon: ShieldCheck,
    color: 'var(--safe)',
    bg: 'var(--safe-bg)',
    badgeClass: 'badge-safe',
    ringColor: '#10b981',
  },
  'Likely Safe': {
    icon: ShieldCheck,
    color: 'var(--likely-safe)',
    bg: 'var(--likely-safe-bg)',
    badgeClass: 'badge-likely-safe',
    ringColor: '#34d399',
  },
  'Suspicious': {
    icon: AlertTriangle,
    color: 'var(--suspicious)',
    bg: 'var(--suspicious-bg)',
    badgeClass: 'badge-suspicious',
    ringColor: '#f59e0b',
  },
  'High Risk': {
    icon: ShieldAlert,
    color: 'var(--high-risk)',
    bg: 'var(--high-risk-bg)',
    badgeClass: 'badge-high-risk',
    ringColor: '#f97316',
  },
  'Very High Risk': {
    icon: ShieldX,
    color: 'var(--very-high-risk)',
    bg: 'var(--very-high-risk-bg)',
    badgeClass: 'badge-very-high-risk',
    ringColor: '#ef4444',
  },
}

function ResultCard({ scamProbability, trustLevel }) {
  const [animatedScore, setAnimatedScore] = useState(0)
  const cleanTrustLevel = (trustLevel || '').trim()
  const config = trustConfig[cleanTrustLevel] || trustConfig['Suspicious']
  const Icon = config?.icon || ShieldCheck

  useEffect(() => {
    let start = 0
    const end = typeof scamProbability === 'number' ? scamProbability : 0
    const duration = 1200
    const startTime = Date.now()

    const animate = () => {
      const elapsed = Date.now() - startTime
      const progress = Math.min(elapsed / duration, 1)
      // Ease-out cubic
      const eased = 1 - Math.pow(1 - progress, 3)
      const current = Math.round(eased * end)
      setAnimatedScore(current)

      if (progress < 1) {
        requestAnimationFrame(animate)
      }
    }

    requestAnimationFrame(animate)
  }, [scamProbability])

  const circumference = 2 * Math.PI * 54
  const strokeDashoffset = circumference - (animatedScore / 100) * circumference

  return (
    <div className="result-card glass animate-fade-in-up">
      <div className="result-card-header">
        <h3 className="result-card-title">Scam Risk Assessment</h3>
        <span className={`badge ${config.badgeClass}`}>
          <Icon size={14} />
          {trustLevel}
        </span>
      </div>

      <div className="result-gauge-container">
        <svg className="result-gauge" viewBox="0 0 120 120">
          {/* Background ring */}
          <circle
            cx="60" cy="60" r="54"
            fill="none"
            stroke="var(--surface)"
            strokeWidth="8"
          />
          {/* Progress ring */}
          <circle
            cx="60" cy="60" r="54"
            fill="none"
            stroke={config.ringColor}
            strokeWidth="8"
            strokeLinecap="round"
            strokeDasharray={circumference}
            strokeDashoffset={strokeDashoffset}
            transform="rotate(-90 60 60)"
            className="result-gauge-progress"
          />
          {/* Glow filter */}
          <defs>
            <filter id="glow">
              <feGaussianBlur stdDeviation="3" result="coloredBlur" />
              <feMerge>
                <feMergeNode in="coloredBlur" />
                <feMergeNode in="SourceGraphic" />
              </feMerge>
            </filter>
          </defs>
        </svg>
        <div className="result-gauge-value">
          <span className="result-score" style={{ color: config.ringColor }}>
            {animatedScore}
          </span>
          <span className="result-percent">%</span>
        </div>
        <p className="result-gauge-label">Scam Probability</p>
      </div>

      <div className="result-detail" style={{ background: config.bg }}>
        <Icon size={18} style={{ color: config.color }} />
        <p style={{ color: config.color }}>
          {trustLevel === 'Safe' && 'This message appears to be a legitimate job posting.'}
          {trustLevel === 'Likely Safe' && 'This message looks mostly safe, but stay cautious.'}
          {trustLevel === 'Suspicious' && 'Several suspicious patterns detected. Verify before proceeding.'}
          {trustLevel === 'High Risk' && 'This message shows strong scam indicators. Do NOT respond or pay.'}
          {trustLevel === 'Very High Risk' && 'This is almost certainly a scam. Do NOT share personal information or make any payment.'}
        </p>
      </div>
    </div>
  )
}

export default ResultCard
