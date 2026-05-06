export default function RiskBadge({ severity }) {
  const level = (severity || 'low').toLowerCase()
  return <span className={`risk-badge ${level}`}>{level}</span>
}
