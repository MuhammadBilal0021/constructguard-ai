import { useState, useEffect } from 'react'
import { getHistory } from '../api/client'

export default function SiteMemory({ siteId }) {
  const [history, setHistory] = useState(null)
  const [loading, setLoading] = useState(false)

  useEffect(() => {
    if (!siteId) return
    setLoading(true)
    getHistory(siteId, 10)
      .then(data => setHistory(data))
      .catch(() => setHistory(null))
      .finally(() => setLoading(false))
  }, [siteId])

  if (loading) {
    return (
      <div className="empty-state">
        <div className="spinner" style={{ width: 20, height: 20, margin: '0 auto' }}></div>
        <p style={{ marginTop: '0.5rem' }}>Loading history...</p>
      </div>
    )
  }

  if (!history || history.total_analyses === 0) {
    return <div className="empty-state">No previous analyses for this site</div>
  }

  return (
    <div className="site-memory">
      <div style={{ fontSize: '0.8rem', color: 'var(--text-muted)', marginBottom: '0.75rem' }}>
        {history.total_analyses} total analysis session{history.total_analyses !== 1 ? 's' : ''} recorded
      </div>
      <div className="alert-feed" style={{ maxHeight: '300px' }}>
        {history.records.map((record, i) => {
          const date = new Date(record.timestamp)
          const timeStr = date.toLocaleString()
          const level = record.escalation_level || 'normal'

          return (
            <div
              key={record.id || i}
              className={`alert-item ${level === 'emergency' ? 'critical' : level === 'high' ? 'high' : level === 'elevated' ? 'medium' : 'low'}`}
            >
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                <span style={{ fontWeight: 600 }}>
                  {record.total_violations} violation{record.total_violations !== 1 ? 's' : ''}
                </span>
                <span className={`risk-badge ${record.risk_score >= 70 ? 'critical' : record.risk_score >= 40 ? 'high' : 'low'}`}>
                  {record.risk_score}/100
                </span>
              </div>
              <div className="alert-time">
                {timeStr} &bull; Escalation: {level}
              </div>
            </div>
          )
        })}
      </div>
    </div>
  )
}
