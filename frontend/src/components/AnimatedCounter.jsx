import { useState, useEffect } from 'react'

export default function AnimatedCounter({ value, duration = 1000, prefix = '', suffix = '' }) {
  const [display, setDisplay] = useState(0)

  useEffect(() => {
    const end = typeof value === 'number' ? value : parseFloat(value) || 0
    const startTime = Date.now()

    const animate = () => {
      const elapsed = Date.now() - startTime
      const progress = Math.min(elapsed / duration, 1)
      const eased = 1 - Math.pow(1 - progress, 3)
      setDisplay(Math.round(end * eased * 10) / 10)
      if (progress < 1) requestAnimationFrame(animate)
    }
    requestAnimationFrame(animate)
  }, [value, duration])

  const formatted = Number.isInteger(value) ? Math.round(display) : display.toFixed(1)

  return <>{prefix}{formatted}{suffix}</>
}
