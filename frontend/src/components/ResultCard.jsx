import { useEffect, useState } from 'react'
import { ShieldCheck, ShieldAlert, ShieldX, AlertTriangle } from 'lucide-react'
import './ResultCard.css'

const trustConfig = {
  'Safe': {
    icon: ShieldCheck,
    color: 'var(--safe)',
    bg: 'var(--safe-bg)',
    badgeClass: 'badge-safe',
    gaugeColor: '#10b981',
    zone: 'SAFE ZONE',
  },
  'Likely Safe': {
    icon: ShieldCheck,
    color: 'var(--likely-safe)',
    bg: 'var(--likely-safe-bg)',
    badgeClass: 'badge-likely-safe',
    gaugeColor: '#34d399',
    zone: 'LOW RISK',
  },
  'Suspicious': {
    icon: AlertTriangle,
    color: 'var(--suspicious)',
    bg: 'var(--suspicious-bg)',
    badgeClass: 'badge-suspicious',
    gaugeColor: '#f59e0b',
    zone: 'MODERATE RISK',
  },
  'High Risk': {
    icon: ShieldAlert,
    color: 'var(--high-risk)',
    bg: 'var(--high-risk-bg)',
    badgeClass: 'badge-high-risk',
    gaugeColor: '#f97316',
    zone: 'HIGH THREAT',
  },
  'Very High Risk': {
    icon: ShieldX,
    color: 'var(--very-high-risk)',
    bg: 'var(--very-high-risk-bg)',
    badgeClass: 'badge-very-high-risk',
    gaugeColor: '#ef4444',
    zone: 'CRITICAL SCAM',
  },
}

function ResultCard({ scamProbability, trustLevel }) {
  const [animatedScore, setAnimatedScore] = useState(0)
  const cleanTrustLevel = (trustLevel || '').trim()
  const config = trustConfig[cleanTrustLevel] || trustConfig['Suspicious']
  const Icon = config?.icon || ShieldCheck

  const finalScore = typeof scamProbability === 'number' ? Math.min(100, Math.max(0, scamProbability)) : 0

  useEffect(() => {
    const duration = 1400
    const startTime = Date.now()

    const animate = () => {
      const elapsed = Date.now() - startTime
      const progress = Math.min(elapsed / duration, 1)
      // Ease out cubic
      const eased = 1 - Math.pow(1 - progress, 3)
      const current = Math.round(eased * finalScore * 10) / 10
      setAnimatedScore(current)

      if (progress < 1) {
        requestAnimationFrame(animate)
      }
    }

    requestAnimationFrame(animate)
  }, [finalScore])

  // Needle angle: -90 degrees (0%) to +90 degrees (100%)
  const needleAngle = -90 + (animatedScore / 100) * 180

  // Arc calculations for SVG (Radius = 100, Center = 130, 120)
  // Arc length for semicircle: PI * R = 3.14159 * 90 = 282.74
  const arcRadius = 90
  const arcLength = Math.PI * arcRadius
  const arcOffset = arcLength - (animatedScore / 100) * arcLength

  return (
    <div className="result-card glass animate-fade-in-up">
      <div className="result-card-header">
        <div className="result-header-title-group">
          <h3 className="result-card-title">Scam Risk Speedometer</h3>
          <span className="speedometer-zone-tag" style={{ color: config.gaugeColor }}>
            ● {config.zone}
          </span>
        </div>
        <span className={`badge ${config.badgeClass}`}>
          <Icon size={14} />
          {trustLevel}
        </span>
      </div>

      {/* ── High-Tech Speedometer Gauge ─────────────────────────────────── */}
      <div className="speedometer-container">
        <svg className="speedometer-svg" viewBox="0 0 260 155">
          <defs>
            {/* Multi-zone color gradient arc */}
            <linearGradient id="speedo-gradient" x1="0%" y1="0%" x2="100%" y2="0%">
              <stop offset="0%" stopColor="#10b981" />
              <stop offset="25%" stopColor="#34d399" />
              <stop offset="50%" stopColor="#f59e0b" />
              <stop offset="75%" stopColor="#f97316" />
              <stop offset="100%" stopColor="#ef4444" />
            </linearGradient>

            {/* Needle gradient */}
            <linearGradient id="needle-gradient" x1="0%" y1="0%" x2="0%" y2="100%">
              <stop offset="0%" stopColor={config.gaugeColor} />
              <stop offset="100%" stopColor="#0f172a" />
            </linearGradient>

            <filter id="speedo-glow" x="-20%" y="-20%" width="140%" height="140%">
              <feGaussianBlur stdDeviation="3" result="blur" />
              <feMerge>
                <feMergeNode in="blur" />
                <feMergeNode in="SourceGraphic" />
              </feMerge>
            </filter>
          </defs>

          {/* Background Track Arc (Grey / Dark) */}
          <path
            d="M 40 130 A 90 90 0 0 1 220 130"
            fill="none"
            stroke="var(--surface-active)"
            strokeWidth="14"
            strokeLinecap="round"
          />

          {/* Colored Spectrum Background */}
          <path
            d="M 40 130 A 90 90 0 0 1 220 130"
            fill="none"
            stroke="url(#speedo-gradient)"
            strokeWidth="14"
            strokeLinecap="round"
            opacity="0.25"
          />

          {/* Active Value Progress Arc */}
          <path
            d="M 40 130 A 90 90 0 0 1 220 130"
            fill="none"
            stroke="url(#speedo-gradient)"
            strokeWidth="14"
            strokeLinecap="round"
            strokeDasharray={arcLength}
            strokeDashoffset={arcOffset}
            className="speedometer-progress-arc"
          />

          {/* Scale Ticks & Percentage Markers */}
          {/* 0% */}
          <line x1="40" y1="130" x2="30" y2="130" stroke="var(--text-tertiary)" strokeWidth="2" />
          <text x="20" y="134" className="speedo-tick-text" fill="var(--text-tertiary)" textAnchor="end">0%</text>

          {/* 25% */}
          <line x1="66" y1="66" x2="59" y2="59" stroke="var(--text-tertiary)" strokeWidth="2" />
          <text x="50" y="54" className="speedo-tick-text" fill="var(--text-tertiary)" textAnchor="end">25%</text>

          {/* 50% */}
          <line x1="130" y1="40" x2="130" y2="30" stroke="var(--text-tertiary)" strokeWidth="2" />
          <text x="130" y="24" className="speedo-tick-text" fill="var(--text-tertiary)" textAnchor="middle">50%</text>

          {/* 75% */}
          <line x1="194" y1="66" x2="201" y2="59" stroke="var(--text-tertiary)" strokeWidth="2" />
          <text x="210" y="54" className="speedo-tick-text" fill="var(--text-tertiary)" textAnchor="start">75%</text>

          {/* 100% */}
          <line x1="220" y1="130" x2="230" y2="130" stroke="var(--text-tertiary)" strokeWidth="2" />
          <text x="240" y="134" className="speedo-tick-text" fill="var(--text-tertiary)" textAnchor="start">100%</text>

          {/* Gauge Center Needle */}
          <g transform={`translate(130, 130) rotate(${needleAngle})`} className="speedometer-needle-group">
            {/* Needle pointer */}
            <polygon
              points="0,-82 4,-10 0,0 -4,-10"
              fill={config.gaugeColor}
              filter="url(#speedo-glow)"
            />
            {/* Center Pivot Hub */}
            <circle cx="0" cy="0" r="9" fill={config.gaugeColor} />
            <circle cx="0" cy="0" r="5" fill="var(--bg-primary)" />
          </g>
        </svg>

        {/* Digital Readout */}
        <div className="speedometer-readout">
          <div className="speedometer-score-row">
            <span className="speedometer-score-val" style={{ color: config.gaugeColor }}>
              {animatedScore}
            </span>
            <span className="speedometer-percent-symbol">%</span>
          </div>
          <span className="speedometer-score-caption">THREAT PROBABILITY</span>
        </div>
      </div>

      {/* Recommendation & Advice Banner */}
      <div className="result-detail" style={{ background: config.bg, borderColor: config.gaugeColor }}>
        <Icon size={20} style={{ color: config.color, flexShrink: 0 }} />
        <p style={{ color: config.color, margin: 0 }}>
          {cleanTrustLevel === 'Safe' && 'This message appears to be legitimate. Normal hiring process.'}
          {cleanTrustLevel === 'Likely Safe' && 'This message looks mostly safe, but exercise standard caution.'}
          {cleanTrustLevel === 'Suspicious' && 'Several suspicious patterns detected. Do not pay any registration fees.'}
          {cleanTrustLevel === 'High Risk' && 'Strong scam indicators detected. Never share OTPs or pay upfront fees.'}
          {cleanTrustLevel === 'Very High Risk' && 'CRITICAL SCAM: Confirmed fraudulent pattern or blacklisted entity. Do NOT send money.'}
        </p>
      </div>
    </div>
  )
}

export default ResultCard
