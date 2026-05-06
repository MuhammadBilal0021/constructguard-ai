import { useRef, useState } from 'react'

const IMAGE_TYPES = ['image/jpeg', 'image/png', 'image/webp', 'image/bmp']
const VIDEO_TYPES = ['video/mp4', 'video/avi', 'video/quicktime', 'video/x-matroska', 'video/webm']

export function isVideoFile(file) {
  if (!file) return false
  return VIDEO_TYPES.includes(file.type) || /\.(mp4|avi|mov|mkv|webm)$/i.test(file.name)
}

export default function ImageUpload({ onFileSelect, preview, videoPreview }) {
  const fileInput = useRef(null)
  const [dragging, setDragging] = useState(false)

  const handleDrop = (e) => {
    e.preventDefault()
    setDragging(false)
    const file = e.dataTransfer.files[0]
    if (file && (file.type.startsWith('image/') || file.type.startsWith('video/') || /\.(mp4|avi|mov|mkv|webm)$/i.test(file.name))) {
      onFileSelect(file)
    }
  }

  const handleDragOver = (e) => {
    e.preventDefault()
    setDragging(true)
  }

  const handleDragLeave = () => setDragging(false)

  const handleClick = () => fileInput.current?.click()

  const handleChange = (e) => {
    const file = e.target.files[0]
    if (file) onFileSelect(file)
  }

  return (
    <>
      <div
        className={`upload-area ${dragging ? 'dragging' : ''}`}
        onClick={handleClick}
        onDrop={handleDrop}
        onDragOver={handleDragOver}
        onDragLeave={handleDragLeave}
      >
        <input
          ref={fileInput}
          type="file"
          accept="image/*,video/mp4,video/avi,video/quicktime,video/webm,.mkv"
          onChange={handleChange}
          style={{ display: 'none' }}
        />
        {preview ? (
          <img src={preview} alt="Selected site" className="upload-preview" />
        ) : videoPreview ? (
          <div style={{ textAlign: 'center' }}>
            <div style={{ fontSize: '3rem', marginBottom: '0.5rem' }}>🎬</div>
            <div className="upload-text">{videoPreview}</div>
            <div className="upload-hint">Video selected — ready to analyze</div>
          </div>
        ) : (
          <>
            <div className="upload-icon">📷</div>
            <div className="upload-text">Drop a construction site image or video here</div>
            <div className="upload-hint">Images: JPG, PNG, WebP &nbsp;|&nbsp; Videos: MP4, AVI, MOV, WebM</div>
          </>
        )}
      </div>
    </>
  )
}
