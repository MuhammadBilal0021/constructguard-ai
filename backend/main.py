"""
ConstructGuard AI — FastAPI Backend
Main entry point with all API routes.
"""

import os
import sys
import time
from pathlib import Path
from contextlib import asynccontextmanager

from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse
from dotenv import load_dotenv

# Add project root to path so imports work
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

load_dotenv()

from backend.core.orchestrator import Orchestrator
from backend.core.escalation import get_site_history, get_all_sites
from backend.utils.image_processor import save_upload, validate_image, UPLOAD_DIR
from backend.utils.video_processor import validate_video, extract_frames, stitch_annotated_video, get_video_info
from backend.models.schemas import AnalysisResponse, HistoryResponse, HealthResponse

# ─── Lifespan ─────────────────────────────────────────────

orchestrator: Orchestrator = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    global orchestrator
    print("\n[*] ConstructGuard AI v3.0 -- Starting up...")
    orchestrator = Orchestrator()
    print("[OK] Server ready!\n")
    yield
    print("\n[*] Shutting down ConstructGuard AI\n")


# ─── App ──────────────────────────────────────────────────

app = FastAPI(
    title="ConstructGuard AI",
    description="Autonomous Construction Site Safety Monitor — AMD MI300X + Qwen3.6-27B",
    version="3.0.0",
    lifespan=lifespan,
)

# CORS — allow frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://localhost:3000",
        os.getenv("FRONTEND_URL", "http://localhost:5173"),
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Serve static files (annotated images, reports)
OUTPUT_DIR = Path(__file__).parent / "output"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
REPORTS_DIR = OUTPUT_DIR / "reports"
REPORTS_DIR.mkdir(parents=True, exist_ok=True)

app.mount("/static/output", StaticFiles(directory=str(OUTPUT_DIR)), name="output")
app.mount("/static/uploads", StaticFiles(directory=str(UPLOAD_DIR)), name="uploads")


# ─── Routes ──────────────────────────────────────────────

@app.get("/", tags=["Health"])
async def root():
    return {"message": "ConstructGuard AI v3.0 — Autonomous Safety Monitor", "status": "running"}


@app.get("/health", response_model=HealthResponse, tags=["Health"])
async def health_check():
    inference_mode = os.getenv("INFERENCE_MODE", "mock")
    gpu_available = False
    try:
        import torch
        gpu_available = torch.cuda.is_available()
    except ImportError:
        pass

    return HealthResponse(
        status="healthy",
        inference_mode=inference_mode,
        gpu_available=gpu_available,
        model_loaded=orchestrator is not None,
        version="3.0.0",
    )


@app.post("/analyze", tags=["Analysis"])
async def analyze_image(
    file: UploadFile = File(...),
    site_id: str = Form(default="site_001"),
):
    """
    Upload a construction site image for safety analysis.
    Returns violations, alerts, annotated image, and PDF report.
    """
    # Validate file
    if not file.filename:
        raise HTTPException(status_code=400, detail="No file provided")
    if not validate_image(file.filename):
        raise HTTPException(status_code=400, detail="Unsupported image format. Use JPG, PNG, or WebP.")

    # Save uploaded file
    file_bytes = await file.read()
    if len(file_bytes) == 0:
        raise HTTPException(status_code=400, detail="Empty file")

    image_path = save_upload(file_bytes, file.filename)

    # Run the full analysis pipeline
    try:
        result = orchestrator.analyze(image_path, site_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")

    # Convert file paths to URLs
    annotated_url = None
    if result.get("annotated_image_path") and os.path.exists(result["annotated_image_path"]):
        rel_path = os.path.relpath(result["annotated_image_path"], str(OUTPUT_DIR))
        annotated_url = f"/static/output/{rel_path.replace(os.sep, '/')}"

    report_url = None
    if result.get("report_path") and os.path.exists(result["report_path"]):
        rel_path = os.path.relpath(result["report_path"], str(OUTPUT_DIR))
        report_url = f"/static/output/{rel_path.replace(os.sep, '/')}"

    return {
        "site_id": result["site_id"],
        "total_workers_detected": result["total_workers_detected"],
        "total_violations": result["total_violations"],
        "violations": result["violations"],
        "alerts": result["alerts"],
        "escalation_level": result["escalation_level"],
        "escalation_message": result["escalation_message"],
        "risk_score": result["risk_score"],
        "annotated_image_url": annotated_url,
        "report_url": report_url,
        "processing_time_ms": result["processing_time_ms"],
    }


@app.get("/history/{site_id}", tags=["History"])
async def get_history(site_id: str, limit: int = 20):
    """Get violation history for a specific site."""
    records = get_site_history(site_id, limit)
    return {
        "site_id": site_id,
        "total_analyses": len(records),
        "records": records,
    }


@app.post("/analyze-video", tags=["Analysis"])
async def analyze_video(
    file: UploadFile = File(...),
    site_id: str = Form(default="site_001"),
    frame_interval: float = Form(default=2.0),
):
    """
    Upload a construction site video for safety analysis.
    Extracts frames, analyzes each, draws bounding boxes,
    and stitches results into an annotated video.
    """
    if not file.filename:
        raise HTTPException(status_code=400, detail="No file provided")
    if not validate_video(file.filename):
        raise HTTPException(status_code=400, detail="Unsupported video format. Use MP4, AVI, MOV, MKV, or WebM.")

    # Save uploaded video
    file_bytes = await file.read()
    if len(file_bytes) == 0:
        raise HTTPException(status_code=400, detail="Empty file")

    video_ext = Path(file.filename).suffix.lower()
    video_name = f"{__import__('uuid').uuid4().hex}{video_ext}"
    video_path = str(UPLOAD_DIR / video_name)
    with open(video_path, "wb") as f:
        f.write(file_bytes)

    # Get video info
    info = get_video_info(video_path)

    # Extract frames
    try:
        frames = extract_frames(video_path, interval_seconds=frame_interval)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Frame extraction failed: {str(e)}")

    if not frames:
        raise HTTPException(status_code=400, detail="No frames could be extracted from the video")

    # Analyze each frame through the pipeline
    frame_results = []
    annotated_paths = []
    all_violations = []

    for i, frame_info in enumerate(frames):
        print(f"[Video] Analyzing frame {i+1}/{len(frames)} (t={frame_info['timestamp']}s)...")
        try:
            result = orchestrator.analyze(frame_info["frame_path"], site_id)
            frame_results.append({
                "frame_number": frame_info["frame_number"],
                "timestamp": frame_info["timestamp"],
                "violations_count": result["total_violations"],
                "risk_score": result["risk_score"],
                "escalation_level": result["escalation_level"],
            })

            # Collect annotated frame path
            if result.get("annotated_image_path") and os.path.exists(result["annotated_image_path"]):
                annotated_paths.append(result["annotated_image_path"])
            else:
                annotated_paths.append(frame_info["frame_path"])

            all_violations.extend(result.get("violations", []))
        except Exception as e:
            print(f"[Video] Frame {i+1} analysis error: {e}")
            annotated_paths.append(frame_info["frame_path"])

    # Stitch annotated frames into output video
    annotated_video_url = None
    try:
        output_fps = 1.0 / frame_interval if frame_interval > 0 else 1.0
        annotated_video_path = stitch_annotated_video(annotated_paths, fps=output_fps)
        rel_path = os.path.relpath(annotated_video_path, str(OUTPUT_DIR))
        annotated_video_url = f"/static/output/{rel_path.replace(os.sep, '/')}"
    except Exception as e:
        print(f"[Video] Stitch error: {e}")

    # Summary stats
    total_violations = len(all_violations)
    max_risk = max((fr["risk_score"] for fr in frame_results), default=0)
    worst_escalation = "normal"
    escalation_priority = {"emergency": 4, "high": 3, "elevated": 2, "normal": 1}
    for fr in frame_results:
        if escalation_priority.get(fr["escalation_level"], 0) > escalation_priority.get(worst_escalation, 0):
            worst_escalation = fr["escalation_level"]

    return {
        "site_id": site_id,
        "video_info": info,
        "frames_analyzed": len(frame_results),
        "frame_results": frame_results,
        "total_violations_across_frames": total_violations,
        "peak_risk_score": max_risk,
        "worst_escalation_level": worst_escalation,
        "annotated_video_url": annotated_video_url,
    }


@app.get("/sites", tags=["History"])
async def list_sites():
    """Get list of all known construction sites."""
    sites = get_all_sites()
    return {"sites": sites}


@app.get("/reports/{filename}", tags=["Reports"])
async def download_report(filename: str):
    """Download a generated PDF report."""
    report_path = REPORTS_DIR / filename
    if not report_path.exists():
        raise HTTPException(status_code=404, detail="Report not found")
    return FileResponse(
        path=str(report_path),
        media_type="application/pdf",
        filename=filename,
    )


# ─── Entry point ─────────────────────────────────────────

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("BACKEND_PORT", 8000))
    uvicorn.run("backend.main:app", host="0.0.0.0", port=port, reload=True)
