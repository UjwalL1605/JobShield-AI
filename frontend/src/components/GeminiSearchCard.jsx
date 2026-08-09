import { Sparkles, ExternalLink, ShieldCheck, ShieldAlert, AlertTriangle, Building, CheckCircle, Info } from 'lucide-react'
import './GeminiSearchCard.css'

function GeminiSearchCard({ geminiAnalysis }) {
  if (!geminiAnalysis || !geminiAnalysis.available) return null

  const {
    is_scam,
    scam_score,
    trust_level,
    verdict_summary,
    company_reputation,
    scam_indicators_found,
    recommended_action,
    web_sources,
    model_used,
  } = geminiAnalysis

  const score = typeof scam_score === 'number' ? scam_score : 50
  const isHighRisk = score >= 60
  const isSafe = score < 30

  return (
    <div className="gemini-card glass animate-fade-in-up">
      <div className="gemini-card-header">
        <div className="gemini-badge-group">
          <div className="gemini-sparkle-icon">
            <Sparkles size={18} />
          </div>
          <div>
            <h3 className="gemini-title">Google AI Deep Search Analysis</h3>
            <span className="gemini-model-tag">{model_used || 'Gemini 2.5 Flash + Search Grounding'}</span>
          </div>
        </div>

        <div className="gemini-verdict-badge">
          {isHighRisk ? (
            <span className="badge badge-very-high-risk">
              <ShieldAlert size={14} /> {trust_level || 'Scam Detected'} ({Math.round(score)}%)
            </span>
          ) : isSafe ? (
            <span className="badge badge-safe">
              <ShieldCheck size={14} /> {trust_level || 'Likely Legitimate'} ({Math.round(score)}%)
            </span>
          ) : (
            <span className="badge badge-suspicious">
              <AlertTriangle size={14} /> {trust_level || 'Suspicious'} ({Math.round(score)}%)
            </span>
          )}
        </div>
      </div>

      {/* ── Verdict Summary ────────────────────────────────────────────── */}
      {verdict_summary && (
        <div className="gemini-summary-box">
          <p className="gemini-summary-text">{verdict_summary}</p>
        </div>
      )}

      {/* ── Company Legitimacy & Web Footprint ─────────────────────────── */}
      {company_reputation && (
        <div className="gemini-section">
          <h4 className="gemini-section-heading">
            <Building size={15} /> Company Web Reputation
          </h4>
          <p className="gemini-section-content">{company_reputation}</p>
        </div>
      )}

      {/* ── Itemized Evidence ─────────────────────────────────────────── */}
      {scam_indicators_found && scam_indicators_found.length > 0 && (
        <div className="gemini-section">
          <h4 className="gemini-section-heading">
            <Info size={15} /> Key Evidence Identified via Web Search
          </h4>
          <ul className="gemini-evidence-list">
            {scam_indicators_found.map((item, idx) => (
              <li key={idx} className="gemini-evidence-item">
                <span className="evidence-bullet">•</span>
                <span>{item}</span>
              </li>
            ))}
          </ul>
        </div>
      )}

      {/* ── Recommended Safety Action ─────────────────────────────────── */}
      {recommended_action && (
        <div className="gemini-action-box">
          <strong>💡 Recommended Action:</strong> {recommended_action}
        </div>
      )}

      {/* ── Grounded Web Sources ──────────────────────────────────────── */}
      {web_sources && web_sources.length > 0 && (
        <div className="gemini-sources-section">
          <h4 className="gemini-sources-heading">Live Google Search Sources Consulted:</h4>
          <div className="gemini-sources-grid">
            {web_sources.map((source, idx) => (
              <a
                key={idx}
                href={source.url}
                target="_blank"
                rel="noopener noreferrer"
                className="gemini-source-chip"
              >
                <span className="source-title">{source.title || 'Web Reference'}</span>
                <ExternalLink size={12} className="source-icon" />
              </a>
            ))}
          </div>
        </div>
      )}
    </div>
  )
}

export default GeminiSearchCard
