# Use Python 3.13 slim image
FROM python:3.13-slim

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

# Install AMD ROCm PyTorch (Note: The base image might need to be an ROCm base if issues arise, 
# but installing the wheel often works on standard Linux if devices are passed through)
RUN pip install torch torchvision --index-url https://download.pytorch.org/whl/rocm5.7
RUN pip install transformers accelerate Pillow

# Copy the backend code
COPY backend /app/backend

# Create output and upload directories
RUN mkdir -p /app/backend/uploads /app/backend/output/reports /app/backend/database

# Expose port
EXPOSE 8000

# Run FastAPI
CMD ["uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8000"]
