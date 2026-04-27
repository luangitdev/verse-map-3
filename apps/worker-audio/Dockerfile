FROM python:3.11-bullseye

WORKDIR /app

# Install system dependencies for audio processing
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

# Copy install script
COPY install-deps.sh .
RUN chmod +x install-deps.sh

# Run install script
RUN ./install-deps.sh

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
