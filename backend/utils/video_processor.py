"""
ConstructGuard AI — Video Processor
Extracts frames from uploaded videos, runs each frame through the
analysis pipeline, and stitches annotated frames back into a video.
"""

import cv2
import os
import uuid
import time
from pathlib import Path

# Directories
OUTPUT_DIR = Path(__file__).parent.parent / "output"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# Supported video formats
SUPPORTED_VIDEO_FORMATS = {".mp4", ".avi", ".mov", ".mkv", ".webm"}

# Default frame extraction interval (seconds between frames)
DEFAULT_FRAME_INTERVAL = 2


def validate_video(filename: str) -> bool:
    """Check if file extension is a supported video format."""
    ext = Path(filename).suffix.lower()
    return ext in SUPPORTED_VIDEO_FORMATS


def extract_frames(video_path: str, interval_seconds: float = DEFAULT_FRAME_INTERVAL) -> list[dict]:
    """
    Extract frames from a video at a given interval.

    Args:
        video_path: Path to the video file
        interval_seconds: Seconds between extracted frames

    Returns:
        List of dicts with 'frame_path', 'timestamp', 'frame_number'
    """
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        raise ValueError(f"Cannot open video: {video_path}")

    fps = cap.get(cv2.CAP_PROP_FPS)
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    duration = total_frames / fps if fps > 0 else 0

    # Calculate frame skip interval
    frame_interval = max(1, int(fps * interval_seconds))

    frames_dir = OUTPUT_DIR / f"frames_{uuid.uuid4().hex[:8]}"
    frames_dir.mkdir(parents=True, exist_ok=True)

    extracted = []
    frame_num = 0

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        if frame_num % frame_interval == 0:
            timestamp = frame_num / fps if fps > 0 else 0
            frame_filename = f"frame_{frame_num:06d}.jpg"
            frame_path = str(frames_dir / frame_filename)
            cv2.imwrite(frame_path, frame)

            extracted.append({
                "frame_path": frame_path,
                "timestamp": round(timestamp, 2),
                "frame_number": frame_num,
            })

        frame_num += 1

    cap.release()

    print(f"[VideoProcessor] Extracted {len(extracted)} frames from {duration:.1f}s video ({total_frames} total frames at {fps:.0f} FPS)")
    return extracted


def stitch_annotated_video(
    annotated_frame_paths: list[str],
    output_path: str = None,
    fps: float = 2.0,
) -> str:
    """
    Stitch annotated frames back into a video file.

    Args:
        annotated_frame_paths: Ordered list of annotated frame image paths
        output_path: Output video path. Auto-generated if None.
        fps: Frames per second for output video

    Returns:
        Path to the output video file
    """
    if not annotated_frame_paths:
        raise ValueError("No frames to stitch")

    # Read first frame to get dimensions
    first_frame = cv2.imread(annotated_frame_paths[0])
    if first_frame is None:
        raise ValueError(f"Cannot read frame: {annotated_frame_paths[0]}")

    h, w = first_frame.shape[:2]

    if output_path is None:
        output_path = str(OUTPUT_DIR / f"annotated_video_{uuid.uuid4().hex[:8]}.mp4")

    fourcc = cv2.VideoWriter_fourcc(*"mp4v")
    writer = cv2.VideoWriter(output_path, fourcc, fps, (w, h))

    for fpath in annotated_frame_paths:
        frame = cv2.imread(fpath)
        if frame is not None:
            # Resize if dimensions don't match
            if frame.shape[:2] != (h, w):
                frame = cv2.resize(frame, (w, h))
            writer.write(frame)

    writer.release()
    print(f"[VideoProcessor] Stitched {len(annotated_frame_paths)} frames into video: {output_path}")
    return output_path


def get_video_info(video_path: str) -> dict:
    """Get basic video metadata."""
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        return {"error": "Cannot open video"}

    fps = cap.get(cv2.CAP_PROP_FPS)
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    duration = total_frames / fps if fps > 0 else 0

    cap.release()

    return {
        "fps": round(fps, 1),
        "total_frames": total_frames,
        "width": width,
        "height": height,
        "duration_seconds": round(duration, 1),
    }
