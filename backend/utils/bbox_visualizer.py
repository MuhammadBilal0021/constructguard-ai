"""
ConstructGuard AI — Bounding Box Visualizer
Draws colored bounding boxes on construction site images using OpenCV.

Color coding:
  🔴 Red    = Critical (no helmet near machinery)
  🟠 Orange = High (no harness at height)
  🟡 Yellow = Medium (no vest in traffic zone)
  🟢 Green  = Low / Compliant
"""

import cv2
import numpy as np
from pathlib import Path

# BGR color map (OpenCV uses BGR, not RGB)
SEVERITY_COLORS = {
    "critical": (0, 0, 255),       # Red
    "high":     (0, 128, 255),     # Orange
    "medium":   (0, 220, 255),     # Yellow
    "low":      (0, 200, 0),       # Green
}

# Box line thickness by severity
SEVERITY_THICKNESS = {
    "critical": 4,
    "high":     3,
    "medium":   2,
    "low":      2,
}


def draw_violations_on_image(image_path: str, violations: list, output_path: str = None) -> str:
    """
    Draw colored bounding boxes on the image for each violation.

    Args:
        image_path: Path to the original image
        violations: List of violation dicts with 'bbox', 'severity', 'violation_type'
        output_path: Optional output path. Auto-generated if None.

    Returns:
        Path to the annotated image file.
    """
    img = cv2.imread(image_path)
    if img is None:
        raise FileNotFoundError(f"Cannot read image: {image_path}")

    img_h, img_w = img.shape[:2]

    for v in violations:
        # Extract bounding box
        bbox = v.get("bbox", {})
        if isinstance(bbox, dict):
            x = bbox.get("x", 0)
            y = bbox.get("y", 0)
            w = bbox.get("w", 50)
            h = bbox.get("h", 50)
        elif isinstance(bbox, (list, tuple)) and len(bbox) == 4:
            x, y, w, h = bbox
        else:
            continue

        # Ensure bbox is within image bounds
        x = max(0, min(x, img_w - 1))
        y = max(0, min(y, img_h - 1))
        w = min(w, img_w - x)
        h = min(h, img_h - y)

        severity = v.get("severity", "medium").lower()
        color = SEVERITY_COLORS.get(severity, (128, 128, 128))
        thickness = SEVERITY_THICKNESS.get(severity, 2)

        # Draw the bounding box
        cv2.rectangle(img, (x, y), (x + w, y + h), color, thickness)

        # Draw label background
        violation_type = v.get("violation_type", "violation")
        label = f"{violation_type.upper()} - {severity.upper()}"
        confidence = v.get("confidence", 0)
        if confidence > 0:
            label += f" ({confidence:.0%})"

        font = cv2.FONT_HERSHEY_SIMPLEX
        font_scale = 0.55
        label_thickness = 2
        (label_w, label_h), baseline = cv2.getTextSize(label, font, font_scale, label_thickness)

        # Label background rectangle
        label_y = max(y - 8, label_h + 8)
        cv2.rectangle(
            img,
            (x, label_y - label_h - 8),
            (x + label_w + 8, label_y + 4),
            color,
            cv2.FILLED,
        )

        # Label text (white on colored background)
        cv2.putText(
            img, label, (x + 4, label_y - 4),
            font, font_scale, (255, 255, 255), label_thickness,
        )

        # Draw corner accents for a more polished look
        corner_len = min(20, w // 4, h // 4)
        _draw_corner_accents(img, x, y, w, h, color, thickness + 1, corner_len)

    # Add summary bar at the bottom
    _draw_summary_bar(img, violations)

    # Save annotated image
    if output_path is None:
        stem = Path(image_path).stem
        ext = Path(image_path).suffix or ".jpg"
        output_path = str(Path(image_path).parent / f"{stem}_annotated{ext}")

    cv2.imwrite(output_path, img)
    return output_path


def _draw_corner_accents(img, x, y, w, h, color, thickness, length):
    """Draw corner accent lines for a more professional look."""
    # Top-left
    cv2.line(img, (x, y), (x + length, y), color, thickness)
    cv2.line(img, (x, y), (x, y + length), color, thickness)
    # Top-right
    cv2.line(img, (x + w, y), (x + w - length, y), color, thickness)
    cv2.line(img, (x + w, y), (x + w, y + length), color, thickness)
    # Bottom-left
    cv2.line(img, (x, y + h), (x + length, y + h), color, thickness)
    cv2.line(img, (x, y + h), (x, y + h - length), color, thickness)
    # Bottom-right
    cv2.line(img, (x + w, y + h), (x + w - length, y + h), color, thickness)
    cv2.line(img, (x + w, y + h), (x + w, y + h - length), color, thickness)


def _draw_summary_bar(img, violations):
    """Draw a summary status bar at the bottom of the image."""
    img_h, img_w = img.shape[:2]
    bar_height = 40

    # Count by severity
    counts = {"critical": 0, "high": 0, "medium": 0, "low": 0}
    for v in violations:
        sev = v.get("severity", "medium").lower()
        if sev in counts:
            counts[sev] += 1

    # Dark semi-transparent bar
    overlay = img.copy()
    cv2.rectangle(overlay, (0, img_h - bar_height), (img_w, img_h), (30, 30, 30), cv2.FILLED)
    cv2.addWeighted(overlay, 0.8, img, 0.2, 0, img)

    # Summary text
    text_parts = []
    if counts["critical"]:
        text_parts.append(f"CRITICAL: {counts['critical']}")
    if counts["high"]:
        text_parts.append(f"HIGH: {counts['high']}")
    if counts["medium"]:
        text_parts.append(f"MEDIUM: {counts['medium']}")
    if counts["low"]:
        text_parts.append(f"LOW: {counts['low']}")

    summary = "ConstructGuard AI  |  " + "  |  ".join(text_parts) if text_parts else "ConstructGuard AI  |  No violations detected"

    cv2.putText(
        img, summary,
        (10, img_h - 12),
        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1,
    )
