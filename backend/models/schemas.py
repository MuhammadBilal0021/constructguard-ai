"""
ConstructGuard AI — Pydantic Schemas
Defines request/response models for the entire API contract.
"""

from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from enum import Enum


# ─── Enums ────────────────────────────────────────────────

class SeverityLevel(str, Enum):
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class EscalationLevel(str, Enum):
    NORMAL = "normal"
    ELEVATED = "elevated"
    HIGH = "high"
    EMERGENCY = "emergency"


class ViolationType(str, Enum):
    NO_HELMET = "no_helmet"
    NO_VEST = "no_vest"
    NO_HARNESS = "no_harness"
    NO_GLOVES = "no_gloves"
    NO_GOGGLES = "no_goggles"
    UNSAFE_POSITION = "unsafe_position"
    ZONE_VIOLATION = "zone_violation"
    OTHER = "other"


# ─── Core Models ──────────────────────────────────────────

class BoundingBox(BaseModel):
    """Bounding box coordinates for a detected object."""
    x: int = Field(..., description="Top-left X coordinate")
    y: int = Field(..., description="Top-left Y coordinate")
    w: int = Field(..., description="Width of bounding box")
    h: int = Field(..., description="Height of bounding box")


class Violation(BaseModel):
    """A single safety violation detected in the image."""
    violation_type: str = Field(..., description="Type of safety violation")
    severity: SeverityLevel = Field(..., description="Risk severity level")
    location: str = Field(default="Unknown", description="Location in image (Zone A/B/C)")
    reasoning: str = Field(default="", description="Natural language explanation of why this is dangerous")
    bbox: BoundingBox = Field(..., description="Bounding box coordinates")
    confidence: float = Field(default=0.0, ge=0.0, le=1.0, description="Detection confidence score")


class Alert(BaseModel):
    """A structured safety alert."""
    alert_id: str = Field(..., description="Unique alert identifier")
    violation: Violation = Field(..., description="The violation that triggered this alert")
    timestamp: str = Field(default_factory=lambda: datetime.now().isoformat())
    message: str = Field(..., description="Human-readable alert message")
    recommended_action: str = Field(default="", description="Recommended corrective action")


# ─── Request Models ──────────────────────────────────────

class AnalyzeRequest(BaseModel):
    """Request to analyze a construction site image."""
    site_id: str = Field(default="site_001", description="Construction site identifier")
    image_filename: Optional[str] = Field(default=None, description="Optional filename override")


# ─── Response Models ─────────────────────────────────────

class AnalysisResponse(BaseModel):
    """Full analysis response from the /analyze endpoint."""
    site_id: str
    timestamp: str = Field(default_factory=lambda: datetime.now().isoformat())
    total_workers_detected: int = Field(default=0)
    total_violations: int = Field(default=0)
    violations: list[Violation] = Field(default_factory=list)
    alerts: list[Alert] = Field(default_factory=list)
    escalation_level: str = Field(default="normal")
    escalation_message: str = Field(default="")
    risk_score: float = Field(default=0.0, ge=0.0, le=100.0)
    annotated_image_url: Optional[str] = Field(default=None)
    report_url: Optional[str] = Field(default=None)
    processing_time_ms: float = Field(default=0.0)


class HistoryRecord(BaseModel):
    """A single historical analysis record."""
    id: int
    site_id: str
    timestamp: str
    total_violations: int
    escalation_level: str
    risk_score: float


class HistoryResponse(BaseModel):
    """Response for site violation history."""
    site_id: str
    total_analyses: int
    records: list[HistoryRecord] = Field(default_factory=list)


class HealthResponse(BaseModel):
    """Health check response."""
    status: str = "healthy"
    inference_mode: str = "mock"
    gpu_available: bool = False
    model_loaded: bool = False
    version: str = "3.0.0"
