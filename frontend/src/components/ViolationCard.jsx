import RiskBadge from './RiskBadge'

export default function ViolationCard({ violation }) {
  const { violation_type, severity, location, reasoning, confidence } = violation

  const displayType = (violation_type || 'unknown').replace(/_/g, ' ')

  return (
    <div className={`violation-card ${severity}`}>
      <div className="violation-header">
        <span className="violation-type">{displayType}</span>
        <RiskBadge severity={severity} />
      </div>
      <div className="violation-location">
        📍 {location || 'Unknown location'}
        {confidence > 0 && (
          <span style={{ marginLeft: '8px', opacity: 0.7 }}>
            ({(confidence * 100).toFixed(0)}% confidence)
          </span>
        )}
      </div>
      <div className="violation-reasoning">"{reasoning}"</div>
    </div>
  )
}
