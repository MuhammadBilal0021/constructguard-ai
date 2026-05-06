export default function EscalationBanner({ level, message }) {
  if (!level || level === 'normal') return null

  const icons = {
    emergency: '🚨',
    high: '⚠️',
    elevated: '📋',
  }

  return (
    <div className={`escalation-banner ${level}`}>
      <span className="escalation-icon">{icons[level] || '⚠️'}</span>
      <span className="escalation-text">{message}</span>
    </div>
  )
}
