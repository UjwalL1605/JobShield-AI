import { ChevronDown, ChevronUp, AlertCircle } from 'lucide-react'
import { useState } from 'react'
import './RiskFactorTable.css'

const severityOrder = { high: 0, medium: 1, low: 2 }

const categoryLabels = {
  fee_request: '💰 Fee / Payment Request',
  urgency_language: '⏰ Urgency Tactics',
  guaranteed_outcomes: '🎯 Unrealistic Guarantees',
  payment_methods: '💳 Direct Payment Methods',
  suspicious_communication: '📱 Suspicious Communication',
  unrealistic_claims: '🌈 Unrealistic Claims',
  emotional_manipulation: '🎭 Emotional Manipulation',
  impersonation_signals: '🎭 Company Impersonation',
  referral_scheme: '🔗 Referral / MLM Scheme',
  unofficial_email: '📧 Unofficial Email',
  free_email: '📧 Free Email Provider',
  suspicious_url: '🔗 Suspicious URL',
  insecure_url: '🔓 Insecure URL',
  unrealistic_salary: '💵 Unrealistic Salary',
}

function RiskFactorTable({ riskFactors, emailAnalysis, salaryAnalysis }) {
  const [expandedIdx, setExpandedIdx] = useState(null)

  // Combine all risk factors
  const allFactors = [...(riskFactors || [])]

  // Add email-specific factors
  if (emailAnalysis?.analyses) {
    emailAnalysis.analyses.forEach((ea) => {
      if (ea.risk_level !== 'low') {
        ea.reasons.forEach((reason) => {
          allFactors.push({
            category: ea.risk_level === 'high' ? 'unofficial_email' : 'free_email',
            severity: ea.risk_level,
            description: reason,
            matched_keywords: [ea.email],
            count: 1,
          })
        })
      }
    })
  }

  // Add salary-specific factors
  if (salaryAnalysis?.risk_level && salaryAnalysis.risk_level !== 'low' && salaryAnalysis.risk_level !== 'unknown') {
    salaryAnalysis.reasons?.forEach((reason) => {
      allFactors.push({
        category: 'unrealistic_salary',
        severity: salaryAnalysis.risk_level,
        description: reason,
        matched_keywords: [],
        count: 1,
      })
    })
  }

  // Sort by severity
  const sorted = allFactors.sort(
    (a, b) => (severityOrder[a.severity] ?? 2) - (severityOrder[b.severity] ?? 2)
  )

  if (sorted.length === 0) {
    return (
      <div className="risk-table-empty glass-subtle">
        <AlertCircle size={24} className="text-muted" />
        <p>No significant risk factors detected.</p>
      </div>
    )
  }

  return (
    <div className="risk-table glass animate-fade-in-up" style={{ animationDelay: '0.15s' }}>
      <h3 className="risk-table-title">
        <AlertCircle size={20} />
        Risk Factor Analysis
        <span className="risk-table-count">{sorted.length} factor{sorted.length !== 1 ? 's' : ''}</span>
      </h3>

      <div className="risk-table-list">
        {sorted.map((factor, idx) => (
          <div
            key={idx}
            className={`risk-row ${expandedIdx === idx ? 'risk-row-expanded' : ''}`}
            onClick={() => setExpandedIdx(expandedIdx === idx ? null : idx)}
          >
            <div className="risk-row-main">
              <span className={`badge badge-severity-${factor.severity}`}>
                {factor.severity}
              </span>
              <span className="risk-row-category">
                {categoryLabels[factor.category] || factor.category}
              </span>
              <span className="risk-row-expand">
                {expandedIdx === idx ? <ChevronUp size={16} /> : <ChevronDown size={16} />}
              </span>
            </div>

            {expandedIdx === idx && (
              <div className="risk-row-detail animate-fade-in">
                <p className="risk-row-desc">{factor.description}</p>
                {(factor.matched_keywords || factor.matches) && (factor.matched_keywords || factor.matches).length > 0 && (
                  <div className="risk-row-keywords">
                    <span className="risk-row-keywords-label">Matched:</span>
                    {(factor.matched_keywords || factor.matches).map((kw, i) => (
                      <code key={i} className="risk-keyword-chip">{kw}</code>
                    ))}
                  </div>
                )}
              </div>
            )}
          </div>
        ))}
      </div>
    </div>
  )
}

export default RiskFactorTable
