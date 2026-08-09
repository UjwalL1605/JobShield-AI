import { Search, ExternalLink, Globe, Building2, Phone, Mail, AlertOctagon, CheckCircle2, ShieldAlert } from 'lucide-react'
import './WebIntelligenceCard.css'

function WebIntelligenceCard({ webIntelligence }) {
  if (!webIntelligence) return null

  const { entities, risk_signals, google_search_queries, impersonation_detected } = webIntelligence
  const hasEntities = entities && (
    entities.companies?.length > 0 ||
    entities.domains?.length > 0 ||
    entities.emails?.length > 0 ||
    entities.phones?.length > 0 ||
    entities.telegram_handles?.length > 0 ||
    entities.upi_ids?.length > 0
  )

  return (
    <div className="web-intel-card glass animate-fade-in-up" style={{ animationDelay: '0.2s' }}>
      <div className="web-intel-header">
        <div className="web-intel-title-group">
          <Globe size={20} className="text-gradient-icon" />
          <h3 className="web-intel-title">Web & Entity Intelligence</h3>
        </div>
        {impersonation_detected ? (
          <span className="badge badge-very-high-risk">
            <ShieldAlert size={13} /> Impersonation Detected
          </span>
        ) : (
          <span className="badge badge-likely-safe">
            <Search size={13} /> Live Verification Active
          </span>
        )}
      </div>

      <p className="web-intel-subtitle">
        Extracted entities cross-referenced with live threat databases and real-time Google verification queries.
      </p>

      {/* ── Risk Signals Banners ────────────────────────────────────────── */}
      {risk_signals && risk_signals.length > 0 && (
        <div className="web-intel-signals">
          {risk_signals.map((sig, idx) => (
            <div key={idx} className={`intel-signal-banner intel-signal-${sig.severity}`}>
              <AlertOctagon size={18} className="intel-signal-icon" />
              <div className="intel-signal-content">
                <strong className="intel-signal-title">{sig.title}</strong>
                <p className="intel-signal-detail">{sig.detail}</p>
              </div>
            </div>
          ))}
        </div>
      )}

      {/* ── Extracted Entities Summary ──────────────────────────────────── */}
      {hasEntities && (
        <div className="web-intel-entities">
          <h4 className="entities-section-title">Detected Entities</h4>
          <div className="entities-grid">
            {entities.companies?.length > 0 && (
              <div className="entity-chip">
                <Building2 size={15} className="entity-icon" />
                <span className="entity-label">Company:</span>
                <span className="entity-value">{entities.companies.join(', ')}</span>
              </div>
            )}
            {entities.emails?.length > 0 && (
              <div className="entity-chip">
                <Mail size={15} className="entity-icon" />
                <span className="entity-label">Email:</span>
                <span className="entity-value">{entities.emails.join(', ')}</span>
              </div>
            )}
            {entities.domains?.length > 0 && (
              <div className="entity-chip">
                <Globe size={15} className="entity-icon" />
                <span className="entity-label">Domain:</span>
                <span className="entity-value">{entities.domains.join(', ')}</span>
              </div>
            )}
            {entities.phones?.length > 0 && (
              <div className="entity-chip">
                <Phone size={15} className="entity-icon" />
                <span className="entity-label">Contact:</span>
                <span className="entity-value">{entities.phones.join(', ')}</span>
              </div>
            )}
            {entities.upi_ids?.length > 0 && (
              <div className="entity-chip">
                <span className="entity-label">UPI ID:</span>
                <span className="entity-value">{entities.upi_ids.join(', ')}</span>
              </div>
            )}
          </div>
        </div>
      )}

      {/* ── 1-Click Google Search & Threat Check ────────────────────────── */}
      {google_search_queries && google_search_queries.length > 0 && (
        <div className="web-intel-queries">
          <h4 className="queries-section-title">
            <Search size={16} /> 1-Click Live Threat Search on Google
          </h4>
          <p className="queries-section-desc">
            Directly cross-reference this offer against public scam complaints, victim reports, and company registries:
          </p>
          <div className="queries-list">
            {google_search_queries.map((q, idx) => (
              <a
                key={idx}
                href={q.url}
                target="_blank"
                rel="noopener noreferrer"
                className="google-query-btn"
              >
                <div className="query-btn-left">
                  <Search size={15} className="query-btn-icon" />
                  <span className="query-btn-label">{q.label}</span>
                </div>
                <ExternalLink size={14} className="query-btn-external" />
              </a>
            ))}
          </div>
        </div>
      )}
    </div>
  )
}

export default WebIntelligenceCard
