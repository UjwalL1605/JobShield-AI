import './HighlightedText.css'

const severityColors = {
  high: { bg: 'rgba(239, 68, 68, 0.15)', border: 'rgba(239, 68, 68, 0.3)', color: '#fca5a5' },
  medium: { bg: 'rgba(245, 158, 11, 0.15)', border: 'rgba(245, 158, 11, 0.3)', color: '#fcd34d' },
  low: { bg: 'rgba(34, 211, 238, 0.15)', border: 'rgba(34, 211, 238, 0.3)', color: '#67e8f9' },
}

function HighlightedText({ text, keywords = [] }) {
  if (!text) return null
  if (!keywords || keywords.length === 0) {
    return (
      <div className="highlighted-text glass animate-fade-in-up" style={{ animationDelay: '0.25s' }}>
        <h3 className="highlighted-text-title">📝 Original Text</h3>
        <pre className="highlighted-pre">{text}</pre>
      </div>
    )
  }

  // Sort keywords by start position descending (for safe replacement)
  const sorted = [...keywords].sort((a, b) => a.start - b.start)

  // Build segments
  const segments = []
  let lastEnd = 0

  for (const kw of sorted) {
    if (kw.start > lastEnd) {
      segments.push({
        text: text.slice(lastEnd, kw.start),
        highlighted: false,
      })
    }
    segments.push({
      text: text.slice(kw.start, kw.end),
      highlighted: true,
      severity: kw.severity,
      category: kw.category,
    })
    lastEnd = Math.max(lastEnd, kw.end)
  }

  if (lastEnd < text.length) {
    segments.push({
      text: text.slice(lastEnd),
      highlighted: false,
    })
  }

  return (
    <div className="highlighted-text glass animate-fade-in-up" style={{ animationDelay: '0.25s' }}>
      <h3 className="highlighted-text-title">
        🔍 Highlighted Suspicious Content
      </h3>
      <div className="highlighted-legend">
        <span className="legend-item">
          <span className="legend-dot" style={{ background: '#ef4444' }}></span>
          High Risk
        </span>
        <span className="legend-item">
          <span className="legend-dot" style={{ background: '#f59e0b' }}></span>
          Medium Risk
        </span>
        <span className="legend-item">
          <span className="legend-dot" style={{ background: '#22d3ee' }}></span>
          Low Risk
        </span>
      </div>
      <pre className="highlighted-pre">
        {segments.map((seg, idx) => {
          if (!seg.highlighted) {
            return <span key={idx}>{seg.text}</span>
          }
          const colors = severityColors[seg.severity] || severityColors.medium
          return (
            <mark
              key={idx}
              className="highlight-mark"
              style={{
                backgroundColor: colors.bg,
                borderBottom: `2px solid ${colors.border}`,
                color: colors.color,
              }}
              title={`${seg.severity} risk — ${seg.category?.replace(/_/g, ' ')}`}
            >
              {seg.text}
            </mark>
          )
        })}
      </pre>
    </div>
  )
}

export default HighlightedText
