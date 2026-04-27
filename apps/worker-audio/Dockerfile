FROM python:3.11

WORKDIR /app

# Install system dependencies for audio processing
# Using Debian-based image for better compatibility
RUN apt-get update && apt-get install -y \
    build-essential \
    gcc \
    g++ \
    gfortran \
    git \
    postgresql-client \
    libsndfile1 \
    libsndfile1-dev \
    ffmpeg \
    libopenblas-dev \
    liblapack-dev \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt .

# Upgrade pip and install build tools
RUN pip install --upgrade pip setuptools wheel

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create cache directories
RUN mkdir -p /tmp/essentia_cache /tmp/demucs_cache /tmp/whisper_cache

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

# Expose port for Flower (optional)
EXPOSE 5555

# Run Celery worker
CMD ["celery", "-A", "celery_pipeline", "worker", "--loglevel=info"]
