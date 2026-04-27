FROM python:3.11-bullseye

WORKDIR /app

# Install system dependencies for audio processing
# Using Debian Bullseye for better compatibility with audio libraries
RUN apt-get update && apt-get install -y --no-install-recommends \
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
    libatlas-base-dev \
    libblas-dev \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# Copy requirements
COPY requirements.txt .

# Upgrade pip and install build tools
RUN pip install --upgrade pip setuptools wheel --no-cache-dir

# Install Python dependencies with longer timeout for large packages
RUN pip install --no-cache-dir \
    --default-timeout=1000 \
    --retries 5 \
    -r requirements.txt

# Copy application code
COPY . .

# Create cache directories
RUN mkdir -p /tmp/essentia_cache /tmp/demucs_cache /tmp/whisper_cache

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV NUMBA_CACHE_DIR=/tmp/numba_cache
ENV MKL_THREADING_LAYER=GNU

# Expose port for Flower (optional)
EXPOSE 5555

# Run Celery worker
CMD ["celery", "-A", "celery_pipeline", "worker", "--loglevel=info", "--concurrency=2"]
