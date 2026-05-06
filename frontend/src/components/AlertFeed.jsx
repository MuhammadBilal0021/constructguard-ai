export default function AlertFeed({ alerts }) {
  if (!alerts || alerts.length === 0) {
    return <div className="empty-state">No alerts generated</div>
  }

  return (
    <div className="alert-feed">
      {alerts.map((alert, i) => (
        <div key={alert.alert_id || i} className={`alert-item ${alert.severity || 'medium'}`}>
          <div>{alert.message}</div>
          <div className="alert-action">→ {alert.recommended_action}</div>
          <div className="alert-time">{alert.alert_id} • {new Date(alert.timestamp).toLocaleTimeString()}</div>
        </div>
      ))}
    </div>
  )
}
