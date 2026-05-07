# Use ROCm base image instead — PyTorch already included
FROM rocm/pytorch:rocm6.2.4_ubuntu22.04_py3.11_pytorch_release_2.3.0

# Set working directory
WORKDIR /app

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONIOENCODING=utf-8 \
    INFERENCE_MODE=production

# Install system dependencies (required for OpenCV)
RUN apt-get update && apt-get install -y --no-install-recommends \
    libgl1 \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install
COPY backend/requirements.txt /app/backend/requirements.txt

# Install standard dependencies
RUN pip install --no-cache-dir -r backend/requirements.txt
RUN pip install transformers accelerate Pillow

# Copy the backend code
COPY backend /app/backend

# Create output and upload directories
RUN mkdir -p /app/backend/uploads /app/backend/output/reports /app/backend/database

# Expose port
EXPOSE 8000

# Run FastAPI
CMD ["uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8000"]
