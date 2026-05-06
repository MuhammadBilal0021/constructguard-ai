"""
ConstructGuard AI — Image Processor
Handles image loading, validation, resizing, and saving.
"""

import os
import uuid
from pathlib import Path
from PIL import Image

# Directories
UPLOAD_DIR = Path(__file__).parent.parent / "uploads"
OUTPUT_DIR = Path(__file__).parent.parent / "output"

# Ensure directories exist
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# Supported formats
SUPPORTED_FORMATS = {".jpg", ".jpeg", ".png", ".bmp", ".webp"}

# Max image dimension (resize if larger)
MAX_DIMENSION = 1920


def validate_image(filename: str) -> bool:
    """Check if file extension is a supported image format."""
    ext = Path(filename).suffix.lower()
    return ext in SUPPORTED_FORMATS


def save_upload(file_bytes: bytes, original_filename: str) -> str:
    """
    Save an uploaded file to the uploads directory.
    Returns the saved file path.
    """
    ext = Path(original_filename).suffix.lower()
    if ext not in SUPPORTED_FORMATS:
        raise ValueError(f"Unsupported image format: {ext}")

    # Generate unique filename
    unique_name = f"{uuid.uuid4().hex}{ext}"
    save_path = UPLOAD_DIR / unique_name

    with open(save_path, "wb") as f:
        f.write(file_bytes)

    return str(save_path)


def load_image(image_path: str) -> Image.Image:
    """Load and return a PIL Image from path."""
    if not os.path.exists(image_path):
        raise FileNotFoundError(f"Image not found: {image_path}")

    img = Image.open(image_path)
    img = img.convert("RGB")  # Ensure RGB mode
    return img


def resize_if_needed(image: Image.Image, max_dim: int = MAX_DIMENSION) -> Image.Image:
    """Resize image if any dimension exceeds max_dim, preserving aspect ratio."""
    w, h = image.size
    if max(w, h) <= max_dim:
        return image

    if w > h:
        new_w = max_dim
        new_h = int(h * (max_dim / w))
    else:
        new_h = max_dim
        new_w = int(w * (max_dim / h))

    return image.resize((new_w, new_h), Image.LANCZOS)


def get_output_path(original_path: str, suffix: str = "_annotated") -> str:
    """Generate output path for processed images."""
    name = Path(original_path).stem
    ext = Path(original_path).suffix or ".jpg"
    output_name = f"{name}{suffix}{ext}"
    return str(OUTPUT_DIR / output_name)


def get_image_dimensions(image_path: str) -> tuple[int, int]:
    """Get width and height of an image."""
    with Image.open(image_path) as img:
        return img.size
