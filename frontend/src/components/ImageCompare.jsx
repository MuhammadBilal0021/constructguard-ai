import { useState } from 'react'

export default function ImageCompare({ originalSrc, annotatedSrc }) {
  const [showAnnotated, setShowAnnotated] = useState(true)

  if (!originalSrc && !annotatedSrc) {
    return <div className="empty-state">No image to display</div>
  }

  return (
    <div className="image-compare">
      <div className="image-compare-toggle">
        <button
          className={`compare-btn ${!showAnnotated ? 'active' : ''}`}
          onClick={() => setShowAnnotated(false)}
        >
          Original
        </button>
        <button
          className={`compare-btn ${showAnnotated ? 'active' : ''}`}
          onClick={() => setShowAnnotated(true)}
        >
          AI Analysis
        </button>
      </div>
      <div className="annotated-image-container">
        <img
          src={showAnnotated && annotatedSrc ? annotatedSrc : originalSrc}
          alt={showAnnotated ? 'AI-annotated construction site' : 'Original construction site'}
          className="annotated-image"
          style={{ animation: 'fadeIn 0.3s ease' }}
          onError={(e) => {
            if (originalSrc && e.target.src !== originalSrc) {
              e.target.src = originalSrc
            }
          }}
        />
      </div>
    </div>
  )
}
