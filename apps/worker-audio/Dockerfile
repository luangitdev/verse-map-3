FROM python:3.11-slim

WORKDIR /app

# Install system dependencies for audio processing
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    postgresql-client \
    libsndfile1 \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create cache directory
RUN mkdir -p /tmp/essentia_cache

# Expose port for Flower (optional)
EXPOSE 5555

# Run Celery worker
CMD ["celery", "-A", "celery_pipeline", "worker", "--loglevel=info"]
