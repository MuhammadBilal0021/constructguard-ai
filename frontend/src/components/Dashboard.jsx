import { useState } from 'react'
import ImageUpload, { isVideoFile } from './ImageUpload'
import ImageCompare from './ImageCompare'
import ViolationCard from './ViolationCard'
import RiskBadge from './RiskBadge'
import RiskGauge from './RiskGauge'
import AnimatedCounter from './AnimatedCounter'
import AlertFeed from './AlertFeed'
import EscalationBanner from './EscalationBanner'
import ReportDownload from './ReportDownload'
import SiteMemory from './SiteMemory'
import { analyzeImage, analyzeVideo, getStaticUrl } from '../api/client'

export default function Dashboard() {
  const [selectedFile, setSelectedFile] = useState(null)
  const [isVideo, setIsVideo] = useState(false)
  const [preview, setPreview] = useState(null)
  const [videoName, setVideoName] = useState(null)
  const [result, setResult] = useState(null)
  const [videoResult, setVideoResult] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)
  const [step, setStep] = useState(0)
  const [siteId, setSiteId] = useState('site_001')
  const [refreshHistory, setRefreshHistory] = useState(0)

  const handleFileSelect = (file) => {
    setSelectedFile(file)
    setResult(null)
    setVideoResult(null)
    setError(null)
    if (isVideoFile(file)) {
      setIsVideo(true)
      setPreview(null)
      setVideoName(file.name)
    } else {
      setIsVideo(false)
      setPreview(URL.createObjectURL(file))
      setVideoName(null)
    }
  }

  const handleAnalyze = async () => {
    if (!selectedFile) return
    setLoading(true)
    setError(null)
    setStep(1)
    const stepTimer = setInterval(() => {
      setStep(prev => prev < 5 ? prev + 1 : prev)
    }, isVideo ? 2000 : 800)

    try {
      if (isVideo) {
        const data = await analyzeVideo(selectedFile, siteId)
        clearInterval(stepTimer)
        setStep(5)
        setVideoResult(data)
        setResult(null)
      } else {
        const data = await analyzeImage(selectedFile, siteId)
        clearInterval(stepTimer)
        setStep(5)
        setResult(data)
        setVideoResult(null)
      }
      setRefreshHistory(prev => prev + 1)
    } catch (err) {
      clearInterval(stepTimer)
      setError(err.response?.data?.detail || err.message || 'Analysis failed')
    } finally {
      setLoading(false)
    }
  }

  const imageSteps = [
    'Vision Agent — detecting workers & violations',
    'Reasoning Agent — analyzing danger context',
    'Risk Scorer — calculating severity scores',
    'Alert Agent — generating safety alerts',
    'Report Agent — compiling PDF report',
  ]
  const videoSteps = [
    'Extracting frames from video...',
    'Vision Agent — scanning each frame for violations',
    'Reasoning + Risk Scoring across all frames',
    'Drawing bounding boxes on each frame',
    'Stitching annotated video + generating report',
  ]
  const steps = isVideo ? videoSteps : imageSteps

  return (
    <main className="dashboard">
      <div className="dashboard-header">
        <h1>Construction Site Safety Analysis</h1>
        <p>Upload a site photo or video for autonomous AI-powered safety inspection</p>
      </div>

      {/* Upload */}
      <div className="upload-zone">
        <div className="card">
          <ImageUpload onFileSelect={handleFileSelect} preview={preview} videoPreview={videoName} />
          {selectedFile && !loading && (
            <div style={{ textAlign: 'center' }}>
              <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '1rem', marginTop: '1rem' }}>
                <label style={{ fontSize: '0.85rem', color: 'var(--text-secondary)' }}>Site ID:</label>
                <input type="text" value={siteId} onChange={(e) => setSiteId(e.target.value)}
                  style={{ background: 'var(--bg-surface)', border: '1px solid var(--border-default)', borderRadius: 'var(--radius-sm)', padding: '6px 12px', color: 'var(--text-primary)', fontFamily: "'JetBrains Mono', monospace", fontSize: '0.85rem', width: '140px' }}
                />
              </div>
              <button className="btn-analyze" onClick={handleAnalyze}>
                {isVideo ? 'Analyze Video' : 'Analyze Site Safety'}
              </button>
            </div>
          )}
        </div>
      </div>

      {/* Processing */}
      {loading && (
        <div className="processing-overlay">
          <div className="spinner" style={{ width: 40, height: 40, margin: '0 auto', borderWidth: 3 }}></div>
          <h3 style={{ marginTop: '1rem', color: 'var(--cg-primary)' }}>
            {isVideo ? 'Analyzing Video Frames...' : 'Analyzing Construction Site...'}
          </h3>
          <div className="processing-steps">
            {steps.map((s, i) => (
              <div key={i} className={`processing-step ${step > i + 1 ? 'done' : step === i + 1 ? 'active' : ''}`}>
                <div className="step-indicator">{step > i + 1 ? '\u2713' : i + 1}</div>
                {s}
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Error */}
      {error && (
        <div className="escalation-banner emergency" style={{ gridColumn: '1 / -1' }}>
          <span className="escalation-icon">!</span>
          <span className="escalation-text">Error: {error}</span>
        </div>
      )}

      {/* ═══ IMAGE RESULTS ═══ */}
      {result && !loading && (
        <div className="results-section" style={{ display: 'contents' }}>
          {/* Stats */}
          <div className="stats-row">
            <div className="stat-card">
              <div className="stat-value"><AnimatedCounter value={result.total_workers_detected} /></div>
              <div className="stat-label">Workers Detected</div>
            </div>
            <div className="stat-card">
              <div className="stat-value" style={{ color: result.total_violations > 0 ? 'var(--severity-critical)' : 'var(--severity-low)' }}>
                <AnimatedCounter value={result.total_violations} />
              </div>
              <div className="stat-label">Violations Found</div>
            </div>
            <div className="stat-card">
              <div className="stat-value" style={{ color: result.risk_score >= 70 ? 'var(--severity-critical)' : result.risk_score >= 40 ? 'var(--severity-high)' : 'var(--severity-low)' }}>
                <AnimatedCounter value={result.risk_score} />
              </div>
              <div className="stat-label">Risk Score /100</div>
            </div>
            <div className="stat-card">
              <div className="stat-value" style={{ fontSize: '1.2rem', color: 'var(--cg-primary)' }}>
                <AnimatedCounter value={Math.round(result.processing_time_ms)} suffix="ms" />
              </div>
              <div className="stat-label">Processing Time</div>
            </div>
          </div>

          {/* Escalation */}
          {result.escalation_level !== 'normal' && (
            <EscalationBanner level={result.escalation_level} message={result.escalation_message} />
          )}

          {/* Image with Before/After Toggle + Risk Gauge */}
          <div className="card">
            <div className="card-header">
              <span className="card-title">Site Analysis</span>
              <RiskBadge severity={result.escalation_level === 'normal' ? 'low' : result.escalation_level} />
            </div>
            <ImageCompare
              originalSrc={preview}
              annotatedSrc={getStaticUrl(result.annotated_image_url)}
            />
          </div>

          <div className="card">
            <div className="card-header">
              <span className="card-title">Risk Assessment</span>
            </div>
            <RiskGauge score={result.risk_score} level={result.escalation_level} />
            <div className="severity-breakdown">
              {result.violations?.filter(v => v.severity === 'critical').length > 0 && (
                <div className="severity-item">
                  <div className="severity-dot" style={{ background: 'var(--severity-critical)' }}></div>
                  Critical: {result.violations.filter(v => v.severity === 'critical').length}
                </div>
              )}
              {result.violations?.filter(v => v.severity === 'high').length > 0 && (
                <div className="severity-item">
                  <div className="severity-dot" style={{ background: 'var(--severity-high)' }}></div>
                  High: {result.violations.filter(v => v.severity === 'high').length}
                </div>
              )}
              {result.violations?.filter(v => v.severity === 'medium').length > 0 && (
                <div className="severity-item">
                  <div className="severity-dot" style={{ background: 'var(--severity-medium)' }}></div>
                  Medium: {result.violations.filter(v => v.severity === 'medium').length}
                </div>
              )}
            </div>
          </div>

          {/* Violations */}
          <div className="card">
            <div className="card-header">
              <span className="card-title">Violations ({result.total_violations})</span>
              <ReportDownload reportUrl={getStaticUrl(result.report_url)} />
            </div>
            <div className="violations-list">
              {result.violations?.map((v, i) => <ViolationCard key={i} violation={v} />)}
              {result.violations?.length === 0 && (
                <div className="empty-state">No violations detected - site is compliant</div>
              )}
            </div>
          </div>

          {/* Site Memory */}
          <div className="card">
            <div className="card-header">
              <span className="card-title">Site Memory</span>
              <span style={{ fontSize: '0.7rem', color: 'var(--text-muted)', fontFamily: "'JetBrains Mono', monospace" }}>{siteId}</span>
            </div>
            <SiteMemory key={refreshHistory} siteId={siteId} />
          </div>

          {/* Alerts */}
          <div className="card" style={{ gridColumn: '1 / -1' }}>
            <div className="card-header">
              <span className="card-title">Alert Feed</span>
              <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>{result.alerts?.length || 0} alerts</span>
            </div>
            <AlertFeed alerts={result.alerts || []} />
          </div>
        </div>
      )}

      {/* ═══ VIDEO RESULTS ═══ */}
      {videoResult && !loading && (
        <div className="results-section" style={{ display: 'contents' }}>
          <div className="stats-row">
            <div className="stat-card">
              <div className="stat-value"><AnimatedCounter value={videoResult.frames_analyzed} /></div>
              <div className="stat-label">Frames Analyzed</div>
            </div>
            <div className="stat-card">
              <div className="stat-value" style={{ color: 'var(--severity-critical)' }}>
                <AnimatedCounter value={videoResult.total_violations_across_frames} />
              </div>
              <div className="stat-label">Total Violations</div>
            </div>
            <div className="stat-card">
              <div className="stat-value" style={{ color: videoResult.peak_risk_score >= 70 ? 'var(--severity-critical)' : 'var(--severity-low)' }}>
                <AnimatedCounter value={videoResult.peak_risk_score} />
              </div>
              <div className="stat-label">Peak Risk Score</div>
            </div>
            <div className="stat-card">
              <div className="stat-value" style={{ fontSize: '1rem', color: 'var(--cg-primary)' }}>
                <AnimatedCounter value={videoResult.video_info?.duration_seconds || 0} suffix="s" />
              </div>
              <div className="stat-label">Video Duration</div>
            </div>
          </div>

          {videoResult.worst_escalation_level !== 'normal' && (
            <EscalationBanner level={videoResult.worst_escalation_level} message={`Worst escalation across ${videoResult.frames_analyzed} analyzed frames: ${videoResult.worst_escalation_level.toUpperCase()}`} />
          )}

          {videoResult.annotated_video_url && (
            <div className="card" style={{ gridColumn: '1 / -1' }}>
              <div className="card-header">
                <span className="card-title">Annotated Video</span>
                <a href={getStaticUrl(videoResult.annotated_video_url)} download className="btn-download">Download Annotated Video</a>
              </div>
              <video src={getStaticUrl(videoResult.annotated_video_url)} controls style={{ width: '100%', borderRadius: 'var(--radius-md)', maxHeight: '500px' }} />
            </div>
          )}

          <div className="card" style={{ gridColumn: '1 / -1' }}>
            <div className="card-header">
              <span className="card-title">Frame-by-Frame Analysis</span>
              <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>
                {videoResult.video_info?.fps} FPS | {videoResult.video_info?.width}x{videoResult.video_info?.height}
              </span>
            </div>
            <div className="alert-feed">
              {videoResult.frame_results?.map((fr, i) => (
                <div key={i} className={`alert-item ${fr.escalation_level === 'emergency' ? 'critical' : fr.escalation_level === 'high' ? 'high' : fr.violations_count > 0 ? 'medium' : 'low'}`}>
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                    <span><strong>Frame {fr.frame_number}</strong> (t={fr.timestamp}s) - {fr.violations_count} violation{fr.violations_count !== 1 ? 's' : ''}</span>
                    <RiskBadge severity={fr.risk_score >= 70 ? 'critical' : fr.risk_score >= 40 ? 'high' : fr.risk_score > 0 ? 'medium' : 'low'} />
                  </div>
                  <div className="alert-time">Risk: {fr.risk_score}/100 | Escalation: {fr.escalation_level}</div>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}
    </main>
  )
}
