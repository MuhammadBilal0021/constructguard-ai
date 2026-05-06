import { useState, useEffect } from 'react'

export default function RiskGauge({ score, level }) {
  const [animatedScore, setAnimatedScore] = useState(0)

  useEffect(() => {
    let start = 0
    const end = score || 0
    const duration = 1200
    const startTime = Date.now()

    const animate = () => {
      const elapsed = Date.now() - startTime
      const progress = Math.min(elapsed / duration, 1)
      // Ease out cubic
      const eased = 1 - Math.pow(1 - progress, 3)
      setAnimatedScore(Math.round(start + (end - start) * eased))
      if (progress < 1) requestAnimationFrame(animate)
    }
    requestAnimationFrame(animate)
  }, [score])

  const radius = 80
  const stroke = 10
  const circumference = 2 * Math.PI * radius
  const offset = circumference - (animatedScore / 100) * circumference

  const getColor = () => {
    if (animatedScore >= 70) return 'var(--severity-critical)'
    if (animatedScore >= 40) return 'var(--severity-high)'
    if (animatedScore > 0) return 'var(--severity-medium)'
    return 'var(--severity-low)'
  }

  return (
    <div className="risk-gauge">
      <svg width="200" height="200" viewBox="0 0 200 200" style={{ transform: 'rotate(-90deg)' }}>
        {/* Background circle */}
        <circle
          cx="100" cy="100" r={radius}
          fill="none"
          stroke="var(--bg-surface)"
          strokeWidth={stroke}
        />
        {/* Score arc */}
        <circle
          cx="100" cy="100" r={radius}
          fill="none"
          stroke={getColor()}
          strokeWidth={stroke}
          strokeLinecap="round"
          strokeDasharray={circumference}
          strokeDashoffset={offset}
          style={{ transition: 'stroke-dashoffset 0.1s ease', filter: `drop-shadow(0 0 8px ${getColor()})` }}
        />
      </svg>
      <div style={{
        position: 'absolute',
        top: '50%',
        left: '50%',
        transform: 'translate(-50%, -50%)',
        textAlign: 'center',
      }}>
        <div className="risk-score-value" style={{ color: getColor() }}>{animatedScore}</div>
        <div className="risk-score-label">/ 100 RISK</div>
      </div>
    </div>
  )
}
