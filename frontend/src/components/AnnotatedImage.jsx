export default function AnnotatedImage({ annotatedUrl, originalPreview }) {
  const src = annotatedUrl || originalPreview

  if (!src) {
    return <div className="empty-state">No image to display</div>
  }

  return (
    <div className="annotated-image-container">
      <img
        src={src}
        alt="Annotated construction site with safety violations"
        className="annotated-image"
        onError={(e) => {
          // Fallback to original preview if annotated image fails
          if (originalPreview && e.target.src !== originalPreview) {
            e.target.src = originalPreview
          }
        }}
      />
    </div>
  )
}
