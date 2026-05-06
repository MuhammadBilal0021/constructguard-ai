export default function ReportDownload({ reportUrl }) {
  if (!reportUrl) return null

  return (
    <a
      href={reportUrl}
      target="_blank"
      rel="noopener noreferrer"
      className="btn-download"
      download
    >
      📄 Download PDF Report
    </a>
  )
}
